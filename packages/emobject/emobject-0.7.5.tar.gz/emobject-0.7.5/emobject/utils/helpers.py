import numpy as np
from skimage.draw import disk
from emobject.emimage import EMMask


def build_visium_segmentation_mask(
    spot_coords: np.ndarray = None,
    spot_size: float = None,
    scale_factor: float = None,
    shape: tuple = None,
) -> np.ndarray:
    """
    Builds a mask for a Visium segmentation. Required for slicing through emObjects.
    Args:
        spot_coords: A 2xN numpy array of spot coordinates.
        spot_size: The size of the spots in pixels.
        scale_factor: The scale factor of the image.
        shape: The shape of the backing image.

    Returns:
        seg_mask: A 2D numpy array of the segmentation mask. Non-zero values are spot ids.
        spot_ids: A dictionary mapping spot ids to barcode
    """

    assert len(shape) == 2
    assert len(spot_coords.shape) == 2
    assert spot_coords.shape[1] == 2

    if scale_factor is not None:
        spot_size = spot_size * scale_factor
        spot_coords = spot_coords * scale_factor

    seg_mask = np.zeros(shape, dtype=np.uint16)

    for spot_id in range(1, len(spot_coords) + 1):
        spot_coord = spot_coords[spot_id - 1]
        if spot_coord[0] < 0 or spot_coord[1] < 0:
            continue
        else:
            # Fill a circle around the spot_coord with diameter spot_size with the spot_id
            rr, cc = disk((spot_coord[1], spot_coord[0]), spot_size / 2)
            try:
                seg_mask[rr, cc] = spot_id
            except IndexError:
                print(f"Index error for spot {spot_id} at {spot_coord}")

    return seg_mask


def merge_emmask(emmask_1, emmask_2) -> EMMask:
    """
    Merge two emmasks into one.

    Args:
        emmask_1 (EMMask): The first EMMask object
        emmask_2 (EMMask): The second EMMask object

    Returns:
        merged_emmask (np.ndarray): A single EMMask object
    """

    #  masks must be the same shape
    if len(emmask_1.shape) == 2:
        shape_1 = emmask_1.shape
    else:
        shape_1 = emmask_1.shape[1:]

    if len(emmask_2.shape) == 2:
        shape_2 = emmask_2.shape
    else:
        shape_2 = emmask_2.shape[1:]

    assert shape_1 == shape_2

    # merge names
    names = np.concatenate([emmask_1.mask_names, emmask_2.mask_names])
    masks = np.stack([emmask_1.mask, emmask_2.mask], axis=0)

    return EMMask(masks=masks, mask_idx=names)
