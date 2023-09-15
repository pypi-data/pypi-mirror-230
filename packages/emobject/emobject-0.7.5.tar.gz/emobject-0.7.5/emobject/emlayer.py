from __future__ import annotations
from typing import Optional, Union
import numpy as np
from scipy import sparse
import pandas as pd
from logging import warning
from emobject.errors import EMObjectException


class BaseLayer:
    def __init__(
        self,
        data: Optional[Union[pd.DataFrame, np.ndarray, sparse.spmatrix]] = None,
        obs: Optional[pd.DataFrame] = None,
        var: Optional[pd.DataFrame] = None,
        sobs: Optional[pd.DataFrame] = None,
        pos: Optional[Union[pd.DataFrame, dict]] = None,
        segmentation: Optional[str] = None,
        name: Optional[str] = None,
        scale_factor: Optional[float] = None,
        assay: Optional[str] = None,
        spot_size: Optional[float] = None,
    ) -> BaseLayer:
        """
        Contains the all tabular/tensor data.

        Args:
            data (Optional[Union[pd.DataFrame, np.ndarray, sparse.spmatrix]]):  data matrix (n_obs x n_var)
            obs (pd.DataFrame): observation matrix (n_obs x annotations)
            var (Optional[pd.DataFrame]): variable matrix (n_var x annotations)
            sobs (Optional[pd.DataFrame]): segment observations
            name (Optional[str]): a name for the layer
            pos (Optional[Union[pd.DataFrame, dict]]): dictionary of position matricies
            segmentation (Optional[str]): name of segmentation mask
            scale_factor (Optional[float]): scale factor for spatial data/Visium
            assay (Optional[str]): assay type (e.g. Visium, seqFISH, etc.)
            spot_size (Optional[float]): spot size for Visium

        Returns:
            BaseLayer instance
        """

        # Get axis info from data matrix
        self._seg = None
        self._lname = name
        self._segmentation = None
        self._scale_factor = scale_factor
        self._assay = assay
        self._spot_size = spot_size

        if data is not None:
            self._obs_ax, self._var_ax = self._get_data_axes(data)
            self.data = data

        self._obs = obs
        if self._obs is not None:
            self._obs_ax = self._obs.index
            assert len(self._obs_ax) == len(self.data)

        self._var = var
        if self._var is not None:
            self._var_ax = self._var.index
            assert len(self._var_ax) == self.data.shape[1]

        self._sobs = sobs

        if name is None:
            # warning('No name provided for layer. Using "unnamed_layer" as default.')
            self._lname = "unnamed_layer"

        self._pos = pos
        if pos is not None:
            self._pos = self._build_pos(pos, self._obs_ax)

        if segmentation is not None:
            self._segmentation = segmentation

    @property
    def name(self) -> str:
        return self._lname

    @name.setter
    def name(self, value) -> None:
        if type(value) != str:
            raise EMObjectException(
                f"Layer names must be of type str, but received\
             name of type {type(value)}."
            )
        else:
            self._lname = value

    def _get_data_axes(self, data) -> tuple:
        """
        Extract observation and variable axis from data input.

        Args:
            data: Optional[Union[np.ndarray, sparse.spmatrix, pd.DataFrame]]

        Returns:
            _obs_ax: pd.RangeIndex
            _var_ax: pd.Index

        TO DO:
            - What is the best format for var axis? It could be str
            for biomarker names, etc. Or RangeIndex.
        """
        if type(data) == pd.DataFrame:
            # expect obs (rows) x var (cols)
            _obs_ax = data.index
            _var_ax = data.columns

        elif type(data) == np.ndarray:
            _obs_ax = pd.RangeIndex(start=0, stop=data.shape[1])
            _var_ax = pd.RangeIndex(start=0, stop=data.shape[0])

        elif type(data) == sparse._csr.csr_matrix:
            # TO DO: veryify sparse matrix functionality here.
            _obs_ax = pd.RangeIndex(start=0, stop=data.shape[1])
            _var_ax = pd.RangeIndex(start=0, stop=data.shape[0])

        else:
            raise EMObjectException(
                f"Expected data of type np.ndarray, \
                sparse.spmatrix, or pd.DataFrame. \
                Instead received data of type {type(data)}"
            )

        return _obs_ax, _var_ax

    def _build_obs(self, obs, _obs_ax) -> pd.DataFrame:
        """
        Build the obs matrix.
        """
        if obs is not None:
            if type(obs) == pd.DataFrame:
                assert len(obs.index) == len(_obs_ax)
                # To Do: align the indices.
        else:
            obs = pd.DataFrame(index=_obs_ax)
        return obs

    def _build_var(self, var, _var_ax) -> pd.DataFrame:
        """
        Build the var matrix.

        Note: conceptually this is indexed on data cols, but
        it is constructed here as row axis. e.g transpose of the illustration.
        """
        if var is not None:
            if type(var) == pd.DataFrame:
                assert len(var.index) == len(_var_ax)
            var = pd.DataFrame(data=var, index=_var_ax)
        else:
            var = pd.DataFrame(index=_var_ax)
        return var

    def _build_pos(
        self,
        pos: Optional[Union[pd.DataFrame, dict]] = None,
        _obs_ax: Optional[Union[np.ndarray, pd.Index]] = None,
    ) -> pd.DataFrame:
        """
        Build the pos matrix.
        TO DO: Extend this to hold multiple coordinate systems.
        """
        pos_dict = dict()
        if pos is not None:
            if type(pos) == dict:
                pos_dict = pos
            elif type(pos) == pd.DataFrame:
                assert len(pos.index) == len(_obs_ax)
                pos_dict[self._lname] = pos
            elif type(pos) == np.ndarray:
                cols = ["x", "y", "z"]
                pos_dict[self._lname] = pd.DataFrame(
                    pos.astype(np.float32), index=_obs_ax, columns=cols[: pos.shape[1]]
                )
        # To Do: align the indices.
        else:
            pos_dict[self._lname] = pd.DataFrame(index=_obs_ax)

        return pos_dict

    @property
    def var(self) -> pd.DataFrame:
        """if self._var is not None:
            self._var = self._build_var(self._var, self._var_ax)
        return self._var"""
        if self._var is None:
            self._var = self._build_var(self._var, self._var_ax)
        return self._var

    @var.setter
    def var(self, value: Optional[Union[np.array, pd.DataFrame]]) -> None:
        if value.shape[0] != self._var_ax.shape[0]:
            raise EMObjectException(
                "Must be a `n_var` length array of arbitrary\
                 width."
            )
        self._var = self._build_var(value, self._var_ax)

    @property
    def obs(self) -> pd.DataFrame:
        if self._obs is not None:
            self._obs = self._build_obs(self._obs, self._obs_ax)
        return self._obs

    @obs.setter
    def obs(self, value: Optional[Union[np.array, pd.DataFrame]]) -> None:
        if value.shape[0] != self._obs_ax.shape[0]:
            raise EMObjectException(
                "Must be a `n_obs` length array of arbitrary\
                 width."
            )
        self._obs = self._build_obs(value, self._obs_ax)

    @property
    def sobs(self) -> list:
        if self._sobs is None:
            # self._sobs = self._build_sobs()
            pass
        return self._sobs

    @sobs.setter
    def sobs(self, value) -> None:
        "TO DO: Add in type checking here."
        self._sobs = value

    @property
    def pos(self) -> dict:
        return self._pos

    @pos.setter
    def pos(self, value: Optional[dict] = None) -> None:
        if type(value) != dict:
            raise EMObjectException("Must be a dictionary of arrays.")

        for key, val in value.items():
            if val.shape[0] != self._layerdict[self._activelayer]._obs_ax.shape[0]:
                raise EMObjectException(
                    "Must be a `n_obs` length array of arbitrary\
                     width."
                )
        self._pos = value

    @property
    def segmentation(self) -> str:
        return self._segmentation

    @segmentation.setter
    def segmentation(self, value: str = None) -> None:
        self._segmentation = value


class LayeredData:
    """
    Stacks multiple BaseLayers into an indexed object.
    """

    def __init__(self, initial_layer: Optional[BaseLayer] = None) -> LayeredData:
        self._layerdict = dict()  # mapping of keys (layer names) to layer

        if initial_layer is not None:
            self.add(initial_layer)

    def __getitem__(self, key: str) -> BaseLayer:
        return self._layerdict[key]

    def __setitem__(self, key: str, layer: BaseLayer) -> None:
        self._layerdict[key] = layer

    def add(self, layer: BaseLayer = None) -> None:
        """
        Add a layer to the EMObject.

        Args:
            layer_name: the name of the layer to add.

        Returns:
            None
        """
        if layer.name not in self.ax:
            self._layerdict[layer.name] = layer
        else:
            warning(f"Layer name {layer.name} already in Layers. Overwriting.")
            self._layerdict[layer.name] = layer

    def drop(self, layer_name: Optional[str] = None) -> None:
        """
        Drop a layer from the EMObject

        Args:
            layer_name: the name of the layer to drop.

        Returns:
            None
        """
        if layer_name not in self.ax:
            raise EMObjectException(f"Layer name {layer_name} not in layers.")
        else:
            del self._layerdict[layer_name]

    @property
    def ax(self) -> list:
        return list(self._layerdict.keys())
