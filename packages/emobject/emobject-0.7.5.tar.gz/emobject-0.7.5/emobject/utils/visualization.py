from __future__ import annotations
from typing import Optional
from emobject.errors import EMObjectException
from emobject.emobject import EMObject
import numpy as np
import cv2

import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl


def plot_cells(
    E: EMObject = None,
    coordinate_system: Optional[str] = None,
    factor: Optional[str] = None,
    size: Optional[float] = 3,
    invert_axis: Optional[bool] = True,
    scale_factor: float = 1.0,
):
    """Plots the cells in EMObject as a scatterplot.

    Args:
        E : EMObject to plot
        factor : the annotation by which to color cells.
    """

    plt.clf()
    if coordinate_system is None:
        coordinate_system = "raw"

    x = np.multiply(
        E.pos[coordinate_system].iloc[:, 0].to_numpy(dtype=np.float32), scale_factor
    )
    y = np.multiply(
        E.pos[coordinate_system].iloc[:, 1].to_numpy(dtype=np.float32), scale_factor
    )
    size *= scale_factor
    if factor not in E.obs.columns:
        raise EMObjectException(f"Factor {factor} not found in obs.")

    factor = E.obs[factor].to_numpy()
    pal = sns.color_palette("husl", len(np.unique(factor)))
    sns.scatterplot(x=x, y=y, hue=factor, s=size, palette=pal, linewidth=0)
    if invert_axis:
        plt.gca().invert_yaxis()
    plt.legend()
    plt.show()


def __colorize(im, color, clip_percentile=0.1):
    """
    Helper function to create an RGB image from a single-channel image using a
    specific color.
    """
    # Check that we do just have a 2D image
    if im.ndim > 2 and im.shape[2] != 1:
        raise EMObjectException("This function expects a single-channel image!")

    # Rescale the image according to how we want to display it
    im_scaled = im.astype(np.float32) - np.percentile(im, clip_percentile)
    im_scaled = im_scaled / np.percentile(im_scaled, 100 - clip_percentile)
    im_scaled = np.clip(im_scaled, 0, 1)

    # Need to make sure we have a channels dimension for the multiplication to work
    im_scaled = np.atleast_3d(im_scaled)

    # Reshape the color (here, we assume channels last)
    color = np.asarray(color).reshape((1, 1, -1))
    return im_scaled * color


def plot_channels(
    E: EMObject = None,
    channels: Optional[list] = None,
    colors: Optional[list] = [
        "blue",
        "magenta",
        "green",
        "yellow",
        "red",
        "cyan",
        "white",
    ],
    x_min: Optional[int] = None,
    x_max: Optional[int] = None,
    y_min: Optional[int] = None,
    y_max: Optional[int] = None,
    save_path: Optional[str] = None,
):
    """Plots the channels in EMObject as a scatterplot.

    Args:
        E : EMObject to plot
        channels : the channels to plot
    """
    color_dict = {
        "blue": (0, 0, 1),
        "magenta": (1, 0, 1),
        "green": (0, 1, 0),
        "yellow": (1, 1, 0),
        "red": (1, 0, 0),
        "cyan": (0, 1, 1),
        "white": (1, 1, 1),
    }
    mpl.rcParams["pdf.fonttype"] = 42

    if channels is None:
        channels = E.img.channels

    if len(channels) > len(colors) or len(channels) > len(color_dict):
        raise EMObjectException(
            "Too many channels to plot. \
                                Please specify a subset of 7 or fewer channels."
        )
    ch_upper = [x.upper() for x in E.img.channels]
    for c in channels:
        if c.upper() not in ch_upper:
            raise EMObjectException(f"Channel {c} not found in EMObject.")

    for i in range(0, len(channels)):
        ch = channels[i]
        color = colors[i]

        # Get the image data
        (ix,) = np.where(np.array(ch_upper) == ch.upper())
        assert len(ix) == 1, f"Channel {ch} found {len(ix)} times in EMObject."
        ix = ix[0]
        img = E.img.img[ix, :, :]

        # Colorize the image
        img = __colorize(img, color_dict[color])
        if i == 0:
            img_all = img
        else:
            img_all += img

    img_all = np.clip(img_all, 0, 1)

    fig, ax = plt.subplots()

    for i in range(0, len(channels)):
        ch = channels[i]
        color = colors[i]
        ax.plot(0, 0, "-", c=color_dict[color], label=ch)

    ax.imshow(img_all)

    if x_min is not None and x_max is not None:
        ax.set_xlim(x_min, x_max)
    if y_min is not None and y_max is not None:
        ax.set_ylim(y_min, y_max)

    plt.axis(False)
    plt.legend()

    if save_path is not None:
        plt.savefig(save_path)

    plt.show()


def plot_mask_overlay(
    E: EMObject = None,
    mask: Optional[str] = None,
    channels: Optional[list] = None,
    mask_color: Optional[str] = "white",
    alpha: Optional[float] = 0.5,
    colors: Optional[list] = [
        "blue",
        "magenta",
        "green",
        "yellow",
        "red",
        "cyan",
        "white",
    ],
    segment_id: Optional[int] = None,
    save_path: Optional[str] = None,
) -> None:
    """Plots the mask in EMObject as a scatterplot.

    Args:
        E (EMObject): EMObject to plot
        mask (str): the mask to plot
        channels (list): the channels to plot
        mask_color (str): the color of the mask
        colors (list): the colors of the channels
        segment_id (int): the segment to plot

    Returns:
        None
    """
    color_dict = {
        "blue": (0, 0, 1),
        "magenta": (1, 0, 1),
        "green": (0, 1, 0),
        "yellow": (1, 1, 0),
        "red": (1, 0, 0),
        "cyan": (0, 1, 1),
        "white": (1, 1, 1),
    }

    mpl.rcParams["pdf.fonttype"] = 42

    # Get mask
    if mask is None:
        raise EMObjectException("Please specify a mask to plot.")

    if mask not in E.mask.mask_names:
        raise EMObjectException(f"Mask {mask} not found in EMObject.")

    if segment_id is None:
        image = E.mask.mloc(mask) != 0
    else:
        image = E.mask.mloc(mask) == segment_id
    image = image.astype(np.uint8)

    cnts = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    if channels is not None:
        if len(channels) > len(colors) or len(channels) > len(color_dict):
            raise EMObjectException(
                "Too many channels to plot. \
                                    Please specify a subset of 7 or fewer channels."
            )
        ch_upper = [x.upper() for x in E.img.channels]
        for c in channels:
            if c.upper() not in ch_upper:
                raise EMObjectException(f"Channel {c} not found in EMObject.")

        for i in range(0, len(channels)):
            ch = channels[i]
            color = colors[i]

            # Get the image data
            (ix,) = np.where(np.array(ch_upper) == ch.upper())
            assert len(ix) == 1, f"Channel {ch} not found {len(ix)} times in EMObject."
            ix = ix[0]
            img = E.img.img[ix, :, :]

            # Colorize the image
            img = __colorize(img, color_dict[color])
            if i == 0:
                img_all = img
            else:
                img_all += img

        img_all = np.clip(img_all, 0, 1)
        back = img_all.copy()
        # dummy plot to get legend
        for i in range(0, len(channels)):
            ch = channels[i]
            color = colors[i]
            plt.plot(0, 0, "-", c=color_dict[color], label=ch)

        for c in cnts:
            cv2.drawContours(img_all, [c], -1, color_dict[mask_color], thickness=-1)
            result = cv2.addWeighted(img_all, 1 - alpha, back, alpha, 0)
        for c in cnts:
            cv2.drawContours(result, [c], -1, color_dict[mask_color], thickness=5)
        plt.imshow(result)
        plt.axis(False)
        plt.legend()
        if save_path is not None:
            mpl.rcParams["figure.dpi"] = 300
            plt.savefig(f"{save_path}/{mask}_seg={segment_id}.pdf")
        plt.show()
        cv2.waitKey(10)
        cv2.destroyAllWindows()

    else:
        # no channels specified, just plot the mask
        plt.imshow(mask)
        cv2.waitKey(10)
        cv2.destroyAllWindows()


def plot_cell_overlay(
    E: EMObject = None,
    coordinate_system: Optional[str] = None,
    factor: Optional[str] = None,
    size: Optional[float] = 3,
    invert_axis: Optional[bool] = False,
    scale_factor: float = 1.0,
    backing_image: Optional[np.ndarray] = None,
    x_min: Optional[float] = None,
    x_max: Optional[float] = None,
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    alpha: Optional[float] = 1,
    save_path: Optional[str] = None,
) -> None:
    """Plots the cells in EMObject as a scatterplot.

    Args:
        E : EMObject to plot
        factor : the annotation by which to color cells.
        size : the size of the points, in Visium use spot size
        invert_axis : whether to invert the y axis. Default is True.
        scale_factor : the scale factor to apply to the coordinates. Default is 1.0/No scaling.
        backing_image : an image to plot behind the cells. Default is None.
        x_min : the minimum x value to plot. Default is None.
        x_max : the maximum x value to plot. Default is None.
        y_min : the minimum y value to plot. Default is None.
        y_max : the maximum y value to plot. Default is None.
        alpha : the alpha value to use for the cells. Default is 1.
        save_path : the path and filename to save the plot to. If None, the plot will not be saved. Default is None.

    Returns:
        None
    """

    plt.clf()
    if coordinate_system is None:
        if len(list(E.pos.keys())) == 1:
            coordinate_system = list(E.pos.keys())[0]
        else:
            raise EMObjectException(
                f"Multiple coordinate systems found. Please specify one of {list(E.pos.keys())}."
            )

    x = np.multiply(
        E.pos[coordinate_system].iloc[:, 0].to_numpy(dtype=np.float32), scale_factor
    )
    y = np.multiply(
        E.pos[coordinate_system].iloc[:, 1].to_numpy(dtype=np.float32), scale_factor
    )
    size *= scale_factor
    if factor not in E.obs.columns:
        raise EMObjectException(f"Factor {factor} not found in obs.")

    factor = E.obs[factor].to_numpy()
    pal = sns.color_palette("husl", len(np.unique(factor)))

    fig, ax = plt.subplots()

    if backing_image is not None:
        ax.imshow(backing_image)

    sns.scatterplot(
        x=x, y=y, hue=factor, s=size, palette=pal, linewidth=0, ax=ax, alpha=alpha
    )

    if invert_axis:
        plt.gca().invert_yaxis()

    if x_min is not None and x_max is not None:
        ax.set_xlim(x_min, x_max)
    if y_min is not None and y_max is not None:
        ax.set_ylim(y_min, y_max)

    plt.legend()

    if save_path is not None:
        plt.savefig(save_path)
    plt.show()
