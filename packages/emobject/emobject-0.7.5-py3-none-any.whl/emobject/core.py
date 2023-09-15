import os
import glob

import pandas as pd
import numpy as np
import zarr
import yaml
from typing import Optional, Union
from numcodecs import Blosc, JSON
from logging import warning

from emobject.emobject import EMObject
from emobject.emimage import EMMask, EMImage
from emobject.emlayer import BaseLayer
from emobject.errors import EMObjectException
from emobject.utils import helpers
from emobject.version import __version__

from emoaccess.main import (
    run_base_object_queries,
    run_mask_queries,
    run_image_queries,
    run_segmentation_mask_queries,
    run_metadata_queries,
)


class EMObjectConfig:
    """Object that defines the config
    for an emObject that is interacting with the
    Enable database.

    Args:
        acquisition_id: required, the acquisition ID to query
        study_id: study id, placeholder
        segmentation_version: required, segmentation version
        biomarker_version: required, biomarker expression version
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
        img_path: optional, path to write zarr store to if img_to_disk==True.
        name: optional, a name for this emObject.
        datatype: optional, describe the datatype used here.
    """

    def __init__(
        self,
        acquisition_id: Optional[str] = None,
        study_id: Optional[int] = None,
        segmentation_version: Optional[int] = None,
        biomarker_version: Optional[int] = None,
        biomarkers: Optional[Union[list, np.ndarray, str]] = None,
        annotations: Optional[Union[list, np.ndarray, str]] = None,
        include_img: Optional[bool] = False,
        include_masks: Optional[bool] = False,
        include_seg_mask: Optional[bool] = False,
        include_metadata: Optional[bool] = True,
        seg_mask_type: Optional[str] = "nucleus",
        img_format: Optional[str] = "zarr",
        img_res: Optional[int] = 0,
        img_to_disk: Optional[bool] = False,
        img_path: Optional[str] = None,
        mask_names: Optional[Union[list, np.ndarray, str]] = None,
        name: Optional[str] = None,
        datatype: Optional[str] = None,
    ):
        self.acquisition_id = acquisition_id
        self.study_id = study_id
        self.segmentation_version = segmentation_version
        self.biomarker_version = biomarker_version
        self.biomarkers = biomarkers
        self.annotations = annotations
        self.include_img = include_img
        self.include_masks = include_masks
        self.include_seg_mask = include_seg_mask
        self.include_metadata = include_metadata
        self.seg_mask_type = seg_mask_type
        self.img_format = img_format
        self.img_res = img_res
        self.img_to_disk = img_to_disk
        self.img_path = img_path
        self.mask_names = mask_names
        self.name = name
        self.datatype = datatype
        self.masks = None
        self.img = None

        self._validate_config()

    def _validate_config(self):
        """Validates the arguments of
        an EMConfig to ensure user has provided
        logical args."""

        # acquisition ids
        assert type(self.acquisition_id) == str or type(self.acquisition_id) == np.str_

        # study is
        if self.study_id is not None:
            assert type(self.study_id) == int
            assert self.study_id > 0

        # seg version
        assert type(self.segmentation_version) == int
        assert self.segmentation_version > 0

        # biomarker_versions
        assert type(self.biomarker_version) == int
        assert self.biomarker_version > 0

        # check list formatting
        if self.biomarkers is not None:
            if type(self.biomarkers) == str:
                self.biomarkers = [self.biomarkers]

        if self.annotations is not None:
            if type(self.annotations) == str:
                self.annotations = [self.annotations]

        if self.include_masks and type(self.mask_names) == str:
            self.mask_names == [self.mask_names]

        if self.include_seg_mask:
            if self.seg_mask_type not in ["nucleus", "cell"]:
                raise EMObjectException(
                    f"Specified segmentation mask type {self.seg_mask_type} unknown."
                )

        # Avoid the issue where user specifies an image but forces an empty biomarker list
        if self.include_img and (
            self.biomarkers == [] or self.biomarkers == np.array([])
        ):
            warning(
                "include_img is True, but no channels/biomarkers. Setting include_img to False."
            )
            self.include_img = False


def add_layer_from_enable_db(
    E: EMObject = None, config: EMObjectConfig = None
) -> BaseLayer:
    """Builds a layer from the Enable database.

    Args:
        config: EMObjectConfig

    Returns:
        BaseLayer
    """

    bm_df, anno_df, coord_df = build_base_object_from_enable_db(
        acquisition_id=config.acquisition_id,
        biomarkers=config.biomarkers,
        annotations=config.annotations,
        segmentation_version=config.segmentation_version,
        biomarker_version=config.biomarker_version,
        config_mode=True,
    )

    if config.include_img:
        config.img = build_emimage_from_enable_db(
            acquisition_id=config.acquisition_id,
            study_id=config.study_id,
            channels=config.biomarkers,
            to_disk=config.img_to_disk,
            resolution=config.img_res,
        )
    segmentation = None

    if config.include_masks or config.include_seg_mask:
        if config.include_seg_mask:
            segmentation = "segmentation_mask"

        config.masks = build_emmask_from_enable_db(
            acquisition_id=config.acquisition_id,
            study_id=config.study_id,
            include_masks=config.include_masks,
            include_seg_masks=config.include_seg_mask,
            seg_mask_type=config.seg_mask_type,
            segmentation_version=config.segmentation_version,
            biomarker_version=config.biomarker_version,
        )
    if segmentation in E.mask.mask_names:
        segmentation = f"{segmentation}_1"

    # Need to add all the masks to the object's emmask
    if config.masks is not None:
        new_emmask = helpers.merge_emmasks(E.mask, config.masks)
        E.mask = new_emmask

    new_layer = BaseLayer(
        data=bm_df,
        obs=anno_df,
        var=None,
        pos=coord_df,
        name=config.acquisition_id,
        segmentation=segmentation,
    )

    E.add(new_layer)
    return E


def build_emobject(config: EMObjectConfig) -> EMObject:
    """Builds a complete EMObject from the Enable database.

    Args:
        config: EMObjectConfig

    Returns:
        EMObject
    """

    bm_df, anno_df, coord_df = build_base_object_from_enable_db(
        acquisition_id=config.acquisition_id,
        biomarkers=config.biomarkers,
        annotations=config.annotations,
        segmentation_version=config.segmentation_version,
        biomarker_version=config.biomarker_version,
        config_mode=True,
    )

    if config.include_img:
        config.img = build_emimage_from_enable_db(
            acquisition_id=config.acquisition_id,
            study_id=config.study_id,
            channels=config.biomarkers,
            to_disk=config.img_to_disk,
            resolution=config.img_res,
        )
    segmentation = None

    if config.include_masks or config.include_seg_mask:
        if config.include_seg_mask:
            segmentation = "segmentation_mask"

        config.masks = build_emmask_from_enable_db(
            acquisition_id=config.acquisition_id,
            study_id=config.study_id,
            include_masks=config.include_masks,
            include_seg_masks=config.include_seg_mask,
            seg_mask_type=config.seg_mask_type,
            segmentation_version=config.segmentation_version,
            biomarker_version=config.biomarker_version,
        )

    if config.include_metadata:
        meta = run_metadata_queries(config.acquisition_id)
    else:
        meta = None

    return EMObject(
        data=bm_df,
        obs=anno_df,
        var=None,
        pos=coord_df,
        mask=config.masks,
        img=config.img,
        meta=meta,
        name=config.acquisition_id,
        segmentation=segmentation,
    )


def build_base_object_from_enable_db(
    acquisition_id: Optional[str] = None,
    biomarkers: Optional[list] = None,
    annotations: Optional[list] = None,
    segmentation_version: int = None,
    biomarker_version: int = None,
    config_mode: Optional[bool] = False,
) -> EMObject:
    """Builds an EMObject from the Enable Database via Diglett.

    This is a separate function to allow for future open-sourcing

    Args:
        acquisition_id: acquistion ID for the region.
        biomarkers: A subset of biomarkers to include. If None, returns all.
        annotations: A subset of annotations to include.
    """

    bm_df, anno_df, coord_df = run_base_object_queries(
        acquisition_id=acquisition_id,
        biomarkers=biomarkers,
        annotations=annotations,
        segmentation_version=segmentation_version,
        biomarker_version=biomarker_version,
    )

    if config_mode:
        return bm_df, anno_df, coord_df

    else:
        return EMObject(
            data=bm_df,
            obs=anno_df,
            var=None,
            pos=coord_df,
            mask=None,
            img=None,
            meta=None,
            name=acquisition_id,
        )


def build_emmask_from_enable_db(
    acquisition_id: Optional[str] = None,
    study_id: Optional[int] = None,
    include_masks: Optional[bool] = None,
    include_seg_masks: Optional[bool] = None,
    seg_mask_type: Optional[str] = None,
    segmentation_version: Optional[int] = None,
    biomarker_version: Optional[int] = None,
):
    """Builds a EMMask object from the Enable database
    using the acquisition ID to obtain ROI masks.

    This needs to follow these steps:
        1. Obtain all story names for the study associated with this acq
        2. Subset the study's story names to the acquisition
        3. stack the masks into an object that can be passed to EMMask
    """

    # Need to get the data for each story this is going to be VERY slow
    acquisition_masks = []
    mask_names = []

    if include_masks:
        mask_dict = run_mask_queries(acquisition_id=acquisition_id)

        # TO DO: remove this logic in the future, didn't want to change to test new SQL
        for key in mask_dict.keys():
            acquisition_masks.append(mask_dict[key])
            mask_names.append(key)

    # Get the unique segment IDs (exclusive of cell segments)
    t = np.array(acquisition_masks)
    unique_seg_ids = np.sort(np.unique(t))
    del t

    if include_seg_masks:
        seg_mask = run_segmentation_mask_queries(
            acquisition_id=acquisition_id,
            study_id=study_id,
            seg_mask_type=seg_mask_type,
            segmentation_version=segmentation_version,
            biomarker_version=biomarker_version,
        )

        acquisition_masks.append(seg_mask)
        mask_names.append("segmentation_mask")
        max_cell_segment_id = np.max(seg_mask)

    # To avoid collisions, make new seg IDs for ROIs, sequentially following the
    # max cell ID.
    new_seg_ids = [max_cell_segment_id + i for i in range(1, len(unique_seg_ids) + 1)]
    assert len(unique_seg_ids) == len(new_seg_ids)

    # Now replace old IDs with the new one
    # TO DO: revisit to see if there's a quicker way here
    acquisition_masks = np.array(acquisition_masks)
    for j in range(
        1, len(new_seg_ids)
    ):  # we skip 0 because that's a special background value.
        old_id = unique_seg_ids[j]
        new_id = new_seg_ids[j]
        acquisition_masks[acquisition_masks == old_id] = new_id

    if not include_seg_masks:
        acquisition_masks = np.array(acquisition_masks)

    return EMMask(
        masks=np.stack(acquisition_masks, axis=0), mask_idx=np.array(mask_names)
    )


def build_emimage_from_enable_db(
    acquisition_id: Optional[str] = None,
    study_id: Optional[int] = None,
    channels: Optional[Union[list, np.ndarray]] = None,
    to_disk: Optional[bool] = False,
    resolution: Optional[int] = 0,
):
    """Builds an EMImage object from an acquisition_id.

    Args:
        acquisition_id (str): desired acquisition
        study_id (int): study, placeholder for future functionality
        channels (Union[list, np.ndarray]]): the channels to include, if None includes all.

    Returns:
        image (EMImage)
    """

    channel_images = run_image_queries(
        acquisition_id=acquisition_id, channels=channels, resolution=resolution
    )

    return EMImage(img=channel_images, channels=channels, to_disk=to_disk)


def save(
    E: EMObject = None, out_dir: Optional[str] = None, name: Optional[str] = None
) -> None:
    """Write an EMObject to disk.

    Args:
        E (EMObject): EMObject to write to disk
        out_dir (str): Path to write file. If None, writes to current directory.
        name (str): Name for the Zarr archive. If None, accesses E.name.

    Returns:
        None
    """

    # Check the outdir
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # Create an empty zarr store
    if name is None:
        name = f"{E.name}.zarr"
    else:
        name = f"{name}.zarr"

    zarr_path = os.path.join(out_dir, name)
    store = zarr.DirectoryStore(zarr_path, normalize_keys=True)
    zarr_root = zarr.group(store=store, overwrite=True)
    compressor = Blosc(cname="zstd", clevel=3, shuffle=2)

    # Establish the top level
    img = None
    mask = None
    core = zarr_root.create_group(name="core")

    # Build image group
    # Add a new dataset for each image.

    if E.img is not None:
        img = zarr_root.create_group(name="img")
        _ = img.create_dataset(
            name="CODEX", data=E.img.img, compressor=compressor
        )  # noqa
        _ = img.create_dataset(
            name="CODEX_ax",
            data=E.img.channels,
            compressor=compressor,
            dtype=object,
            object_codec=JSON(),
        )

    # Build mask group
    if E.mask is not None:
        mask = zarr_root.create_group(name="mask")
        if E.mask._style == "tensor":
            _ = mask.create_dataset(
                name="masktensor", data=E.mask.mask, compressor=compressor
            )
            _ = mask.create_dataset(name="maskix", data=E.mask.mask_names)
        else:
            _ = mask.create_dataset(
                name="maskix", data=E.mask.mask_names, dtype=object, object_codec=JSON()
            )
            _ = mask.create_dataset(
                name="maskdims", data=E.mask.dims, dtype=object, object_codec=JSON()
            )
            _ = mask.create_dataset(
                name="maskpos", data=np.array(list(E.mask.pos.values()))
            )
            for name in E.mask.mask.keys():
                _ = mask.create_dataset(
                    name=name, data=E.mask.mask[name], compressor=compressor
                )

    if E._meta is not None:
        _ = core.create_dataset(
            name="meta",
            data=E.meta.to_numpy(),
            compressor=compressor,
            dtype=object,
            object_codec=JSON(),
        )

    # Build core data group
    # add layers as hierarchy:
    for layer in E.layers:
        layer_group = core.create_group(layer)

        E.set_layer(layer)
        if E._layerdict[layer].data is not None:
            _ = layer_group.create_dataset(
                name="data",
                data=E._layerdict[layer].data,
                compressor=compressor,
                dtype=object,
                object_codec=JSON(),
            )

        if E._layerdict[layer]._obs is not None:
            _ = layer_group.create_dataset(
                name="obs",
                data=E._layerdict[layer]._obs.to_numpy(),
                compressor=compressor,
                dtype=object,
                object_codec=JSON(),
            )

            _ = layer_group.create_dataset(
                name="obs_y",
                data=E._layerdict[layer]._obs.columns.to_numpy(),
                compressor=compressor,
                dtype=object,
                object_codec=JSON(),
            )

        # Note, in version 0.6.0, all of this now is layer-specific.
        if E._layerdict[layer]._var is not None:
            _ = layer_group.create_dataset(
                name="var",
                data=E._layerdict[layer]._var.to_numpy(),
                compressor=compressor,
                dtype=object,
                object_codec=JSON(),
            )
            _ = layer_group.create_dataset(
                name="var_y",
                data=E._layerdict[layer]._var.columns.to_numpy(),
                compressor=compressor,
                dtype=object,
                object_codec=JSON(),
            )

        if E._layerdict[layer]._sobs is not None:
            _ = layer_group.create_dataset(
                name="sobs",
                data=E._layerdict[layer]._sobs.to_numpy(),
                compressor=compressor,
                dtype=object,
                object_codec=JSON(),
            )

            _ = layer_group.create_dataset(
                name="sobs_y",
                data=E._layerdict[layer]._sobs.columns.to_numpy(),
                compressor=compressor,
                dtype=object,
                object_codec=JSON(),
            )

        pos = layer_group.create_group("pos")
        _ = E.pos  # in case it wasn't ever made ou need to call this.

        for coord_sys in list(E._layerdict[layer]._pos.keys()):
            pos.create_dataset(
                name=coord_sys,
                data=E._layerdict[layer]._pos[coord_sys],
                compressor=compressor,
            )
            pos.create_dataset(
                name=f"{coord_sys}_y",
                data=np.array(E._layerdict[layer]._pos[coord_sys].columns),
                compressor=compressor,
                dtype=object,
                object_codec=JSON(),
            )

        # add the index information
        ix = layer_group.create_group("ix")
        ix.create_dataset(name="obsax", data=E._layerdict[layer]._obs_ax.to_numpy())
        ix.create_dataset(
            name="varax",
            data=E._layerdict[layer]._var_ax.to_numpy(),
            dtype=object,
            object_codec=JSON(),
        )

        if E._sobs_ax is not None:
            ix.create_dataset(
                name="sobsax", data=E._layerdict[layer]._obs_ax.to_numpy()
            )

    # write a file with overall object state
    # for each layer, write the assay, scalefactor, spot_size
    # for entire object, write the emobject version, and default layer

    state_dict = {"version": __version__, "defaultlayer": E._defaultlayer, "layers": {}}

    for layer in E.layers:
        state_dict["layers"][layer] = {
            "assay": E._layerdict[layer]._assay,
            "scale_factor": E._layerdict[layer]._scale_factor,
            "spot_size": E._layerdict[layer]._spot_size,
        }

    with open(os.path.join(zarr_path, "state.yml"), "w+") as f:
        yaml.dump(state_dict, f)


def load(path: str = None) -> EMObject:
    """Read an EMObject from disk

    Args:
        path (str): Path to EMObject Zarr store.

    Returns:
        EMObject
    """

    # Placeholders
    emimg_to_add = [None]
    mask = None

    # Check that the path is valid
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path {path} does not exist.")

    # Check if this is before/after version 0.6.0
    if not os.path.exists(os.path.join(path, "state.yml")):
        E = __load_deprecated(path)
        return E

    if os.path.exists(os.path.join(path, "core")):
        core_level_elements = ["seg", "meta", "pos"]
        obj_layers = glob.glob(os.path.join(path, "core", "*"))
        obj_layers = [s.split("/")[-1] for s in obj_layers]
        obj_layers = [s for s in obj_layers if s not in core_level_elements]

        # load the first layer
        layer_name = obj_layers[0]
        layer_path = os.path.join(path, "core", layer_name)
        layer = __load_layer(layer_path)

    # Load img
    img_group_path = os.path.join(path, "img")
    if os.path.exists(img_group_path):
        emimg_to_add = __load_img(img_group_path)

    # Load mask
    mask_group_path = os.path.join(path, "mask")
    if os.path.exists(mask_group_path):
        mask = __load_mask(mask_group_path)

    # Now it's time to build the EMObject

    # Load the meta attributes
    meta = None
    meta_path = os.path.join(path, "core", "meta")
    if os.path.exists(meta_path):
        meta = zarr.convenience.load(meta_path)
        if meta.shape[1] == 2:
            col_names = ["FEATURE_NAME", "FEATURE_VALUE"]
        else:
            col_names = None
        meta = pd.DataFrame(meta, columns=col_names)

    object_name = os.path.basename(path).split(".")[0]

    E = EMObject(
        data=None,
        obs=None,
        var=None,
        sobs=None,
        meta=meta,
        pos=None,
        mask=mask,
        img=emimg_to_add[0],
        first_layer_name=layer_name,
        name=object_name,
    )
    E.add(layer)

    # Load the rest of the layers
    for layer_name in obj_layers[1:]:
        layer_path = os.path.join(path, "core", layer_name)
        layer = __load_layer(layer_path)
        E.add(layer)

    # Load the state
    with open(os.path.join(path, "state.yml"), "r") as stream:
        state_dict = yaml.load(stream, Loader=yaml.SafeLoader)
        E._defaultlayer = state_dict["defaultlayer"].lower()
        for layer in E.layers:
            matching_key = __find_matching_key(state_dict["layers"], layer)
            E._layerdict[layer]._assay = state_dict["layers"][matching_key]["assay"]
            E._layerdict[layer]._scale_factor = state_dict["layers"][matching_key][
                "scale_factor"
            ]
            E._layerdict[layer]._spot_size = state_dict["layers"][matching_key][
                "spot_size"
            ]
    E.set_layer(E._defaultlayer)
    return E


def __find_matching_key(dictionary, key):
    for dict_key in dictionary:
        if dict_key.lower() == key.lower():
            return dict_key
    return None


def __load_pos(pos_path: str = None, obs_ix=None) -> dict:
    """Load the position dictionary from disk

    Args:
        path (str): Path to EMObject Zarr store.

    Returns:
        dict
    """
    if os.path.exists(pos_path):
        #  get position info
        coord_sys_to_add = glob.glob(os.path.join(pos_path, "*"))
        # coord_sys_to_add = [c.split('/')[-1].split('_')[0] for c in coord_sys_to_add]
        coord_sys_to_add = [c.split("/")[-1] for c in coord_sys_to_add]
        coord_sys_to_add = [c for c in coord_sys_to_add if not c.endswith("_y")]
        coord_sys_to_add = set(coord_sys_to_add)
        posdict = dict()
        for coord_sys in coord_sys_to_add:
            data = zarr.convenience.load(os.path.join(pos_path, coord_sys))
            cols = zarr.convenience.load(os.path.join(pos_path, f"{coord_sys}_y"))
            posdict[coord_sys] = pd.DataFrame(data=data, columns=cols, index=obs_ix)

        return posdict
    else:
        raise EMObjectException("No position data found.")


def __load_layer(layer_path: str = None) -> BaseLayer:
    """
    Helper function to load a layer from disk

    Args:
        layer_path (str): Path to layer group in the Zarr store.
    """

    # Load the data
    data_path = os.path.join(layer_path, "data")
    if os.path.exists(data_path):
        data = zarr.convenience.load(data_path)
    else:
        data = None

    # Load the var
    var_path = os.path.join(layer_path, "var")
    if os.path.exists(var_path):
        var = zarr.convenience.load(var_path)
    else:
        var = None

    var_y_path = os.path.join(layer_path, "var_y")
    if os.path.exists(var_y_path):
        var_y = zarr.convenience.load(var_y_path)
    else:
        var_y = None

    # Load the obs
    obs_path = os.path.join(layer_path, "obs")
    if os.path.exists(obs_path):
        obs = zarr.convenience.load(obs_path)
    else:
        obs = None

    obs_y_path = os.path.join(layer_path, "obs_y")
    if os.path.exists(obs_y_path):
        obs_y = zarr.convenience.load(obs_y_path)
    else:
        obs_y = None

    # Load the sobs
    sobs_path = os.path.join(layer_path, "sobs")
    if os.path.exists(sobs_path):
        sobs = zarr.convenience.load(sobs_path)
    else:
        sobs = None

    sobs_y_path = os.path.join(layer_path, "sobs_y")
    if os.path.exists(sobs_y_path):
        sobs_y = zarr.convenience.load(sobs_y_path)
    else:
        sobs_y = None

    # Load the ix
    obs_ax_path = os.path.join(layer_path, "ix", "obsax")
    if os.path.exists(obs_ax_path):
        obs_ax = zarr.convenience.load(obs_ax_path)
    else:
        obs_ax = None

    var_ax_path = os.path.join(layer_path, "ix", "varax")
    if os.path.exists(var_ax_path):
        var_ax = zarr.convenience.load(var_ax_path)
    else:
        var_ax = None

    sobs_ax_path = os.path.join(layer_path, "ix", "sobsax")
    if os.path.exists(sobs_ax_path):
        sobs_ax = zarr.convenience.load(sobs_ax_path)
    else:
        sobs_ax = None

    # Load the pos
    pos_path = os.path.join(layer_path, "pos")
    if os.path.exists(pos_path):
        pos = __load_pos(pos_path, obs_ax)
    else:
        pos = None

    # parse the layer name
    layer_name = layer_path.split("/")[-1]

    # Construct the data frames
    data = pd.DataFrame(data=data, columns=var_ax, index=obs_ax)

    if obs is not None:
        obs = pd.DataFrame(data=obs, columns=obs_y, index=obs_ax)
    if var is not None:
        var = pd.DataFrame(data=var, columns=var_y, index=var_ax)
    if sobs is not None:
        sobs = pd.DataFrame(data=sobs, columns=sobs_y, index=sobs_ax)

    return BaseLayer(data=data, var=var, obs=obs, sobs=sobs, pos=pos, name=layer_name)


def __load_img(path: str = None) -> list:
    """
    Helper function to load an image from disk

    Args:
        path (str): Path to image group in the Zarr store.
    """
    if os.path.exists(os.path.join(path)):
        # we have images to load
        imgs_to_load = glob.glob(os.path.join(path, "*"))
        imgs_to_load = [i.split("/")[-1].split("_")[0] for i in imgs_to_load]
        imgs_to_load = set(imgs_to_load)
        # this is written like this to future-proof for holding multiple image types.
        emimg_to_add = list()
        for img in imgs_to_load:
            if img == "codex":
                img_path = os.path.join(path, img)
                img_tensor = zarr.convenience.load(img_path)
                img_ix = zarr.convenience.load(os.path.join(path, f"{img}_ax"))
                emimg = EMImage(img=img_tensor, channels=img_ix, img_name=img)
            emimg_to_add.append(emimg)

        # Remove this assertion when multiple image types are supported.
        if not len(emimg_to_add) == 1:
            raise EMObjectException(
                "Attempted to add multiple images to single EMObject. This is not yet implemented."
            )

    else:
        emimg_to_add = [None]

    return emimg_to_add


def __load_mask(path: str = None) -> EMMask:
    """
    Helper function to load a mask from disk

    Args:
        path (str): Path to mask group in the Zarr store.
    """
    if os.path.exists(path):
        if os.path.exists(os.path.join(path, "masktensor")):
            mask = zarr.convenience.load(os.path.join(path, "masktensor"))
            labels = zarr.convenience.load(os.path.join(path, "maskix"))
            return EMMask(mask, mask_idx=labels)
        else:
            # Open a Zarr group
            group = zarr.open_group(path, mode="r")
            tree = zarr.tree(group)
            paths = tree.keys()
            mask = {}
            mask_idx = zarr.convenience.load(os.path.join(path, "maskix"))
            mask_pos = zarr.convenience.load(os.path.join(path, "mask_pos"))
            dims = zarr.convenience.load(os.path.join(path, "maskdims"))
            pos = {key: mask_pos[i] for i, key in enumerate(mask_idx)}
            for p in paths:
                mask[p] = zarr.convenience.load(os.path.join(path, p))

            return EMMask(mask, mask_idx=mask_idx, dims=dims, pos=pos, to_disk=True)
    else:
        return None


def __load_deprecated(path: str = None) -> EMObject:
    """Read an EMObject from disk

    Args:
        path (str): Path to EMObject Zarr store.

    Returns:
        EMObject
    """

    # Placeholders
    emimg_to_add = [None]
    mask = None
    sobs = None
    # pos = None
    sobs = None
    meta = None

    if os.path.exists(os.path.join(path, "ix")):
        obs_ix = zarr.convenience.load(os.path.join(path, "ix", "obsax"))
        var_ax = zarr.convenience.load(os.path.join(path, "ix", "varax"))
        if os.path.exists(os.path.join(path, "ix", "sobsax")):
            sobs_ax = zarr.convenience.load(os.path.join(path, "ix", "sobsax"))
        else:
            sobs_ax = None

    if os.path.exists(os.path.join(path, "core")):
        core_level_elements = ["seg", "meta", "pos"]
        obj_layers = glob.glob(os.path.join(path, "core", "*"))
        obj_layers = [s.split("/")[-1] for s in obj_layers]
        obj_layers = [s for s in obj_layers if s not in core_level_elements]

        if os.path.exists(os.path.join(path, "core", "meta")):
            meta = zarr.convenience.load(os.path.join(path, "core", "meta"))
        else:
            meta = None

        if os.path.exists(os.path.join(path, "core", "pos")):
            pos_path = os.path.join(path, "core", "pos")
            # get position info
            coord_sys_to_add = glob.glob(os.path.join(pos_path, "*"))
            coord_sys_to_add = np.array(
                [c.split("/")[-1].split("_")[0] for c in coord_sys_to_add]
            )
            coord_sys_to_add = np.unique(coord_sys_to_add)

            _posdict = dict()
            for coord_sys in coord_sys_to_add:
                data = zarr.convenience.load(os.path.join(pos_path, coord_sys))
                cols = zarr.convenience.load(os.path.join(pos_path, f"{coord_sys}_y"))
                _posdict[coord_sys] = pd.DataFrame(
                    data=data, columns=cols, index=obs_ix
                )

        if "raw" in obj_layers:
            layer_path = os.path.join(path, "core", "raw")
            data = zarr.convenience.load(os.path.join(layer_path, "data"))

            if os.path.exists(os.path.join(layer_path, "var")):
                var = zarr.convenience.load(os.path.join(layer_path, "var"))
            else:
                var = None
            if os.path.exists(os.path.join(layer_path, "var_y")):
                var_y = zarr.convenience.load(os.path.join(layer_path, "var_y"))
            else:
                var_y = None
            if os.path.exists(os.path.join(layer_path, "obs")):
                obs = zarr.convenience.load(os.path.join(layer_path, "obs"))
            else:
                obs = None
            if os.path.exists(os.path.join(layer_path, "obs_y")):
                obs_y = zarr.convenience.load(os.path.join(layer_path, "obs_y"))
            else:
                obs_y = None
            if os.path.exists(os.path.join(layer_path, "sobs")):
                sobs = zarr.convenience.load(os.path.join(layer_path, "sobs"))
            else:
                sobs = None
            if os.path.exists(os.path.join(layer_path, "sobs_y")):
                sobs_y = zarr.convenience.load(os.path.join(layer_path, "sobs_y"))
            else:
                sobs_y = None

    else:
        raise EMObjectException("Not a valid EMObject store.")

    # Now figure out masks
    if os.path.exists(os.path.join(path, "mask")):
        # we have masks to load
        mask = zarr.convenience.load(os.path.join(path, "mask", "masktensor"))
        labels = zarr.convenience.load(os.path.join(path, "mask", "maskix"))
        assert mask.shape[0] == labels.shape[0]
        mask = EMMask(mask, mask_idx=labels)

    if os.path.exists(os.path.join(path, "img")):
        # we have images to load
        imgs_to_load = glob.glob(os.path.join(path, "img", "*"))
        imgs_to_load = np.array([i.split("/")[-1].split("_")[0] for i in imgs_to_load])
        imgs_to_load = np.unique(imgs_to_load)

        # this is written like this to future-proof for holding multiple image types.
        emimg_to_add = list()
        for img in imgs_to_load:
            if img == "codex":
                img_path = os.path.join(path, "img", img)
                img_tensor = zarr.convenience.load(img_path)
                img_ix = zarr.convenience.load(os.path.join(path, "img", f"{img}_ax"))
                emimg = EMImage(img=img_tensor, channels=img_ix, img_name=img)
            emimg_to_add.append(emimg)

        # Remove this assertion when multiple image types are supported.
        if not len(emimg_to_add) == 1:
            raise EMObjectException(
                "Attempted to add multiple images to single EMObject. This is not yet implemented."
            )

    # Build the initial EMObject
    if obs is not None:
        obs = pd.DataFrame(data=obs, columns=obs_y, index=obs_ix)
    if var is not None:
        var = pd.DataFrame(data=var, columns=var_y, index=var_ax)
    if sobs is not None:
        sobs = pd.DataFrame(data=sobs, columns=sobs_y, index=sobs_ax)

    name = path.split("/")[-1].split(".")[0]
    E = EMObject(
        data=pd.DataFrame(data=data, columns=var_ax, index=obs_ix),
        obs=obs,
        var=var,
        pos=_posdict,
        sobs=sobs,
        mask=mask,
        img=emimg_to_add[0],  # this needs to change when multiple images are supported
        meta=meta,
        name=name,
        is_view=False,
    )
    #  E._pos = _posdict

    # Free memory
    del _posdict
    del emimg_to_add
    del mask
    del var
    del sobs
    del obs
    del data

    # Now need to add the rest of the layers.
    for layer in obj_layers:
        if layer != "raw":
            layer_path = os.path.join(path, "core", layer)
            data = zarr.convenience.load(os.path.join(layer_path, "data"))

            if os.path.exists(os.path.join(layer_path, "var")):
                var = zarr.convenience.load(os.path.join(layer_path, "var"))
            else:
                var = None
            if os.path.exists(os.path.join(layer_path, "var_y")):
                var_y = zarr.convenience.load(os.path.join(layer_path, "var_y"))
            else:
                var_y = None
            if os.path.exists(os.path.join(layer_path, "obs")):
                obs = zarr.convenience.load(os.path.join(layer_path, "obs"))
            else:
                obs = None
            if os.path.exists(os.path.join(layer_path, "obs_y")):
                obs_y = zarr.convenience.load(os.path.join(layer_path, "obs_y"))
            else:
                obs_y = None
            if os.path.exists(os.path.join(layer_path, "sobs")):
                sobs = zarr.convenience.load(os.path.join(layer_path, "sobs"))
            else:
                sobs = None
            if os.path.exists(os.path.join(layer_path, "sobs_y")):
                sobs_y = zarr.convenience.load(os.path.join(layer_path, "sobs_y"))
            else:
                sobs_y = None

            data = pd.DataFrame(data=data, columns=var_ax, index=obs_ix)

            if obs is not None:
                obs = pd.DataFrame(data=obs, columns=obs_y, index=obs_ix)
            if var is not None:
                var = pd.DataFrame(data=var, columns=var_y, index=var_ax)
            if sobs is not None:
                sobs = pd.DataFrame(data=sobs, columns=sobs_y, index=sobs_ax)

            E.add(BaseLayer(data=data, var=var, obs=obs, sobs=sobs, name=layer))
    return E
