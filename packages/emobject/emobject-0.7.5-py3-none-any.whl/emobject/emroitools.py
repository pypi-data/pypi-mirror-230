import numpy as np
from skimage import draw
import emobject.database as db


def convert_rect_to_poly(roi_coord):
    """
    Converts roi coordinates to polygon-style data structure if it is rectangle style.

    Args:
        roi_coord: 2xN numpy array of roi coordinates in either poly or rectangle format.

    Returns:
        A 2xN numpy array of roi coordinates with polygon data structure.
    """

    if len(roi_coord) == 2:  # rect data structure only has two points
        poly_array = []
        roi_coord = roi_coord.T  # transpose required here for rectangular coordinates
        poly_array.append((roi_coord[0][0], roi_coord[1][0]))
        poly_array.append((roi_coord[0][1], roi_coord[1][0]))
        poly_array.append((roi_coord[0][1], roi_coord[1][1]))
        poly_array.append((roi_coord[0][0], roi_coord[1][1]))

        roi_coord = np.array(poly_array)

    return roi_coord


def roi_to_mask(roi_coord, image_shape):
    """
    Converts roi coordinates to binary mask.
    From, https://gist.github.com/hadim/fa89b50bbd240c486c61787d205d28a6

    Args:
        roi_coord: 2xN numpy array of roi coordinates.
        image_shape: a tuple of image shape.

    Returns:
        A binary mask with area enclosed in roi set to True.
    """

    vertex_row_coords = roi_coord[:, 1]
    vertex_col_coords = roi_coord[:, 0]
    fill_row_coords, fill_col_coords = draw.polygon(
        vertex_row_coords, vertex_col_coords, image_shape
    )
    mask = np.zeros(image_shape, dtype=bool)
    mask[fill_row_coords, fill_col_coords] = True

    return mask


def roi_dict_to_mask_dict(roi_dict, conn):
    """
    Converts a dictionary of rois to a dictionary of masks.

    Args:
        roi_dict: dictionary of roi_id, roi_coords (2xN np.array) key-value pairs.
        conn: RDS sql_alchemy connection.

    Returns:
        A dictionary of roi_id, binary_mask key_value pairs.
    """

    masks_dict = {}

    for (
        roi_id,
        roi_coord,
    ) in roi_dict.items():  # iterate over all rois from all notes in study
        image_shape = db.get_image_dimensions_for_roi_id(roi_id, conn)
        image_shape = (image_shape["HEIGHT"].item(), image_shape["WIDTH"].item())
        masks_dict[roi_id] = roi_to_mask(roi_coord, image_shape)

    return masks_dict


def combine_masks_dict(masks_dict):
    """
    Converts a dictionary of masks into one stacked mask.
    Warning, logic assumes ROIs are not overlapping

    Args:
        masks_dict: dictionary of roi_id, binary mask key-value pairs.

    Returns:
        A binary mask of all masks in dictionary combined.
    """

    # initialize a mask
    mask_keys = list(masks_dict.keys())
    combined_mask = np.zeros_like(masks_dict[mask_keys[0]], dtype="uint16")

    # stack image - each subroi is assigned a value equal to roi_id
    for roi_id, mask in masks_dict.items():
        combined_mask = combined_mask + roi_id * mask

    return combined_mask


def story_to_notes(story_title, study_id, conn):
    """
    Converts story title to notes_id.

    Args:
        story_title: A string representing the non-unique story title.
        study_id: An integer representing the unique study id.
        conn: RDS sql_alchemy connection.

    Returns:
        A list of all associated note_ids for the given story.
    """

    story_id = db.get_story_id_from_study_id_and_title(study_id, story_title, conn)

    note_ids = db.get_note_id_from_story_id(story_id, conn)

    return note_ids


def notes_to_rois(note_ids, conn):
    """
    Converts note_ids to roi coordinates.

    Args:
        note_ids: A list of integers representing note_ids.
        conn: RDS sql_alchemy connection.

    Returns:
        A dictionary of roi_id, roi key-value pairs, where rois are 2xN numpy arrays of coordinates.
    """

    rois = {}  # initialize container for rois

    if note_ids is None:
        return None

    else:
        for note_id in note_ids:
            roi_ids = db.get_roi_ids_from_note_id(note_id, conn)

            if roi_ids is not None:
                for roi_id in roi_ids:
                    rois[roi_id] = roi_id_to_roi(roi_id, conn)

                return rois
            else:
                return None


def roi_id_to_roi(roi_id, conn):
    """
    Converts roi_id to roi coordinates.

    Args:
        roi_id: An integer uniquely identifying an roi.
        conn: RDS sql_alchemy connection.

    Returns:
        A 2xN numpy array of roi coordinates scaled to the image size.
    """

    roi_coords = db.get_roi_coord_from_roi_id(roi_id, conn)
    # get image dimensions to properly scale
    im_dim = db.get_image_dimensions_for_roi_id(roi_id, conn)

    # scale roi_coord by image dimensions
    # currently there is unintuitive behavior where both x and y points are scaled by the height
    roi_coords = (
        np.array(
            [
                np.array(roi_coords["x"]) * im_dim["HEIGHT"].item(),
                np.array(roi_coords["y"]) * im_dim["HEIGHT"].item(),
            ]
        ).T
    ).astype("int")

    roi_coords = convert_rect_to_poly(
        roi_coords
    )  # converts rect to poly data structure

    return roi_coords


def story_to_rois(story_title, study_id, conn):
    """
    Returns all the rois for a given story in a dictionary organized by acquisition_id.

    Args:
        story_title: string representing the non-unique story title.
        study_id: int representing the unique study id.
        conn: RDS sql_alchemy connection.

    Returns:
        A dictionary of rois from the study organized by acquisition_id (key),
        where each value is another dictionary with roi_id, roi_coordinates key-value pairs.
    """

    # get note_ids
    notes = story_to_notes(story_title, study_id, conn)

    # get roi_id, roi_coord
    roi_dict = notes_to_rois(notes, conn)
    if roi_dict is not None:
        roi_dict = split_roi_id_by_acq_id(roi_dict, conn)
    else:
        roi_dict = None
    return roi_dict


def split_roi_id_by_acq_id(roi_dict, conn):
    """
    Given a dictionary with roi_id keys, splits into nested dictionary organized by acquisition_id.

    Args:
        roi_dict: dictionary with roi_ids as keys, and any values as values.

    Returns:
        A dictionary of dictionaries, where the highest level keys are acquisition_ids.
    """

    split_dict = {}

    for roi_id, value in roi_dict.items():
        acq_id = db.get_acq_id_from_roi_id(roi_id, conn)

        if acq_id not in split_dict.keys():
            split_dict[acq_id] = {}

        split_dict[acq_id][roi_id] = value

    return split_dict


def get_all_masks_for_story(study_id, story_title, conn):
    """
    Given a study_id and story_title, return a dictionary of acquisition_ids and masks.

    Args:
        study_id: int representing unique study id.
        story_title: string representing (hopefully) unique story title.

    Returns:
        A dictionary of acquisition_id (key), mask (value) pairs.
    """
    story_rois = story_to_rois(story_title, study_id, conn)
    combo_mask = {}
    for acq_id, roi_values in story_rois.items():
        combo_mask[acq_id] = combine_masks_dict(roi_dict_to_mask_dict(roi_values, conn))

    return combo_mask


def get_all_masks_for_story_and_acq_id(study_id, story_title, acquisition_id, conn):
    """
    Given a study_id and story_title, return a dictionary of acquisition_ids and masks.

    Args:
        study_id: int representing unique study id.
        story_title: string representing (hopefully) unique story title.

    Returns:
        A dictionary of acquisition_id (key), mask (value) pairs.
    """
    story_rois = story_to_rois(story_title, study_id, conn)

    if story_rois is not None:
        combo_mask = {}
        for acq_id, roi_values in story_rois.items():
            combo_mask[acq_id] = combine_masks_dict(
                roi_dict_to_mask_dict(roi_values, conn)
            )

    else:
        combo_mask = None
    return combo_mask


def scale_verticies(vertices, img_shape):
    vertices[:, 0] = vertices[:, 0] * img_shape[1]
    vertices[:, 1] = vertices[:, 1] * img_shape[0]
    return vertices


def roi_df_to_mask_dict(roi_df):
    # Get the unique region_of_interest_ids
    roi_ids = np.unique(roi_df["region_of_interest_id"])

    rois = list()  # store the masks in a dictionary keyed by name
    names = list()  # store the names of the masks
    for roi_id in roi_ids:
        # get the vertices for the current roi_id
        vertices = roi_df.loc[
            roi_df["region_of_interest_id"] == roi_id, ["y", "correct_x"]
        ].values
        name = roi_df.loc[roi_df["region_of_interest_id"] == roi_id, "title"].values[0]
        names.append(name)
        roi_type = roi_df.loc[
            roi_df["region_of_interest_id"] == roi_id, "region_of_interest_type"
        ].values[0]

        if roi_type == "box":
            vertices = convert_rect_to_poly(vertices)

        img_shape = roi_df.loc[
            roi_df["region_of_interest_id"] == roi_id, ["width", "height"]
        ].values[0]
        vertices = scale_verticies(vertices, img_shape)
        mask = roi_to_mask(vertices, img_shape)
        rois.append(mask.T)

    rois = np.array(rois, dtype=int)
    for i in range(0, rois.shape[0]):
        rois[i, :, :] = rois[i, :, :] * roi_ids[i]

    unique_story_names = np.unique(names)
    mask_dict = dict()
    for unique_name in unique_story_names:
        (ix,) = np.where(np.array(names) == unique_name)
        mask = rois[ix, :, :]
        mask_dict[unique_name] = np.sum(mask, axis=0)

    return mask_dict
