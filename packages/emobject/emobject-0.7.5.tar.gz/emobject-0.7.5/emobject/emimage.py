from __future__ import annotations
import numpy as np
import zarr
import matplotlib.pyplot as plt

# from dask import array as da
from numcodecs import Blosc
from typing import Optional, Union
import warnings
import os
from emobject.errors import EMObjectException
from scipy import sparse
import tifffile


class EMImage:
    """
    An image container class

    Args:
        img (Union[zarr.array, np.ndarray]): Image file
        channels (np.ndarray): Biomarker channel names
        chunk_size (tuple): Tuple of ints describing the zarr chunksize
        img_name (str): Name of image.
        to_disk (bool): toggle saving of zarr archive to disk. If True, uses img_name
            as file name.
        out_dir (str): directory to write zarr. If None, writes to current directory.
    """

    def __init__(
        self,
        img: Optional[Union[zarr.array, np.ndarray, str]] = None,
        channels: Optional[np.ndarray] = None,
        chunk_size=(256, 256),
        img_name: Optional[str] = None,
        format: Optional[str] = "zarr",
        to_disk: Optional[bool] = False,
        out_dir: Optional[str] = None,
    ) -> EMImage:
        # Handle outdir.
        if to_disk:
            if out_dir is None:
                out_dir = "."

            if not os.path.exists(out_dir):
                os.mkdir(out_dir)

        if type(img) == np.ndarray:
            if format == "zarr":
                # convert to zarr
                # TO DO: need to read more to understand zarr read from disk.
                compressor = Blosc(cname="zstd", clevel=3, shuffle=2)
                array = zarr.array(img, chunks=chunk_size, compressor=compressor)
                if to_disk:
                    file_name = f"{img_name}.zarr"
                    zarr_file = os.path.join(out_dir, file_name)
                    zarr.convenience.save(zarr_file, array)
                    array = zarr.convenience.open(zarr_file, mode="r")
            else:
                array = img
            del img

        elif type(img) == zarr.array:
            # already receiving a zarr
            if to_disk:
                file_name = f"{img_name}.zarr"
                zarr_file = os.path.join(out_dir, file_name)
                zarr.convenience.save(zarr_file, array)
                array = zarr.convenience.open(zarr_file)

        elif type(img) == str:
            # check that file exists
            if not os.path.exists(img):
                raise EMObjectException(f"File {img} does not exist.")

            img_name, array = self.__handle_img_path(
                img, to_disk=to_disk, out_dir=out_dir
            )

        if channels is not None:
            if len(channels) != array.shape[0]:
                warnings.warn(
                    (
                        "Length of channel names does not match number",
                        "of channels in provided image.",
                    )
                )

                if len(channels) > array.shape[0]:
                    print(
                        f"Using the first {len(array.shape[0])} channel\
                         names to match image."
                    )
                    channels = channels[: array.shape[0]]
                else:
                    to_add = len(array.shape[0]) - len(channels)
                    print(
                        f"Adding {to_add} dummy channel names to match \
                        image."
                    )
                    new_ch = np.array(
                        ["ch_" + str(i + len(channels)) for i in range(0, to_add)]
                    )  # noqa
                    channels = np.concatenate([channels, new_ch])

        self.img = array
        self.channels = channels
        self.name = img_name
        self.shape = array.shape

    def plot_channel(self, channel: str = None) -> None:
        """Plot a single image channel.

        Args:
            channel (str): the channel name to plot
        """

        ix = np.where(np.array(self.channels) == channel)[0][0]
        x = self._minmaxrescale(ix)
        plt.imshow(x, cmap="gray", vmax=np.quantile(x.flatten(), 0.998))

    def _minmaxrescale(self, ix):
        x = self.img[ix, :, :]
        min = np.min(x)
        max = np.max(x)
        x = (x - min) / (max - min)
        return x

    def __handle_img_path(
        self, img: str, to_disk: Optional[bool] = False, out_dir: Optional[str] = None
    ):
        """
        Helper function to open image file.

        Args:
            img (str): path to image file
        """

        if not os.path.exists(img):
            raise EMObjectException(f"File {img} does not exist.")

        img_name = os.path.basename(img).split(".")[0]
        # if there's a / in the name, use the last part
        if "/" in img_name:
            img_name = img_name.split("/")[-1]

        # Figure out what kind of file it is
        if img.endswith(".zarr"):
            array = zarr.convenience.open(img, mode="r")

        elif img.endswith(".npy"):
            array = np.load(img)

            if to_disk:
                file_name = f"{img_name}.zarr"
                zarr_file = os.path.join(out_dir, file_name)
                zarr.convenience.save(zarr_file, array)
                array = zarr.convenience.open(zarr_file, mode="r")

        elif img.endswith(".tiff") or img.endswith(".tif"):
            array = tifffile.imread(img)
            if to_disk:
                file_name = f"{img_name}.zarr"
                zarr_file = os.path.join(out_dir, file_name)
                zarr.convenience.save(zarr_file, array)
                array = zarr.convenience.open(zarr_file, mode="r")

        else:
            raise EMObjectException(f"File type not recognized for {img}")

        return array, img_name


class EMMask:
    """
    A container for multiple 2-D masks.

    Args:
        masks (np.ndarray, dict): ROI masks associated with this acquisition, expects tensor
        mask_idx (Union[list, np.ndarray]): index of mask names, matching height axis of `masks`.
        style (str): Either 'tensor' or 'dict', indicating how the mask is represented
        dims (tuple): Tuple of integers indicating the width and height of the full mask. This should
            be the exact same as the image or full object dimensions.
        pos (tuple): Dict of x,y positions of the top left corner of a
            minimal mask within the full image.
        to_disk (bool): Indicates whether or not the mask will be stored as Zarr on disk.
    """

    def __init__(
        self,
        masks: Optional[Union(np.ndarray, dict)] = None,
        mask_idx: Optional[Union[list, np.ndarray]] = None,
        style: Optional[str] = None,
        dims: Optional[tuple] = None,
        pos: Optional[dict] = None,
        to_disk: Optional[bool] = None,
    ) -> EMMask:
        # init
        self._mask_idx = mask_idx
        self.mask = masks

        # define
        if isinstance(masks, np.ndarray):
            self._style = "tensor"
            if len(masks.shape) == 2:
                masks = masks.reshape(1, masks.shape[0], masks.shape[1])

            self.dims = (masks.shape[1], masks.shape[2])

            if mask_idx is not None:
                if type(mask_idx) == list:
                    mask_idx = np.array(mask_idx)
            else:
                # Make dummy mask names
                mask_idx = np.array(
                    [f"mask_{i}" for i in range(0, masks.shape[0])]
                )  # noqa

        elif isinstance(masks, dict):
            for key in masks.keys():
                assert isinstance(masks[key], np.ndarray)
            self._style = "dict"

            # Dims must be provided if dict is used
            #: TODO Slicing must account for this!
            if dims is not None:
                self.dims = dims
            else:
                raise EMObjectException("Must provide image dims with dictionary masks")

            if pos is not None:
                assert pos.keys() == masks.keys()
                self.pos = pos
            else:
                raise EMObjectException(
                    "Must provide mask positions with dictionary masks"
                )

            self._mask_idx = np.array(list(masks.keys()))

    def __getitem__(self, key: str) -> np.ndarray:
        return self.mloc(key)

    def _build_mask(self) -> np.ndarray:
        for i in len(self.masks):
            # check the sparsity of the mask
            total_elements = self.masks[i].size
            zero_elements = (self.masks[i] == 0).sum()
            sparsity = zero_elements / total_elements
            if sparsity > 0.5:
                # if the mask is sparse, we will use a sparse matrix
                # to save memory
                self.masks[i] = sparse.coo_matrix(self.masks[i])

    @property
    def n_masks(self) -> int:
        return len(self.mask_names)

    @property
    def dim(self) -> tuple(int, int):
        if self._style == "tensor":
            if len(self.mask.shape) == 2:
                return self.mask.shape
            else:
                return self.mask.shape[1:]
        else:
            return [m.shape for m in self.mask]

    @property
    def mask_style(self) -> str:
        return self._style

    @property
    def mask_names(self) -> np.ndarray:
        if type(self._mask_idx) == str:
            self._mask_idx = np.array([self._mask_idx])
        if len(self._mask_idx.shape) == 0:
            self._mask_idx = self._mask_idx.reshape(-1)
        return self._mask_idx

    @mask_names.setter
    def mask_names(self, value: Optional[Union[np.ndarray, list]] = None) -> None:
        if type(value) == list:
            value = np.array(value)
        assert value.shape[0] == self.n_masks, f"{value.shape[0]} != {self.n_masks}"
        self._mask_idx = value

    @property
    def n_seg(self) -> int:
        if self._style == "tensor":
            n_seg_dict = dict()
            if len(self.mask.shape) == 2:
                self.mask = self.mask[np.newaxis, :, :]

            for i, mask in enumerate(self.mask_names):
                n_seg_dict[mask] = np.unique(self.mask[i, :, :]).shape[0] - 1
            return n_seg_dict
        else:
            return len(self.mask.keys())

    def add_mask(
        self,
        mask: Union[np.ndarray, sparse.coo_matrix] = None,
        mask_name: Optional[str] = None,
        dims: Optional[tuple] = None,
        pos: Optional[tuple] = None,
    ) -> None:
        """
        Add a mask to the mask tensor.

        Args:
            mask (np.ndarray): the mask to add
            mask_name (str): the name of the mask to add

        Returns:
            None
        """
        if mask_name is None:
            raise EMObjectException("Must provide a mask name.")

        if mask is None:
            raise EMObjectException("Must provide a mask.")

        if self._style == "tensor":
            if len(mask.shape) == 2:
                mask.reshape(1, mask.shape[0], mask.shape[1])
            if len(self.mask.shape) == 2:
                self.mask = self.mask.reshape(1, self.mask.shape[0], self.mask.shape[1])

            """if type(mask) == np.ndarray:
                # check the sparsity of the mask
                total_elements = mask.size
                zero_elements = (mask == 0).sum()
                sparsity = zero_elements / total_elements
                if sparsity > 0.5:
                    # if the mask is sparse, we will use a sparse matrix
                    # to save memory
                    mask = sparse.coo_matrix(mask)"""

            # self.mask = np.append(self.mask, axis=0)

            self.mask = np.concatenate([self.mask, mask[np.newaxis, :, :]], axis=0)
            self._mask_idx = np.concatenate(
                [self._mask_idx, np.array([mask_name]).reshape(-1)]
            )

        else:
            self.mask[mask_name] = mask
            self.dims[mask_name] = dims

    def remove_mask(self, mask_name: Optional[str] = None) -> None:
        """
        Remove a mask from the mask object.

        Args:
            mask_name (str): the name of the mask to remove
        Returns:
            None
        """
        if mask_name is None:
            raise EMObjectException("Must provide a mask name.")
        if mask_name not in self.mask_names:
            raise EMObjectException(f"Mask name {mask_name} not found.")

        if self._style == "tensor":
            (i,) = np.where(self.mask_names == mask_name)
            self.mask = np.delete(self.mask, i, axis=0)
            self.mask_names = np.delete(self.mask_names, i, axis=0)
        else:
            self.mask.pop(mask_name)
            self.pos.pop(mask_name)

    def mloc(
        self, mask_name: Optional[str] = None, return_dense: Optional[bool] = False
    ) -> np.ndarray:
        """
        Select mask by name. The purpose of this is to give a
        indexing to the 3rd dimension of the mask tensor (e.g. mask name)

        Args:
            mask_name (str): the name of the mask to return.

        Returns:
            np.ndarray
        """
        if self._style == "tensor":
            (i,) = np.where(self.mask_names == mask_name)

            if type(self.mask[i]) == sparse.coo_matrix:
                if return_dense:
                    if len(self.mask[i].shape) == 3:
                        return self.mask[i].dense().squeeze()
                    else:
                        return self.mask[i].dense()
            else:
                if len(self.mask[i].shape) == 3:
                    return self.mask[i].squeeze()
                else:
                    return self.mask[i]
        else:
            return self.__pad_mask_to_image(
                self.mask[mask_name],
                x=self.pos[mask_name][0],
                y=self.pos[mask_name][1],
                W=self.dims[0],
                H=self.dims[1],
            )

    def plot(self, mask_name=None, **kwargs) -> None:
        """Plots a mask.

        Args:
            mask_name (str): the mask name to plot

        Returns:
            None
        """
        img = self.mloc(mask_name=mask_name, return_dense=True)
        plt.imshow(img, cmap="nipy_spectral")

    def __pad_mask_to_image(mask, x, y, W, H):
        # Determine the mask dimensions
        mask_height, mask_width = mask.shape

        x = int(x)
        y = int(y)
        W = int(W)
        H = int(H)

        # Calculate the padding sizes
        top_padding = y
        bottom_padding = H - (y + mask_height)
        left_padding = x
        right_padding = W - (x + mask_width)

        # Pad the mask array with zeros
        padded_mask = np.pad(
            mask,
            ((top_padding, bottom_padding), (left_padding, right_padding)),
            mode="constant",
        )

        return padded_mask
