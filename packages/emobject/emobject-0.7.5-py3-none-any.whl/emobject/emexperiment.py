from __future__ import annotations
from logging import warning
from typing import Optional, Union, List, Callable
from emobject.errors import EMExperimentException
import emoaccess.queries as queries
import emoaccess.emexp as emexp_helpers
import emobject.core as core
from emobject.core import EMObjectConfig, build_emobject, save, EMObject
from emobject.version import __version__
import numpy as np
import pandas as pd
import os
import glob


class EMExperimentConfig:
    """Object that defines the config
    for an emExperiment that is interacting with the
    Enable database.

    Args:
        acquisition_id: required, the acquisition ID to query
        study_id: study id, placeholder
        segmentation_versions: required, segmentation version
        biomarker_versions: required, biomarker expression version
        biomarkers: optional, a list or name of biomarkers
            to download. If None, gets all.
        annotations: optional, a list or name of annotations to download.
            If None, gets all.
        include_img: optional, if True, fetches the image with channels
            subsetted same as biomarkers.
        include_masks: optional, if True, fetches ROI masks.
        include_seg_masks: optional. If True, gets the segmentation mask.
        seg_mask_type: optional. Type of segmentation mask to fetch. Can be
            'nucleus' or 'cell'.
        img_format: img_format - placeholder
        img_res: optional, factor to downsample image by
        img_to_disk: optional, if True writes the zarr store to disk,
            otherwise object held in memory.
        root_dir: optional, path where experiment is built.
        name: optional, a name for this emObject.
        datatype: optional, describe the datatype used here.
    """

    def __init__(
        self,
        acquisition_ids: Optional[list] = None,
        study_id: Optional[int] = None,
        segmentation_versions: Optional[list] = None,
        biomarker_versions: Optional[list] = None,
        biomarkers: Optional[Union[list, np.ndarray, str]] = None,
        annotations: Optional[Union[list, np.ndarray, str]] = None,
        include_img: Optional[bool] = False,
        include_masks: Optional[bool] = False,
        include_seg_mask: Optional[bool] = False,
        seg_mask_type: Optional[str] = "nucleus",
        img_res: Optional[int] = 0,
        mask_names: Optional[Union[list, np.ndarray, str]] = None,
        name: Optional[str] = None,
        root_dir: Optional[str] = None,
        datatype: Optional[str] = None,
    ):
        # simple case, zarr directory is provided
        if root_dir is not None:
            zarrs = glob.glob(os.path.join(root_dir, ".zarr"))
            if len(zarrs) < 1:
                raise EMExperimentException(
                    "Provided root_dir does not contain any .zarr files"
                )

        # otherwise validate DB call
        else:
            if acquisition_ids is None and study_id is None:
                raise EMExperimentException(
                    "Must provide either acquisition_ids or study_id."
                )

            if segmentation_versions is not None and biomarker_versions is not None:
                if len(segmentation_versions) != len(biomarker_versions):
                    raise EMExperimentException(
                        "Must provide same number of segmentation and biomarker versions."
                    )

            if acquisition_ids is not None and study_id is not None:
                warning(
                    "Both acquisition_ids and study_id provided. \
                        Note: acquisition_ids overrides study_id"
                )

        self.acquisition_ids = acquisition_ids
        self.study_id = study_id
        self.segmentation_versions = segmentation_versions
        self.biomarker_versions = biomarker_versions
        self.biomarkers = biomarkers
        self.annotations = annotations
        self.include_img = include_img
        self.include_masks = include_masks
        self.include_seg_mask = include_seg_mask
        self.seg_mask_type = seg_mask_type
        self.img_res = img_res
        self.mask_names = mask_names
        self.name = name
        self.datatype = datatype
        self.masks = None
        self.img = None
        self.root_dir = root_dir

    def _validate_config_for_enable_db(self) -> None:
        # validation above. Skip the rest if zarr dir is provided
        # Later we will validate each zarr.
        if self.root_dir is not None:
            return

        if (
            self.segmentation_versions is not None
            and self.biomarker_versions is not None
        ):
            if len(self.segmentation_versions) != len(self.biomarker_versions):
                raise EMExperimentException(
                    "Must provide same number of segmentation and biomarker versions."
                )
            if len(self.segmentation_versions) != len(self.acquisition_ids):
                raise EMExperimentException(
                    "Must provide same number of segmentation versions and acquisition ids."
                )
            if len(self.biomarker_versions) != len(self.acquisition_ids):
                raise EMExperimentException(
                    "Must provide same number of biomarker versions and acquisition ids."
                )


class EMExperiment:
    """
    Holds the data for a single experiment, composed of multiple emObjects.

    This could be thought of as representing the study level, cohorts of studies,
    or acquistions, and is useful for cohort level comparisons.

    There are three ways to construct an EMExperiment object:
    1. Pass a list of emObjects
    2. Pass a directory containing emObject Zarr stores
    3. Pass a database configuration object, which will retrieve remote data
    """

    def __init__(
        self,
        experiment_name: Optional[str] = None,
        root_dir: Optional[str] = None,
        emobjects: Optional[list] = None,
        config: Optional[EMExperimentConfig] = None,
    ) -> EMExperiment:
        """
        Args:
            experiment_name: a name for the experiment (optional)
            root_dir: a directory containing emObject zarr stores.
            emobjects: a list of emObjects
            config: An EMExperiment config file
        """

        # It's ok to only pass a config object.

        self._groupnames = ["ungrouped"]  # list of groups
        self._groups = dict()
        self._groups["ungrouped"] = list()
        self._zarrpaths = dict()
        self._meta = None
        self.config = None
        self._acquisition_ids = list()
        self._segmentation_versions = list()
        self._biomarker_versions = list()
        self._study_id = None

        if config is None:
            if experiment_name is not None:
                self._experiment_name = experiment_name  # name of the experiment
            else:
                warning(
                    "No experiment name provided. Using default name 'emExperiment'."
                )
                self._experiment_name = "emExperiment"
            # dict of zarr paths
            if root_dir is None:
                self._rootdir = f"./{self._experiment_name}"
        else:
            self.config = config
            self._experiment_name = config.name
            self._acquisition_ids = config.acquisition_ids
            self._rootdir = config.root_dir
            self._groups["ungrouped"] = self._acquisition_ids
            self._biomarker_versions = config.biomarker_versions
            self._segmentation_versions = config.segmentation_versions
            self._study_id = config.study_id

    def __iter__(self):
        return self._groups.__iter__()  # make the iterator the dictionary's iterator.

    def __next__(self):
        return self._groups.__next__()

    @property
    def summary(self):
        """
        Returns a summary of the emExperiment
        """
        print(f"EMObject Version {__version__}")
        print(f"EMExperiment: {self._experiment_name}")
        print("Groups:")
        for group in self._groups.keys():
            if group == "ungrouped":
                # there's an exception that ungrouped is not a dict
                print(f"\t{group}: {len(self._groups[group])} emObjects")
                for ai in self._groups[group]:
                    print(f"\t\t{ai}")
            else:
                print(f"\t{group}: {len(self._groups[group])} subgroups")
                for subgroup in self._groups[group].keys():
                    print(
                        f"\t\t{subgroup}: {len(self._groups[group][subgroup])} emObjects"
                    )

    @property
    def group_names(self):
        """
        Returns a list of the groups that exist in the emExperiment.
        """
        if len(self._groupnames) == 0:
            self._groupnames.append("ungrouped")
        return self._groupnames

    @property
    def acquisitions(self):
        """
        Returns a list of the acquisitions that exist in the emExperiment.
        """
        self._acquisition_ids = list()

        for group in self._groups:
            if group == "ungrouped":
                for ai in self._groups[group]:
                    self._acquisition_ids.append(ai)

            else:
                for subgroup in self._groups[group].keys():
                    for ai in self._groups[group][subgroup]:
                        if ai not in self._acquisition_ids:
                            self._acquisition_ids.append(ai)

        return self._acquisition_ids

    def add_group(self, groupname: str, acquisition_ids: Optional[dict] = None) -> None:
        """
        Adds a top-level group to the emExperiment.

        Args:
            groupname: the name of the group to add. typically this is the metadata covariate.
            acquisition_ids: a dictionary of covariate feature value to acquisition ids to add to the group

        Returns:
            None
        """
        if groupname in self._groupnames:
            raise EMExperimentException(f"Group {groupname} already exists.")

        self._groupnames.append(groupname)
        if acquisition_ids is None:
            self._groups[groupname] = dict()
        else:
            self._groups[groupname] = acquisition_ids

            # remove the acquisition ids from the ungrouped group
            for subgroup in acquisition_ids.keys():
                for ai in acquisition_ids[subgroup]:
                    self._groups["ungrouped"].remove(ai)

    def remove_group(self, groupname: str) -> None:
        """
        Removes a group from the emExperiment.

        Args:
            groupname: the name of the group to remove

        Returns:
            None
        """
        if groupname not in self._groups.keys:
            raise EMExperimentException(f"Group {groupname} does not exist.")

        # move the acquisition ids back to the ungrouped group
        for subgroup in self._groups[groupname].keys():
            for ai in self._groups[groupname][subgroup]:
                self._groups["ungrouped"].append(ai)
        self._groupnames.remove(groupname)
        self._groups.pop(groupname)

    def add_subgroup(
        self, groupname: str, subgroupname: str, acquisition_ids: list
    ) -> None:
        """
        Adds a subgroup to a group in the emExperiment.

        Args:
            groupname: the name of the group to add the subgroup to
            subgroupname: the name of the subgroup to add
            acquisition_ids: a list of acquisition ids to add to the subgroup

        Returns:
            None
        """
        if groupname not in self._groups.keys():
            raise EMExperimentException(
                f"Group {groupname} does not exist. Use add_group to add a group."
            )

        if subgroupname in self._groups[groupname].keys():
            raise EMExperimentException(f"Subgroup {subgroupname} already exists.")

        self._groups[groupname][subgroupname] = acquisition_ids

        # remove the acquisition ids from the ungrouped group
        for ai in acquisition_ids:
            self._groups["ungrouped"].remove(ai)

    def remove_subgroup(self, groupname: str, subgroupname: str) -> None:
        """
        Removes a subgroup from a group in the emExperiment.

        Args:
            groupname: the name of the group to remove the subgroup from
            subgroupname: the name of the subgroup to remove

        Returns:
            None
        """
        if groupname not in self._groups.keys:
            raise EMExperimentException(f"Group {groupname} does not exist.")

        if subgroupname not in self._groups[groupname].keys():
            raise EMExperimentException(f"Subgroup {subgroupname} does not exist.")

        # move the acquisition ids back to the ungrouped group
        for ai in self._groups[groupname][subgroupname]:
            self._groups["ungrouped"].append(ai)
        self._groups[groupname].pop(subgroupname)

    def autogroup(self, covariate: str, acquisition_ids: Optional[list] = None) -> None:
        """
        Automatically groups acquisitions based on a covariate.

        Args:
            covariate: the covariate to group by
            acquisition_ids: a list of acquisition ids to group. If None, all acquisitions are grouped.

        Returns:
            None
        """
        _ = self.acquisitions

        if acquisition_ids is None:
            acquisition_ids = self.acquisitions

        if self._meta is None:
            _ = self.get_experiment_metadata()
            assert self._meta is not None

        possible_covariates = self._meta["FEATURE_NAME"].unique()
        possible_covariates = [
            cov.lower() for cov in possible_covariates if cov is not None
        ]

        if covariate.lower() not in possible_covariates:
            raise EMExperimentException(f"Covariate {covariate} does not exist.")

        # subset metdata to only the covariate of interest
        covariate_meta = self._meta[self._meta["FEATURE_NAME"] == covariate]

        # Now check that each acquisition id is in the metadata subset
        missing_ais = set(acquisition_ids) - set(
            covariate_meta["ACQUISITION_ID"].unique()
        )
        if len(missing_ais) > 0:
            raise EMExperimentException(
                f"Acquisition ids {missing_ais} do not have metadata covariate {covariate} assigned."
            )

        # Now get the unique values of the covariate
        covariate_values = [c.lower() for c in covariate_meta["FEATURE_VALUE"]]
        covariate_values = list(set(covariate_values))  # remove duplicates
        self.add_group(covariate)
        for value in covariate_values:
            # get the acquisition ids for this covariate value
            value_ais = (
                covariate_meta[covariate_meta["FEATURE_VALUE"].str.lower() == value][
                    "ACQUISITION_ID"
                ]
                .unique()
                .tolist()
            )
            self.add_subgroup(covariate, value, value_ais)

    def add_acquisition(
        self,
        acq_id: Union[str, list],
        groupname: Optional[str] = None,
        subgroup: Optional[str] = None,
    ) -> None:
        """
        Adds an acquisition to the emExperiment.

        Args:
            acq_id: the acquisition id to add. Multiple acquisition ids can be added at once by passing a list.
            groupname: the metadata-level group to add the acquisition to. If no group is specified, the acquisition is added to the 'ungrouped' group.
            subgroup: the subgroup (e.g. metadata feature) to add acquisition to.

        Returns:
            None
        """
        if type(acq_id) is str:
            acq_id = [acq_id]

        if groupname is None:
            for ai in acq_id:
                if ai not in self._groups["ungrouped"]:
                    self._groups["ungrouped"].append(ai)

        if groupname is not None and subgroup is None:
            raise EMExperimentException(
                "Must specify subgroup if groupname is specified."
            )

        if groupname not in self._groupnames:
            # group doesen't exist, so create it and ad all the acq_ids.
            warning(f"Group {groupname} does not exist. Creating a new group...")
            ai_dict = {subgroup: acq_id}
            self.add_group(groupname=groupname, acquisition_ids=ai_dict)

        else:
            # group exists, see if subgroup exists.
            if subgroup not in self._groups[groupname].keys():
                # subgroup doesen't exist, so create it and add all the acq_ids.
                warning(
                    f"Subgroup {subgroup} does not exist. Creating a new subgroup..."
                )
                self._groups[groupname][subgroup] = acq_id
            else:
                # subgroup exists, so add the acq_ids.
                for ai in acq_id:
                    if ai not in self._groups[groupname][subgroup]:
                        self._groups[groupname][subgroup].append(ai)
                    else:
                        warning(
                            f"Acquisition {acq_id} already exists in group {groupname}. Skipping..."
                        )

    def remove_acquisition(self, acq_id: Union[str, list]) -> None:
        """
        Removes an acquisition from the emExperiment.

        Args:
            acq_id: the acquisition id to remove. Multiple acquisition ids can be removed at once by passing a list.

        Returns:
            None
        """
        if type(acq_id) is str:
            acq_id = [acq_id]

        # what's the best way to do this?
        # iterate through the groups and remove the acquisition from each group?
        # TODO: revist this for a more efficient implementation.
        for group in self._groups.keys():
            for subgroup in self._groups[group].keys():
                for ai in acq_id:
                    if ai in self._groups[group][subgroup]:
                        self._groups[group][subgroup].remove(ai)

    def get_experiment_metadata(self) -> pd.DataFrame:
        """
        Assembles the metadata for each acquisition in the emExperiment.

        Args:
            None

        Returns:
            A pandas dataframe containing the metadata for each acquisition in the emExperiment.
        """
        if self._acquisition_ids is not None:
            if type(self._acquisition_ids) is str:
                self._acquisition_ids = [self._acquisition_ids]
            else:
                assert (
                    type(self._acquisition_ids) is list
                ), "acquisition_ids must be a list of acquisition ids"

            meta = queries.get_all_metadata_for_acquisition_id(self._acquisition_ids)
            self._meta = meta

        else:
            raise EMExperimentException("No acquisition ids provided.")

        return meta

    def build(
        self,
        local_mode: Optional[bool] = False,
        enable_internal_mode: Optional[bool] = False,
    ) -> None:
        """
        Builds the emExperiment as an on-disk Zarr store.

        Args:
            local_mode: if True, the emExperiment will be built in local mode, which requires emObjects Zarr
                stores to be present in the root directory of the emExperiment.
            enable_internal_mode: if True, the emExperiment will be built by populating emObjects from the
                internal database, which requires correct Enable credentials.

        Returns:
            None
        """
        if not local_mode and not enable_internal_mode:
            raise EMExperimentException(
                "Must specify either local_mode or enable_internal_mode."
            )

        if local_mode and enable_internal_mode:
            raise EMExperimentException(
                "Cannot specify both local_mode and enable_internal_mode."
            )

        # Perform checks to make sure the emExperiment is valid
        self._validate()

        # Create the root directory
        if not os.path.exists(self._rootdir):
            os.mkdir(self._rootdir)

        if local_mode:
            # in this case, emobjects are already present in the root directory
            if len(self._acquisition_ids) > 0:
                # check that these objects exist in the root directory
                # CHECK: Unclear where _acquisition_ids comes from
                for acq_id in self._acquisition_ids:
                    if not os.path.exists(
                        os.path.join(self._rootdir, f"{acq_id}.zarr")
                    ):
                        raise EMExperimentException(
                            f"Acquisition {acq_id} not found in root directory."
                        )
                    else:
                        self._zarrpaths[acq_id] = os.path.join(
                            self._rootdir, f"{acq_id}.zarr"
                        )

            # CHECK:  I think that this will be an empty list if nothing is provided in the config.
            # It should be able to generate acquisition IDs from .zarr path names, I think this is how.
            else:
                zarrs = glob.glob(os.path.join(self._rootdir, ".zarr"))
                # CHECK: Need this test in this class, as well as in the config class?
                if len(zarrs) < 1:
                    raise EMExperimentException(
                        "Provided zarr_dir does not contain any .zarr files"
                    )
                self._acquisition_ids = [
                    os.basename(zarrs).split(".", 1)[0] for zarr in zarrs
                ]

                for acq_id in self._acquisition_ids:
                    self._zarrpaths[acq_id] = os.path.join(
                        self._rootdir, f"{acq_id}.zarr"
                    )

        else:
            # in this case, we need to populate the emobjects from the internal database
            # To do this, we need to have the correct biomarker and segmentation versions
            # for each acquisition in the emExperiment.

            if self.config is None:
                raise EMExperimentException(
                    "Cannot build emExperiment without providing an EMExperimentConfig."
                )

            # get the biomarker and segmentation versions for each acquisition
            # this is all wrapped in the config class so we can use that to check the versions.
            if (
                (
                    self.config.biomarker_versions is None
                    or self.config.biomarker_versions is None
                )
                and self._biomarker_versions is None
                and self._segmentation_versions is None
            ):
                self.config._validate_config_for_enable_db()

            # for each acqusition in the experiment, construct an emobject.
            # In the future, this is going to need to be parallelized.

            # Check for study_id
            if self.config.study_id is not None and self.config.acquisition_ids is None:
                self.acquisition_ids = queries.get_all_acquisition_ids_for_study_id(
                    self.config.study_id
                )

            # First build all the emObjectConfigs
            emobject_configs = list()
            self.config.acquisition_ids = self._acquisition_ids
            for i in range(0, len(self._acquisition_ids)):
                emobject_configs.append(
                    EMObjectConfig(
                        acquisition_id=self.config.acquisition_ids[i],
                        study_id=None,
                        segmentation_version=self._segmentation_versions[i],
                        biomarker_version=self._biomarker_versions[i],
                        biomarkers=self.config.biomarkers,
                        annotations=self.config.annotations,
                        include_img=self.config.include_img,
                        include_masks=self.config.include_masks,
                        include_seg_mask=self.config.include_seg_mask,
                        seg_mask_type=self.config.seg_mask_type,
                        img_res=self.config.img_res,
                        name=self._acquisition_ids[i],
                    )
                )

            # Now build the emObjects
            for emo_config in emobject_configs:
                E = build_emobject(emo_config)
                save(E, out_dir=self._rootdir)

            # Add groups to the experiment
            # This should all now be handled within the add_group method, leaving this here for now.

            """for group_name in groups.keys():
                acquisitions_to_assign = groups[group_name]

                if type(acquisitions_to_assign) == str:
                    acquisitions_to_assign = [acquisitions_to_assign]

                for ai in acquisitions_to_assign:
                    if ai in self._groups['ungrouped']:
                        self._groups['ungrouped'].remove(ai)

                self.add_group(group_name, acquisitions_to_assign)"""

            # Build the dictionary of zarrs, this also essentially checks that everything was built correctly
            for (
                acq_id
            ) in (
                self.acquisitions
            ):  # for some reason self._acquisition_ids is empty here? seems wrong.
                if not os.path.exists(os.path.join(self._rootdir, f"{acq_id}.zarr")):
                    raise EMExperimentException(
                        f"Acquisition {acq_id} not found in root directory."
                    )
                else:
                    self._zarrpaths[acq_id] = os.path.join(
                        self._rootdir, f"{acq_id}.zarr"
                    )

    def _validate(self) -> None:
        """
        Validates the emExperiment.
        """

        # Make sure that there are groups
        if len(self._groupnames) == 0:
            raise EMExperimentException("No groups exist in the emExperiment.")

        for group in self._groupnames:
            if len(self._groups[group]) == 0:
                if group != "ungrouped":
                    raise EMExperimentException(f"Group {group} is empty.")

        if self._experiment_name is None:
            raise EMExperimentException("No experiment name provided.")

        if self._rootdir is None:
            self._rootdir = f"./{self._experiment_name}"

    def get_available_versions(self) -> pd.DataFrame:
        """
        Based on the acquisition_ids provided in the experiment, gets all of the usable versions of both
        biomarker expression and segmentation.
        """
        _ = self.acquisitions
        return emexp_helpers.get_available_versions(self._acquisition_ids)

    @property
    def segmentation_versions(self) -> List[str]:
        return self._segmentation_versions

    @segmentation_versions.setter
    def segmentation_versions(
        self, segmentation_versions: List[Union[int, str]]
    ) -> None:
        if len(segmentation_versions) != len(self._acquisition_ids):
            raise EMExperimentException(
                "Number of segmentation versions provided does not match number of acquisitions."
            )

        self._segmentation_versions = segmentation_versions

    @property
    def biomarker_versions(self) -> List[str]:
        return self._biomarker_versions

    @biomarker_versions.setter
    def biomarker_versions(self, biomarker_versions: List[Union[int, str]]) -> None:
        if len(biomarker_versions) != len(self._acquisition_ids):
            raise EMExperimentException(
                "Number of biomarker versions provided does not match number of acquisitions."
            )

        self._biomarker_versions = biomarker_versions

    def load_object(
        self, emo_names: Optional[Union[str, List[str]]] = None
    ) -> Union[EMObject, list[EMObject]]:
        """
        Loads the emObject(s) from the emExperiment into memory.

        Args:
            emo_names: The name(s) of the emObject(s) to load. If None, all emObjects are loaded.

        Returns:
            The emObject(s) loaded from the emExperiment. If emo_names is a list, a dictionary of emObjects is returned.
        """

        if emo_names is None:
            emo_names = self._acquisition_ids

        if len(emo_names) == 1:
            E = core.load(self._zarrpaths[emo_names[0]])

        else:
            E = dict()
            for emo_name in emo_names:
                E[emo_name] = core.load(self._zarrpaths[emo_name])

        return E

    def apply(
        self,
        emo_names: Optional[Union[str, List[str]]] = None,
        func: Callable = None,
        **kwargs,
    ) -> None:
        """
        Applies a function to the emObject(s) in the emExperiment.

        Args:
            emo_names: The name(s) of the emObject(s) to apply the function to. If None, the function is applied to all emObjects.
            func: The function to apply to the emObject(s).
            kwargs: Keyword arguments to pass to the function.

        Returns:
            modified emObject or None if func applies changes in place.
        """

        if emo_names is None:
            emo_names = self._acquisition_ids

        if len(emo_names) == 1:
            E = core.load(self._zarrpaths[emo_names[0]])
            E2 = func(E, **kwargs)
            yield E2

        else:
            for emo_name in emo_names:
                E = core.load(self._zarrpaths[emo_name])
                E2 = func(E, **kwargs)
                yield E2
