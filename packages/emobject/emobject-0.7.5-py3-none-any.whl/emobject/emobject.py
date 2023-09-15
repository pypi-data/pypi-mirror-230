# emObject
# A data abstraction for spatial omics.
from __future__ import annotations
from logging import warning
from typing import Optional, Union

import pandas as pd
from emobject.errors import EMObjectException
from emobject.emimage import EMImage, EMMask
from emobject.emlayer import LayeredData, BaseLayer
from emobject.utils import helpers
from emobject.version import __version__
import numpy as np
from scipy import sparse


class EMObject(LayeredData, BaseLayer):
    """
    An object that represents a single image capture (region).

    Args:
        data: data matrix (n_obs x n_var)
        obs: observation matrix (n_obs x annotations)
        var: variable matrix (n_var x annotations)
        pos: spatial coordinate matrix (n_obs x n_spatial_dimensions)
        sobs: segment observations (might remove)
        mask: ROI or single cell segmentation masks as array
        img: a multiplexed image
        meta: metadata about the entire region
        name: a name for the EMObject
        is_view: toggles whether to treat this as a view of another EMObject
        first_layer_name: the name of the first layer to be added, if None, uses object name.
    """

    def __init__(
        self,
        data: Optional[Union[np.ndarray, sparse.spmatrix, pd.DataFrame]] = None,
        obs: Optional[pd.DataFrame] = None,
        var: Optional[pd.DataFrame] = None,
        pos: Optional[Union[np.ndarray, pd.DataFrame]] = None,
        sobs: Optional[pd.DataFrame] = None,
        mask: Optional[Union[np.ndarray, EMMask]] = None,
        img: Optional[Union[np.ndarray, EMImage]] = None,
        meta: Optional[pd.DataFrame] = None,
        name: Optional[str] = None,
        assay: Optional[str] = None,
        scale_factor: Optional[float] = None,
        segmentation: Optional[str] = None,
        is_view: Optional[bool] = False,
        first_layer_name: Optional[str] = None,
    ) -> EMObject:
        super(EMObject, self).__init__()
        BaseLayer.__init__(self)

        if name is None:
            self._name = "default"
        else:
            self._name = name

        if first_layer_name is None:
            first_layer_name = self._name

        if data is not None:
            self.add(
                BaseLayer(
                    data=data,
                    obs=obs,
                    var=var,
                    name=first_layer_name,
                    segmentation=segmentation,
                    scale_factor=scale_factor,
                    pos=pos,
                    assay=assay,
                )
            )

            self._var_ax = self._layerdict[first_layer_name]._var_ax
            self._obs_ax = self._layerdict[first_layer_name]._obs_ax
        else:
            self._data = None
            self._var_ax = None
            self._obs_ax = None

        try:
            self._obs = self._layerdict[self._name].obs
            self._var = self._layerdict[self._name].var
        except KeyError:
            self._obs = None
            self._var = None

        self._activelayer = self._name
        self._defaultlayer = None
        self._sobs_ax = None
        self._meta = meta
        self._img = img
        self._mask = mask
        self._seg = None
        self._name = name
        self._defaultlayer = self._name

        # TO DO: Graphs and sobs
        self._sobs = None
        self.graph = None

    def __getitem__(self, key: str) -> BaseLayer:
        """
        Returns a layer from the EMObject.

        Args:
            key: the name of the layer to be returned.

        Returns:
            layer: the layer specified by key.
        """
        return self._layerdict[key]

    ##################################
    # ATTRIBUTE CONSTRUCTION
    ##################################

    def _build_meta(self, meta: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Store meta data
        """

        if meta is not None:
            if type(meta) == pd.DataFrame:
                return meta
            else:
                return None

    def _build_img(
        self,
        img: Optional[Union[np.ndarray, EMImage]] = None,
        _var_ax: Optional[Union[np.ndarray, pd.Index]] = None,
    ) -> EMImage:
        if type(img) == np.ndarray:
            img = EMImage(img, channels=_var_ax.to_numpy())
        return img

    def _build_mask(self, mask) -> Optional[EMMask]:
        if type(mask) == np.ndarray:
            return EMMask(masks=mask, mask_idx=None, to_disk=False)
        else:
            return mask

    def build_seg(self, coord_sys: Optional[str]):
        """
        Builds an assignement matrix of cells to segments using a specific coordinate system.

        Args:
            coord_sys: str
                The coordinate system to use for building the segmentation.
        Returns:
            seg: np.ndarray
                seg is a `n_obs` x `n_mask` array. Columns correspond to masks.
                Non-zero integer values assign cells to specific segments.
        """
        assert coord_sys in self._layerdict[self._activelayer]._pos.keys()
        self._layerdict[self._activelayer]._seg = self._build_seg(coord_sys=coord_sys)

    def _build_seg(self, coord_sys=None) -> np.ndarray:
        """
        Builds an assignement matrix of cells to segments.

        n_obs x n_mask tensor, encoded with IDs.

        Args:
            None

        Returns:
            seg: np.ndarray
                seg is a `n_obs` x `n_mask` array. Columns correspond to masks.
                Non-zero integer values assign cells to specific segments.
        """

        if self.mask is None:
            raise EMObjectException("Masks not provided, cannot generate seg.")
        elif self.pos is None:
            raise EMObjectException(
                "Spatial information not stored in pos, \
                cannot generate seg."
            )

        if coord_sys is None:
            # If there are multiple coordinate systems in the layer, warn the user, and use the original one.
            if len(self._layerdict[self._activelayer]._pos.keys()) > 1:
                warning(
                    f"Multiple spatial coordinates detected, using first coordinate set: \
                    {list(self._layerdict[self._activelayer]._pos.keys())[0]}. \
                    If build fails, try specifying a coordinate system with E.build_seg(coord_sys='X')."
                )
            orig_coord_key = list(self._layerdict[self._activelayer]._pos.keys())[0]
        else:
            orig_coord_key = coord_sys

        shape = (self.n_obs, self.mask.n_masks)
        seg = np.zeros(shape, dtype=np.uint16)
        n_seg = self.mask.n_seg

        mask_idx = 0
        for mask_name in n_seg.keys():
            mask = self.mask.mloc(mask_name)
            seg_ids = np.unique(mask)
            try:
                coords = (
                    self._layerdict[self._activelayer]._pos[orig_coord_key].to_numpy()
                )
            except AttributeError:
                if self._layerdict[self._activelayer] == "visium":
                    warning(
                        "Visium data detected, applying scalefactor to segment coordinates.\
                            Be sure the appropriate scalefactor is set (E.scalefactor = X)"
                    )

                    coords = (
                        self._layerdict[self._activelayer]
                        ._pos[orig_coord_key]
                        .to_numpy()
                        * self.scale_factor
                    )
                else:
                    coords = (
                        self._layerdict[self._activelayer]
                        ._pos[orig_coord_key]
                        .to_numpy()
                    )

            coords = coords.astype(int)

            for si in seg_ids:
                if si == 0:
                    continue
                val = mask[coords[:, 1], coords[:, 0]]  # are x and y reversed?
                (idx,) = np.where(val == si)
                seg[idx, mask_idx] = si
            mask_idx += 1
        return seg

    def _build_sobs(self) -> dict:
        """
        Builds the observation matrix for segments.

        Annotations are done on a maskwise basis. Therefore,
        this object is structured as a list of length `n_masks`
        where each entry is a `n_seg` x `n_annotation` matrix.
        """

        n_masks = self.mask.n_masks
        mask_names = self.mask.mask_names
        sobs = dict()

        for i in range(0, n_masks):
            sobs_ix = np.unique(self.seg[:, i])
            if sobs_ix[0] == 0:
                sobs_ix = sobs_ix[1:]
            mask_name = mask_names[i]
            sobs[mask_name] = pd.DataFrame(index=sobs_ix)

        return sobs

    ##################################
    # PROPERTIES
    ##################################

    # LAYER SPECIFIC ATTRIBUTES
    # Data
    @property
    def data(self) -> Optional[pd.DataFrame]:
        if len(self.ax) >= 1:
            return self._layerdict[self._activelayer].data
        else:
            return None

    @property
    def X(self) -> Optional[pd.DataFrame]:
        return self.data

    # var
    @property
    def n_var(self) -> int:
        return len(self._layerdict[self._activelayer]._var_ax)

    @property
    def var(self) -> pd.DataFrame:
        if self._var is not None:
            if self._layerdict[self._activelayer].var is None:
                self._layerdict[self._activelayer].var = self._var
        return self._layerdict[self._activelayer].var

    @var.setter
    def var(self, value: Optional[Union[np.array, pd.DataFrame]]) -> None:
        if value.shape[0] != self.var_ax.shape[0]:
            raise EMObjectException(
                "Must be a `n_var` length array of arbitrary\
                 width."
            )
        self._layerdict[self._activelayer].var = value
        if self._activelayer == "raw":
            self._var = value

    # obs
    @property
    def n_obs(self) -> int:
        return len(self._layerdict[self._activelayer]._obs_ax)

    @property
    def obs(self) -> pd.DataFrame:
        self._validate()
        if self._obs is not None:
            if self._layerdict[self._activelayer].obs is None:
                self._layerdict[self._activelayer].obs = self._obs
        return self._layerdict[self._activelayer].obs

    @obs.setter
    def obs(self, value: Optional[Union[np.array, pd.DataFrame]]) -> None:
        if value.shape[0] != self.obs_ax.shape[0]:
            raise EMObjectException(
                "Must be a `n_obs` length array of arbitrary\
                 width."
            )
        self._layerdict[self._activelayer].obs = value
        if self._activelayer == "raw":
            self._obs = value
        self._validate()

    # EMOBJECT ADDITIONAL ATTRIBUTES

    @property
    def pos(self) -> pd.DataFrame:
        return self._layerdict[self._activelayer]._pos

    @property
    def seg(self) -> Optional[list]:
        if self._layerdict[self._activelayer]._seg is None:
            self._layerdict[self._activelayer]._seg = self._build_seg()
        return self._layerdict[self._activelayer]._seg

    @property
    def meta(self) -> Optional[pd.DataFrame]:
        if self._meta is not None:
            self._meta = self._build_meta(self._meta)
        return self._meta

    @property
    def img(self) -> Optional[EMImage]:
        if self._img is not None:
            self._img = self._build_img(self._img, self._var_ax)
        return self._img

    @property
    def mask(self) -> Optional[EMMask]:
        if self._mask is not None:
            self._mask = self._build_mask(self._mask)
        return self._mask

    @property
    def sobs(self):
        if self._sobs is None:
            self._sobs = self._build_sobs()
            # Add to the BaseLayer
            self._layerdict[self._activelayer].sobs = self._sobs
        elif self._layerdict[self._activelayer].sobs is None:
            self._layerdict[self._activelayer].sobs = self._sobs
        return self._sobs

    # EMOBJECT-WIDE PROPERTIES

    # Generic/Informational Properties
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value) -> None:
        if type(value) is not str:
            raise EMObjectException("New EMObject name must be of type str.")
        self._name = value

    @property
    def n_seg(self) -> int:
        if self.mask is not None:
            return self.mask.n_seg
        else:
            return 0

    @property
    def is_view(self) -> bool:
        return self._is_view

    @is_view.setter
    def is_view(self, value) -> None:
        pass  # should be immutable I think

    @property
    def layers(self) -> list:
        return self.ax

    @property
    def summary(self) -> None:
        print(f"EMObject Version {__version__}")
        print(f"EMObject: {self.name}")
        print(f"Layers: {len(self.ax)}")

        for layer in self.layers:
            print(f"\t Layer: {layer}")
            print(f"\t\t Layer segmentation: {self._layerdict[layer]._segmentation}")
            print(f"\t\t Assay: {self._layerdict[layer]._assay}")

            print(f"\t\t n_obs: {len(self._layerdict[layer]._obs_ax)}")
            print(f"\t\t n_var: {len(self._layerdict[layer]._var_ax)}")
            """if len(self.mask.n_seg) > 0:
                print(f"\t\t n_seg: {self.n_seg}")
"""
        if self._mask is not None:
            print(f"masks: {self.mask.n_masks}")

        if self._seg is not None:
            print("Segment Summary:")
            print("Mask \t Segments")
            for i in self.mask.n_seg.keys():
                print(f"{i} \t {self.mask.n_seg[i]}")

    @property
    def version(self) -> float:
        print(f"EMObject Version {__version__}")
        return __version__

    @property
    def layer(self) -> str:
        return self._activelayer

    @layer.setter
    def layer(self, value) -> None:
        assert value in self.layers or value is None
        if value is None:
            self._activelayer = self._defaultlayer
        else:
            self._activelayer = value

    # Axes

    # TO DO: Should there be setters for changing axis? if so, how can the
    # dataframes be kept in alignment/share axes?
    @property
    def var_ax(self) -> pd.Index:
        # return self._var_ax
        return self._layerdict[self._activelayer]._var_ax

    @property
    def obs_ax(self) -> pd.Index:
        # return self._obs_ax
        return self._layerdict[self._activelayer]._obs_ax

    @property
    def scale_factor(self) -> float:
        return self._layerdict[self._activelayer].scale_factor

    @scale_factor.setter
    def scale_factor(self, value: float) -> None:
        self._layerdict[self._activelayer].scale_factor

    @property
    def assay(self) -> str:
        return self._layerdict[self._activelayer].assay

    @assay.setter
    def assay(self, value: str) -> None:
        self._layerdict[self._activelayer].assay = value.lower()

    @property
    def default_layer(self) -> str:
        return self._defaultlayer

    @default_layer.setter
    def default_layer(self, value: str) -> None:
        if value not in self.layers:
            raise EMObjectException(f"Layer {value} does not exist.")
        self._default_layer = value

    ##################################
    # METHODS
    ##################################

    def add_anno(
        self,
        attr: Optional[str] = None,
        value: Optional[Union[np.array, pd.DataFrame, list]] = None,
        name: Optional[Union[np.array, list, str]] = None,
        layer: Optional[str] = None,
        mask: Optional[Union[int, str]] = None,
    ) -> None:
        """
        Adds a new annotation to an attribute (var, obs, sobs).

        Args:
            attr: the attribute to add annotation to. One of
                   'sobs', 'var', 'obs'.
            value: the annotation. Must be array-like of same
                      size as axis.
            name: annotation name
            layer:   the layer to slice within. If None, uses the active layer.
            mask:   the mask to which segment observations are applied.
                Required if attr='sobs'.

        Returns:
            None
        """
        self._validate()

        # Set the layer
        if layer is None:
            layer = self._activelayer
        else:
            assert layer in self.ax

        # Some checks on inputs
        if type(value) == list:
            value = np.array(value)
        if len(value.shape) == 1:
            value = value.reshape(value.shape[0], 1)

        # Deal with annotation names.
        if name is not None:
            # Standardize as ndarray
            if type(name) == str or type(name) == list:
                name = np.array(name).reshape(-1)
            n_names_reqd = value.shape[1]  # n_obs/n_var/n_seg x n_newAnnos

            if name.shape[0] < n_names_reqd:
                # Handle case where too few names are provided
                warning(
                    f"Expected {n_names_reqd} names but received \
                    {name.shape[0]} names. Generating dummy annotation names."
                )
                n_new_names = n_names_reqd - name.shape[0]
                new_names = np.array([f"anno_{i}" for i in range(0, n_new_names)])
                name = np.concatenate([name, new_names])
        else:
            if type(value) != pd.DataFrame:
                #  No names provided, handle this.
                warning(
                    "No annotation names received. Generating dummy annotation\
                    names."
                )
                n_new_names = value.shape[1]
                name = np.array([f"anno_{i}" for i in range(0, n_new_names)])
                assert name.shape[0] == value.shape[1]

        if type(value) == pd.DataFrame:
            name = value.columns

        if attr == "var":
            # add attribute on var.
            # check annotation matches specified attribute
            assert value.shape[0] == self._layerdict[layer]._var_ax.shape[0]

            # Check that new annotation names are unique
            existing_annos = list(self._layerdict[layer].var.index)
            for n in name:
                if n in existing_annos:
                    raise EMObjectException(
                        f"The annotation name {n} already \
                        exists in the {attr} attribute. Please provide a unique \
                        name for the new annotation."
                    )

            if type(value) == np.ndarray:
                _appenddf = pd.DataFrame(
                    data=value, columns=name, index=self._layerdict[layer]._var_ax
                )
            elif type(value) == pd.DataFrame:
                _appenddf = value
                if name is not None:
                    _appenddf.columns = name
                if not _appenddf.index.equals(self._var_ax):
                    warning(
                        "Provided dataframe index does not match the var axis. Attempting to join on index."
                    )

            if (
                self._layerdict[layer]._var is None
                or self._layerdict[layer]._var.shape[1] == 0
            ):
                self._layerdict[layer]._var = _appenddf
            else:
                # left join on index
                self._layerdict[layer]._var = self._layerdict[layer]._var.join(
                    _appenddf, how="left"
                )
                """self._layerdict[layer]._var = pd.concat([self._layerdict[layer]._var, # noqa
                                                         _appenddf],
                                                        axis=1)"""
        elif attr == "obs":
            # add an attribute on obs
            # check annotation matches specified attribute
            assert value.shape[0] == self._layerdict[layer]._obs_ax.shape[0]

            # Check that new annotation names are unique
            existing_annos = self._layerdict[layer]._obs.columns
            for n in name:
                if n in existing_annos:
                    raise EMObjectException(
                        f"The annotation name {n} already \
                        exists in the {attr} attribute. Please provide a unique \
                        name for the new annotation."
                    )

            if type(value) == np.ndarray:
                _appenddf = pd.DataFrame(
                    data=value, columns=name, index=self._layerdict[layer]._obs_ax
                )
            elif type(value) == pd.DataFrame:
                _appenddf = value
                if name is not None:
                    _appenddf.columns = name
                if not _appenddf.index.equals(self._layerdict[layer]._obs_ax):
                    warning(
                        "Index of new annotation does not match obs index. Attempting to join on index value."
                    )

            if (
                self._layerdict[layer]._obs is None
                or self._layerdict[layer]._obs.shape[1] == 0
            ):
                self._layerdict[layer]._obs = _appenddf
            else:
                # join the new annotation horizontally on the index
                self._layerdict[layer]._obs = self._layerdict[layer]._obs.join(
                    _appenddf, how="left"
                )  # noqa
                """self._layerdict[layer]._obs = pd.concat([self._layerdict[layer]._obs, # noqa
                                                         _appenddf],
                                                        axis=1)"""

        elif attr == "sobs":
            # add an attribute on sobs
            if mask is None:
                raise EMObjectException("Mask to annotate is unspecified.")

            # Check that new annotation names are unique
            _ = self.sobs  # build sobs if not already built
            existing_annos = self._layerdict[layer]._sobs[mask].columns
            for n in name:
                if n in existing_annos:
                    raise EMObjectException(
                        f"The annotation name {n} already \
                        exists in the {attr} attribute. Please provide a unique \
                        name for the new annotation."
                    )

            # check that segment is valid.
            if type(mask) == str:
                if mask not in self.mask.mask_names:
                    raise EMObjectException(
                        f"Mask name {mask} is not in the current\
                     object."
                    )
            else:
                raise EMObjectException(
                    f"Mask must be a string. Received {type(mask)}."
                )

            # Get index for sobs
            anno_idx = self.sobs[mask].index  # hopefully calls build_sobs?
            if value.shape[0] != anno_idx.shape[0]:
                if anno_idx.shape[0] - value.shape[0] == 1:
                    # Handle case where one segment is missing
                    raise EMObjectException(
                        "Received one fewer segment annotations than expected.\
                         This is likely due to a missing background segment annotation (seg_id = 0). Try prepending a np.nan dummy."
                    )
                    """new_val = [np.nan]
                    for v in value:
                        new_val.append(v)
                    value = np.array(new_val)
                    assert value.shape[0] == anno_idx.shape[0]"""
                else:
                    raise EMObjectException(
                        f"Annotation length does not match the\
                        number of segments in the mask. Expected {anno_idx.shape[0]}\
                        but received {value.shape[0]}."
                    )

            if type(value) == np.ndarray:
                _appenddf = pd.DataFrame(data=value, columns=name, index=anno_idx)
            elif type(value) == pd.DataFrame:
                _appenddf = value
                if name is not None:
                    _appenddf.columns = name
                _appenddf.index = self._sobs_ax

            if (
                self._layerdict[layer]._obs is None
                or self._layerdict[layer]._obs.shape[1] == 0
            ):
                self._layerdict[layer]._sobs[mask] = _appenddf
            else:
                self._layerdict[layer]._sobs[mask] = pd.concat(
                    [self._layerdict[layer]._sobs[mask], _appenddf], axis=1  # noqa
                )
        else:
            raise EMObjectException(
                f"Unrecognized attribute to annotate. Must be one\
                 of 'sobs', 'var', 'obs', but received {attr}."
            )

        self._validate()

    def del_anno(
        self,
        attr: Optional[str] = None,
        name: Optional[str] = None,
        layer: Optional[str] = None,
        mask: Optional[Union[str, int]] = None,
    ) -> None:
        """Delete an annotation from an annotation matrix.

        Args:
            attr: the attribute to add annotation to. One of
                   'sobs', 'var', 'obs'.
            name: annotation name
            layer:   the layer to slice within. If None, uses the active layer.
            mask:   the mask to which segment observations are applied.
                Required if attr='sobs'.

        Returns:
            None
        """
        self._validate()

        if layer is None:
            layer = self._activelayer

        if attr is not None:
            if attr == "obs":
                assert name in self._layerdict[layer]._obs.columns
                self._layerdict[layer]._obs.drop(columns=name, axis=0, inplace=True)
            elif attr == "var":
                assert name in self._layerdict[layer]._var.columns
                self._layerdict[layer]._var.drop(columns=name, axis=0, inplace=True)
            elif attr == "sobs":
                # check that segment is valid.
                assert mask is not None

                # Validity checks on masks, get correct mask.
                if type(mask) == str:
                    if mask not in self.mask.mask_names:
                        raise EMObjectException(
                            f"Mask name {mask} is not in the\
                             current object."
                        )
                    else:
                        (ix,) = np.where(self.mask.mask_names == mask)
                        mask = ix[0]

                elif type(mask) == int:
                    if mask >= len(self.mask.mask_names) or mask < 0:
                        raise EMObjectException(
                            f"Mask index {mask} is \
                            out of range for the current object."
                        )

                assert name in self._layerdict[layer]._sobs[mask].columns

                # delete the annotation
                self._layerdict[layer]._sobs[mask].drop(
                    columns=name, axis=0, inplace=True
                )
        self._validate()

    def loc(
        self,
        obs_subset: Optional[Union[np.ndarray, list]] = None,
        var_subset: Optional[Union[np.ndarray, list]] = None,
        seg_subset: Optional[Union[np.ndarray, list, int]] = None,
        mask: Optional[str] = None,
        layer: Optional[str] = None,
    ) -> EMObject:
        """
        Allows for slicing of EMObjects to subsets of interest.

        Args:
            obs_subset: subset of observations to include.
                Elements must belong to obs_ax
            var_subset: subset of variables to include.
                Elements must belong to var_ax
            seg_subset: subset of segments to include.
                Elements must belong to sobs_ax
            mask:
            layer:  the layer to slice within.
                If None, uses the active layer.
        Returns:
            Subsetted EMObject view
        """
        self._validate()

        if layer is None:
            layer = self._activelayer
        else:
            assert layer in self.ax

        if obs_subset is None:
            obs_subset = self._layerdict[layer]._obs_ax
        if var_subset is None:
            var_subset = self._layerdict[layer]._var_ax
        if type(obs_subset) == list:
            obs_subset = np.array(obs_subset)
        if type(var_subset) == list:
            var_subset = np.array(var_subset)

        if seg_subset is not None:
            assert seg_subset in np.unique(self.seg)
            all_r = set()
            if type(seg_subset) == int:
                seg_subset = [seg_subset]
            for si in seg_subset:
                rr, cc = np.where(self._layerdict[layer]._seg == si)
                all_r.update(rr)
            obs_subset = np.array(list(all_r))
            obs_subset = self._layerdict[layer]._obs_ax[obs_subset]

        if mask is not None:
            if self._layerdict[layer]._seg is None:
                _ = self.seg
            assert mask in self.mask.mask_names
            (ix,) = np.where(self.mask.mask_names == mask)
            obs_subset, _ = np.where(self._layerdict[layer]._seg[:, ix] != 0)
            obs_subset = self._layerdict[layer]._obs_ax[obs_subset]

        pos_dict = {}
        for coord_sys in self._layerdict[layer]._pos.keys():
            pos_dict[coord_sys] = (
                self._layerdict[layer]._pos[coord_sys].loc[obs_subset, :]
            )

        # a view will return an in-memory EMObject that has been subsetted
        return EMObject(
            data=self._layerdict[layer].data.loc[obs_subset, var_subset],
            obs=self._layerdict[layer].obs.loc[obs_subset, :],
            var=self._layerdict[layer].var.loc[var_subset, :],
            pos=pos_dict,
            mask=self.mask,
            img=self.img,
            name=f"ViewOf{self.name}-{layer}",
            is_view=True,
        )

    def slice(
        self,
        obs_subset: Optional[Union[np.ndarray, list]] = None,
        seg_subset: Optional[Union[np.ndarray, list, int]] = None,
        anchor_layer: Optional[str] = None,
        layers: Optional[Union[str, list, np.ndarray]] = None,
    ) -> EMObject:
        """
        Slices through all emObject layers on the basis of observations, variables, or masks
        and returns a new EMObject with the subsetted data.

        Args:
            obs_subset: subset of observations to include.
                Elements must belong to obs_ax
            seg_subset: subset of segments to include.
                Elements must belong to sobs_ax
            layers: the layers to slice within. If None, uses all.
        """
        self._validate()

        if layers is None:
            raise EMObjectException("Must specify layers to slice.")
        elif type(layers) == str:
            layers = [layers]
        if type(layers) == list:
            layers = np.array(layers)

        if anchor_layer is not None:
            assert anchor_layer in self.layers
        else:
            anchor_layer = self._activelayer

        """
        if anchor_coord_sys is not None:
            assert anchor_coord_sys in E._layerdict[anchor_layer].pos.keys()
        else:
            warning(f"Coordinate system {anchor_coord_sys} not found in layer {anchor_layer}. Using {list(self._layerdict[anchor_layer].pos.keys())[0]}.")
            anchor_coord_sys = list(E._layerdict[anchor_layer].pos.keys())[0]
        """

        # Check that each layer has an assigned segmentation
        for layer in layers:
            # requires finding a spot to store spot_size
            if (
                self._layerdict[layer].segmentation is None
                and self._layerdict[layer]._assay == "visium"
            ):
                try:
                    test_key = list(self._layerdict[layer].obs.keys())[0]
                    visium_mask = helpers.build_visium_segmentation_mask(
                        spot_coords=self._layerdict[layer].pos[test_key],
                        spot_size=self._layerdict[layer]._spot_size,
                        scale_factor=self._layerdict[layer]._scale_factor,
                        shape=self.mask.dim,
                    )

                    self.mask.add_mask(visium_mask, name="visium_segmentation")
                    self._layerdict[layer].segmentation = "visium_segmentation"
                except Exception:
                    raise EMObjectException(
                        "Could not build segmentation mask for Visium data. Be sure to specify a spot_size in the metadata.\
                                            Alternatively, you can manually build a segmentation mask using utils.helpers.build_visium_segmetnation_mask\
                                            and assign it to the layer."
                    )

            assert self._layerdict[layer].segmentation is not None
            # Also check that the data layers have positions
            assert self._layerdict[layer].pos is not None
            test_key = list(self._layerdict[layer].pos.keys())[0]
            assert len(self._layerdict[layer].data) == len(
                self._layerdict[layer].pos[test_key]
            )

        # Based on the current layer's segmentation, slice the data
        # on the basis of the segmentation mask from the other layers.
        # Then, subset to any additional observations specified.
        # First, construct a new EMObject with the data from the current layer
        if obs_subset is None:
            obs_subset = self._layerdict[self._activelayer].data.index

        pos_dict = {}
        for coord_sys in self._layerdict[anchor_layer]._pos.keys():
            pos_dict[coord_sys] = (
                self._layerdict[anchor_layer]._pos[coord_sys].loc[obs_subset, :]
            )

        E = EMObject(
            data=self._layerdict[anchor_layer].data.loc[obs_subset, :],
            obs=self._layerdict[anchor_layer].obs.loc[obs_subset, :],
            var=self._layerdict[anchor_layer].var,
            pos=pos_dict,
            mask=self.mask,
            img=self.img,
            name=f"sliced_{self.name}",
            first_layer_name=anchor_layer,
            segmentation=self._layerdict[anchor_layer].segmentation,
        )

        # Make binary anchor mask
        try:
            sparse_anchor_mask = sparse.coo_matrix(
                self.mask.mloc(self._layerdict[anchor_layer].segmentation)
            )
        except TypeError:
            sparse_anchor_mask = sparse.coo_matrix(
                self.mask.mloc(self._layerdict[anchor_layer].segmentation).squeeze()
            )
        (obs_subset_anchor_mask_ix,) = np.where(
            np.isin(sparse_anchor_mask.data, obs_subset)
        )  # this is the "binarized array"
        obs_subset_anchor_mask_ix_rr = sparse_anchor_mask.row[obs_subset_anchor_mask_ix]
        obs_subset_anchor_mask_ix_cc = sparse_anchor_mask.col[obs_subset_anchor_mask_ix]

        for layer in layers:
            if layer != anchor_layer:
                assert self.mask.mloc(self._layerdict[layer].segmentation) is not None
                layer_segmentation = self.mask.mloc(self._layerdict[layer].segmentation)
                # Now subset the layer segmentatino using the root segmentation
                if len(layer_segmentation.shape) == 3:
                    layer_segmentation = layer_segmentation.squeeze()
                subset_ids = np.unique(
                    layer_segmentation[
                        obs_subset_anchor_mask_ix_rr, obs_subset_anchor_mask_ix_cc
                    ]
                )
                subset_ids = subset_ids[subset_ids != 0]
                # The values in the segmentation mask should be the cell/spot IDs
                # Subset the data and positions
                # for objects generated from the enable database, the index is the cell id.
                # TODO: Ensure that this is the case for all EMObjects
                pos_dict = {}
                for coord_sys in self._layerdict[layer]._pos.keys():
                    pos_dict[coord_sys] = (
                        self._layerdict[layer]._pos[coord_sys].loc[subset_ids, :]
                    )

                new_layer = BaseLayer(
                    data=self._layerdict[layer].data.loc[subset_ids, :],
                    obs=self._layerdict[layer].obs.loc[subset_ids, :],
                    var=self._layerdict[layer].var,
                    pos=pos_dict,
                    segmentation=self._layerdict[layer].segmentation,
                    name=layer,
                )
                E.add(new_layer)

        return E

    def _observations_for_segment(
        self,
        segment_id: Union[int, list, np.ndarray],
        mask_name: str,
        target_layer: str,
    ) -> dict:
        """Returns the observations in target layer for a given segment ID.
        For example, the CODEX cells of a specified visium spot or ROI mask segment.

        Args:
            segment_id: the segment ID to query
            mask_name: the name of the mask that contains segment_id
            target_layer: the layer to query for observations

        Returns:
            np.ndarray: the observations in target layer for a given segment ID
        """
        segment_to_cell_map = {}

        assert mask_name in self.mask.mask_names
        assert target_layer in self.layers

        # Check that a segmentation mask exists for the target layer
        if self._layerdict[target_layer].segmentation is None:
            if "segmentation_mask" in self.mask.mask_names:
                warning(
                    f"Automatically assigning mask `segmentation_mask` to {target_layer}.\
                        To assign a different mask, use `E.set_layer_segmentation()`."
                )
            else:
                raise EMObjectException(
                    f"No segmentation mask exists for {target_layer}.\
                                        Please specify a segmentation mask for {target_layer}\
                                        with `E.set_layer_segmentation().`"
                )

        if isinstance(segment_id, int):
            segment_id = [segment_id]

        # Get the pixels that belong to the segment
        segment_mask = sparse.coo_matrix(self.mask.mloc(mask_name))

        for si in segment_id:
            (segment_ix,) = np.where(segment_mask.data == si)

            if len(segment_ix) == 0:
                segment_to_cell_map[si] = []

            else:
                segment_ix_rr = segment_mask.row[segment_ix]
                segment_ix_cc = segment_mask.col[segment_ix]

                # Get the target layer's segmentation mask
                target_observations = np.unique(
                    self.mask.mloc(self._layerdict[target_layer].segmentation)[
                        segment_ix_rr, segment_ix_cc
                    ]
                )
                target_observations = target_observations[target_observations != 0]
                segment_to_cell_map[si] = target_observations

        return segment_to_cell_map

    def set_layer(self, value: Optional[str] = None) -> None:
        """Sets the active layer.

        Args:
            value: name of an existing layer in the EMObject
        Returns:
            None
        """
        assert value in self.ax or value is None
        self._validate()

        if value is None:
            self._activelayer = self._defaultlayer
        else:
            self._activelayer = value

    def _validate(self) -> None:
        """Validates the integrity of the EMObject
        as a check against unexpected modifications
        to the object."""

        for layer in self.layers:
            # Check that the obs index is consistent
            obs_ix_data = np.array(
                self._layerdict[layer].data.index
            )  # use arrays for consistency
            var_ix_data = np.array(self._layerdict[layer].data.columns)

            # Check the index of everything that is suppossed to be indexed by observations
            if self._layerdict[layer]._obs is not None:
                if not np.array_equal(
                    np.array(self._layerdict[layer]._obs.index), obs_ix_data
                ):
                    # the content of the index is not the same, check if the length is
                    if len(self._layerdict[layer]._obs.index) != len(obs_ix_data):
                        raise EMObjectException(
                            "Observation index mismatch (different lengths!)."
                        )
                    else:
                        # the length is the same, check if the order is the same
                        warning(
                            "Content of observation index is not the same as data. Renaming data index..."
                        )
                        self._layerdict[layer].data.index = self._layerdict[
                            layer
                        ]._obs.index

                    # raise EMObjectException('Observation index mismatch.')

            # Check that var axis is consistent
            if self._layerdict[layer].var is not None:
                if not np.array_equal(
                    np.array(self._layerdict[layer].var.index), var_ix_data
                ):
                    # the content of the index is not the same, check if the length is
                    if len(self._layerdict[layer].var.index) != len(var_ix_data):
                        raise EMObjectException(
                            "Variable index mismatch (different lengths!)."
                        )
                    else:
                        # the length is the same, check if the order is the same
                        warning(
                            "Content of variable index is not the same as data. Renaming data columns..."
                        )
                        self._layerdict[layer].data.columns = self._layerdict[
                            layer
                        ].var.index
                    # raise EMObjectException('Variable index mismatch.')

        if self._seg is not None and len(obs_ix_data) != self._seg.shape[0]:
            raise EMObjectException("Observation index mismatch.")

        if self._layerdict[layer]._pos is not None:
            for key in self._layerdict[layer]._pos.keys():
                if not np.array_equal(
                    np.array(self._layerdict[layer]._pos[key].index),
                    np.array(self._layerdict[layer].data.index),
                ):
                    raise EMObjectException("Observation index mismatch (pos).")

        # Check that segment axis is consistent
        if (
            self._seg is not None
            and self._mask is not None
            and self._seg.shape[1] != len(self._mask.mask_names)
        ):
            raise EMObjectException("Segment index mismatch.")

    def add_coordinate_system(
        self,
        label: str = None,
        coords: Union[np.ndarray, pd.DataFrame] = None,
        cols: Optional[Union[list, np.ndarray]] = None,
        scale_factor: Optional[float] = 1.0,
        layer: Optional[str] = None,
    ) -> None:
        """Add a new coordinate system to emobject.

        Args:
            label (str): name of new coordinate system
            coords (Union[np.ndarray, pd.DataFrame, None]): the coordinates (n_obs x dimensions)
            cols Optional[Union[list, np.ndarray, None]]: labels for cols e.g. x, y. Defaults to zero indexed ints
            scale_factor (Optional[float]): scale factor to apply to coordinates (common in Visium). Defaults to 1.

        Returns:
            None
        """

        if label is None:
            raise EMObjectException(
                "Must provide a name/label for this new coordinate system."
            )

        if coords is None:
            raise EMObjectException(
                "Must provide coordinate values for this new coordinate system."
            )

        if layer is None:
            layer = self._activelayer
        else:
            if layer not in self.layers:
                raise EMObjectException("Layer does not exist.")

        assert coords.shape[0] == self.n_obs

        if type(coords) == np.ndarray:
            coords = np.multiply(coords.astype(np.float32), scale_factor)
            coords = pd.DataFrame(
                coords, index=self._layerdict[layer].data.index, columns=cols
            )
        _ = self.pos  # make sure pos exists
        self.pos[label] = coords

    def add_mask(
        self,
        mask: Optional[np.ndarray] = None,
        mask_name: Optional[Union[np.ndarray, list]] = None,
    ) -> None:
        """Add a new mask to emobject.

        Args:
            mask (Optional[np.ndarray]): mask array (n_obs x n_masks)
            mask_name (Optional[Union[np.ndarray, list]]): name of mask. Defaults to None.
        """

        if mask is None:
            raise EMObjectException("Must provide a mask array.")

        if mask_name is None:
            raise EMObjectException("Must provide a mask name.")

        if type(mask_name) == str:
            mask_name = np.array([mask_name])

        if type(mask) == list:
            mask = np.array(mask)

        if type(mask_name) == list:
            mask_name = np.array(mask_name)

        if len(mask.shape) == 3:
            if mask.shape[0] != mask_name.shape[0]:
                raise EMObjectException("Mask and mask_name must have the same length.")
        else:
            if mask_name.shape[0] != 1:
                raise EMObjectException("Mask and mask_name must have the same length.")

        if self.mask is None:
            self._mask = EMMask(mask, mask_name)
        else:
            self._mask.add_mask(mask, mask_name)

    def set_layer_segmentation(self, layer: Optional[str], segmentation: str) -> None:
        """Sets the segmentation for a layer.

        Args:
            layer (str): name of layer
            segmentation (str): name of segmentation
        """

        if layer not in self.layers:
            raise EMObjectException(f"Layer {layer} does not exist.")

        if layer is None:
            layer = self._activelayer
            warning(
                f"Layer not specified, setting segmentation for active layer {layer}."
            )

        if segmentation not in self.mask.mask_names:
            raise EMObjectException(f"Mask {segmentation} does not exist.")

        self._layerdict[layer].segmentation = segmentation

    def drop_obs(self, obs: Union[list, np.ndarray]) -> None:
        """Drop observations from the current layer of the emObject.

        Args:
            obs (Union[list, np.ndarray]): list of observations to drop
        """

        if self._activelayer is None:
            raise EMObjectException("No active layer.")

        if type(obs) == list:
            obs = np.array(obs)

        self._layerdict[self._activelayer].data.drop(obs, inplace=True)
        self._layerdict[self._activelayer]._obs.drop(obs, inplace=True)

        if self._layerdict[self._activelayer]._pos is not None:
            for key in self._layerdict[self._activelayer]._pos.keys():
                self._layerdict[self._activelayer]._pos[key].drop(obs, inplace=True)

        self._layerdict[self._activelayer]._obs_ax = np.array(
            self._layerdict[self._activelayer].data.index
        )

        if self._seg is not None:
            warning("Existing `.seg` will be dropped. Attempting to reconstruct...")
            self._seg = None
            try:
                _ = self.seg
            except IndexError:
                warning(
                    "Failed to reconstruct `.seg`. Please pass an explicit coordinate system to `E.build_seg()`."
                )
                pass

        self._validate()

    def drop_var(self, var: Union[list, np.ndarray]) -> None:
        """Drop variables from the current layer of the emObject.

        Args:
            var (Union[list, np.ndarray]): list of variables to drop
        """

        if self._activelayer is None:
            raise EMObjectException("No active layer.")

        if type(var) == list:
            var = np.array(var)

        self._layerdict[self._activelayer].data.drop(var, axis=1, inplace=True)
        self._layerdict[self._activelayer].var.drop(var, inplace=True)
        self._layerdict[self._activelayer]._var_ax = np.array(
            self._layerdict[self._activelayer].data.columns
        )

        self._validate()

    def add_measurements(
        self,
        measurements: Union[np.ndarray, pd.DataFrame],
        var_names: Optional[Union[np.ndarray, list]] = None,
        layer: Optional[str] = None,
    ) -> None:
        """
        Add new variables to the current layer of the emObject.
        This expands the variable axis of the data array.
        """
        if layer is None:
            layer = self._activelayer

        if layer not in self.layers:
            raise EMObjectException("Layer does not exist.")

        if var_names is None and type(measurements) == np.ndarray:
            var_names = np.array([f"new_obs_{i}" for i in range(measurements.shape[1])])

        if type(measurements) == np.ndarray:
            measurements = pd.DataFrame(
                measurements, index=self._layerdict[layer].data.index, columns=var_names
            )

        if measurements.shape[0] != self.n_obs:
            raise EMObjectException(
                f"New measurements must have the same number of rows as existing data objects. Found {measurements.shape[0]} rows, expected {self.n_obs}."
            )

        if not np.all(measurements.index == self._layerdict[layer].data.index):
            raise EMObjectException(
                "New measurements must have the same index as existing observations."
            )

        self._layerdict[layer].data = pd.concat(
            [self._layerdict[layer].data, measurements], axis=1
        )
        self._layerdict[layer]._var_ax = np.array(self._layerdict[layer].data.columns)

        # also need to update var, which is indexed
        if (
            self._layerdict[layer].var is not None
            and self._layerdict[layer].var.shape[1] > 0
        ):
            self._layerdict[layer].var = pd.concat(
                [
                    self._layerdict[layer].var,
                    pd.DataFrame(
                        np.empty(measurements.shape[1], self.var.shape[1]),
                        index=measurements.columns,
                    ),
                ],
                axis=0,
            )
        else:
            self._layerdict[layer].var = pd.DataFrame(
                data=None, index=self._layerdict[layer]._var_ax
            )

        self._validate()

    def slice_on_segment(
        self,
        segment_id: Union[int, list, np.ndarray],
        mask_name: str = None,
        target_layer: Optional[str] = None,
    ) -> dict:
        """Slice the emObject on a segment.

        Args:
            segment_id (Union[int, list, np.ndarray]): segment id(s)
            mask_name (str): name of mask to use
            target_layer (Optional[str]): name of layer to slice on

        Returns:
            dict: dictionary of observations for each segment
        """

        if target_layer is None:
            target_layer = self._activelayer

        return self._observations_for_segment(
            segment_id=segment_id, mask_name=mask_name, target_layer=target_layer
        )
