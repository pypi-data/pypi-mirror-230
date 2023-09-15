import os
import pandas as pd
from dotenv import load_dotenv
from typing import Union


class Engine:
    pass


def _biomarker_name_filter(n):
    """Check if a biomarker name is valid
    will remove "EMPTY", "BLANK" and all numeric markers

    Args:
        n (str): biomarker name

    Returns
        bool: if the biomarker name is valid

    """
    if n.isnumeric():
        return False
    if n.upper() in ["EMPTY", "BLANK"]:
        return False
    return True


def load_env_var():
    if os.path.exists(os.path.expanduser("~/.env")):
        load_dotenv(os.path.expanduser("~/.env"))


def connect_sf():
    """
    Establish a SnowflakeConnection

    Returns:
        SnowflakeConnection
    """


def connect_rds(disable_autosource=False):
    """Construct a postgres(RDS) connector

    Args:
        disable_autosource (bool, optional): if set to False (autosource),
            will look for file ~/.Pythonenv and add env variables from the file

    Returns:
        sqlalchemy.engine.base.Engine

    """


def connect_boto3(disable_autosource=False):
    """Construct a s3 connector

    Args:
        disable_autosource (bool, optional): if set to False (autosource),
            will look for file ~/.Pythonenv and add env variables from the file

    Returns:
        boto3.resources.factory.s3.ServiceResource

    """


def get_study_id_for_acquisition_id(acquisition_id, conn):
    """Given an acquisition id, returns a study id

    Args:
        acquisition_id (str): acquisition id
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns
        study_id (int): study id

    """


def get_all_acquisition_ids_for_study_id(study_id: int, conn) -> list:
    """Given an study id, returns a list of the acquisition ids

    Args:
        acquisition_id (str): acquisition id
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns
        study_id (int): study id

    """


def get_all_annotation_ids_for_segmentation_version(
    acquisition_id: str = None,
    segmentation_version: int = None,  # noqa
    conn: Engine = None,
) -> list:
    """Given an annotation id, returns the segmentation version.

    Note that segmentation version is not unique across the platform,
    but is unique within a study

    Args:
        annotation_id (int): annotation id
        acquisition_id (str): acquisition id, note that this argument is not
            needed for the query, keeping it for backward compatibility
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        int: segmentation version

    """


def get_all_biomarkers_for_acquisition_id(
    acquisition_id: str = None, conn: Engine = None
) -> list:
    """Given an acquisition id, returns all available biomarkers

    Args:
        acquisition_id (str): acquisition id
        conn (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns
        list: list of biomarkers

    """


def query_cell_coords(
    acquisition_id: str = None, segmentation_version: int = None, conn: Engine = None
) -> pd.DataFrame:
    pass


def get_annotation_names(acquisition_id: str = None, conn: Engine = None) -> dict:
    pass


def get_story_id_from_study_id_and_title(study_id, title, conn):
    """
    Given a study_id, returns a story_id.

    Args:
        study_id: integer uniquely identifying a study.
        title: string uniquely (hopefully) identifying story within a study.
        conn: RDS sql_alchemy connection.

    Returns:
        An integer representing the story_id.
    """


def get_all_story_info_for_study_id(study_id, conn):
    """
    Given a study_id, returns a story_id.

    Args:
        study_id: integer uniquely identifying a study.
        title: string uniquely (hopefully) identifying story within a study.
        conn: RDS sql_alchemy connection.

    Returns:
        An integer representing the story_id.
    """


def get_note_id_from_story_id(story_id, conn):
    """
    Given a story_id, returns a list of note_ids.

    Args:
        story_id: integer uniquely identifying a story.
        conn: RDS sql_alchemy connection.

    Returns:
        A list of integers representing note_ids.
    """


def get_roi_ids_from_note_id(note_id, conn):
    """
    Given a note_id, returns all associated roi_ids.

    Args:
        note_id: integer uniquely identifying a note.
        conn: RDS sql_alchemy connection.

    Returns:
        A list of integers representing roi_ids.
    """


def get_roi_coord_from_roi_id(roi_id, conn):
    """
    Given a roi_id, returns roi coordinates.

    Args:
        roi_id: integer uniquely identifying an ROI.
        conn: RDS sql_alchemy connection.

    Returns:
        A dataframe with columns 'X' and 'Y'.
    """


def get_image_dimensions_for_roi_id(roi_id, conn):
    """
    Given a roi_id, returns image dimensions.

    Args:
        roi_id: integer uniquely identifying an ROI.
        conn: RDS sql_alchemy connection.

    Returns:
        A dataframe with columns 'height' and 'width'.
    """


def get_acq_id_from_roi_id(roi_id, conn):
    """
    Given a roi_id, returns associated acquisition_id.

    Args:
        roi_id: integer uniquely identifying an ROI.
        conn: RDS sql_alchemy connection.

    Returns:
        An integer representing the acquisition_id.
    """


def get_channel_im(
    acquisition_id, biomarker, channel=None, cur=None, b3=connect_boto3(), resolution=0
):
    """Given an acquisition_id and biomarker_name, returns a slice of the
    image resolution defaults to highest value, but can be set lower. user
    needs to know how low the resolution gets resolution is scaled 2^n

    Args:
        acquisition_id (str): acquisition id
        biomarker (str): name for the biomarker
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector
        b3 (boto3.resources.factory.s3.ServiceResource, optional): aws connector
        resolution (int, optional): zoom-out level, 0 - full resolution, 1 - 2x, etc.

    Returns:
        array-like: 2D array of shape (height, width)

    """


def get_image_channel_for_biomarker_acquisition_id(
    acq_id, biomarker, conn, return_all=False
):
    """Given an acquisition id (CODEX assay), and a biomarker name,
    returns the image channel

    Args:
        acq_id (str): acquisition id
        biomarker (str): name for the biomarker
        conn (SnowflakeConnection/sqlalchemy.engine): snowflake/postgres connector
        return_all (bool, optional): if to print all available image channels

    Returns:
        int: image channel index
    """


def get_vizuuid_for_acquisition_id(acquisition_id, conn):
    """Given an acquisition id, returns a civ-prod uuid

    Args:
        acquisition_id (str): acquisition id
        conn (SnowflakeConnection/sqlalchemy.engine): snowflake/postgres connector

    Returns
        uuid (str): base image uuid
    """


def get_channel_cycle_for_biomarker_acquisition_id(
    acquisition_id, biomarker, conn, return_all=False
):
    """Given an acquisition id and a biomarker name,
    returns the channel and cycle number

    Args:
        acq_id (str): acquisition id
        biomarker (str): name for the biomarker
        conn (SnowflakeConnection/sqlalchemy.engine): snowflake/postgres connector
        return_all (bool, optional): if to print all channel/cycle hits

    Returns:
        tuple: (channel, cycle)
    """


def get_assay_name_for_acquisition_id(acquisition_id, conn):
    """Given an acquisition id, returns the assay name

    Args:
        acq_id (str): acquisition id
        conn (SnowflakeConnection/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        str: assay name
    """


def get_phenocycler_channel_cycle_for_biomarker_acquisition_id(
    acq_id, biomarker, conn, return_all=False
):
    """Given an acquisition id (PhenoCycler assay), and a biomarker name,
    returns the channel number (cycle default to 1)

    Args:
        acq_id (str): acquisition id
        biomarker (str): name for the biomarker
        conn (SnowflakeConnection/sqlalchemy.engine): snowflake/postgres connector
        return_all (bool, optional): if to print all channel/cycle hits

    Returns:
        tuple: (channel, 1)
    """


def get_codex_channel_cycle_for_biomarker_acquisition_id(
    acquisition_id, biomarker, conn
):
    """Given an acquisition id, and a biomarker name, returns the channel
    and cycle nunmber

    Args:
        acq_id (str): acquisition id
        biomarker (str): name for the biomarker
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        pd.DataFrame: (channel, cycle)

    """


def if_exists_viz_tile(uuid, x, y, c, level, b3):
    """Check if a specific tile exists

    Args:
        uuid (str): uuid for the region
        x (int): tile index (width dimension)
        y (int): tile index (height dimension)
        c (int): channel index
        level (int): zoom-out level, 0 - full resolution, 1 - 2x, etc.
        b3 (boto3.resources.factory.s3.ServiceResource): aws connector

    Returns:
        bool: True if this tile exists, False if not

    """


def get_image_dim_for_acquisition_id(acquisition_id, conn):
    """Given an acquisition id, returns size of the image in pixels

    Args:
        acquisition_id (str): acquisition id
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns
        tuple: (width, height)

    """


def get_x_y_tile_range_for_acqid_and_level(acq_id, resolution, cur):
    """Get range of x and y tiles for tiled images

    Args:
        acq_id (str): acquisition ID of the region
        resolution (int): zoom-out level, 0 - full resolution, 1 - 2x, etc.
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        tuple: max x, y tile id

    """


def get_viz_tile(uuid, x, y, c, level, b3):
    """Download a visualizer tile

    Args:
        uuid (str): uuid for the region
        x (int): tile index (width dimension)
        y (int): tile index (height dimension)
        c (int): channel index
        level (int): zoom-out level, 0 - full resolution, 1 - 2x, etc.
        b3 (boto3.resources.factory.s3.ServiceResource): aws connector

    Returns:
        array-like: tile image

    """


def get_study_uuid_for_study_id(study_id, conn):
    """Given an study id, returns the s3 study uuid

    Args:
        study_id (int): study id
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        uuid (str): study uuid
    """


def get_segmentation_version_from_biomarker_expression_version(
    bm_version, acquisition_id, conn
):
    """Given a biomarker expression version and an acquisition id,
    returns the segmentation version.

    Note that segmentation version and biomarker expression version are not
    unique across the platform, but are unique within a study

    Args:
        bm_version (int): biomarker expression version
        acquisition_id (str): acquisition id, note that this argument is necessary
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        int: segmentation version

    """


def get_biomarker_version_from_segmentation_version(seg_version, acquisition_id, conn):
    """Given a biomarker expression version and an acquisition id,
    returns the segmentation version.

    Note that segmentation version and biomarker expression version are not
    unique across the platform, but are unique within a study

    Args:
        seg_version (int): biomarker expression version
        acquisition_id (str): acquisition id, note that this argument is necessary
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        int: segmentation version

    """


def get_segmentation_version_from_annotation_id(annotation_id, acquisition_id, conn):
    """Given an annotation id, returns the segmentation version.

    Note that segmentation version is not unique across the platform,
    but is unique within a study

    Args:
        annotation_id (int): annotation id
        acquisition_id (str): acquisition id, note that this argument is not
            needed for the query, keeping it for backward compatibility
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        int: segmentation version

    """


def get_biomarker_expression_version_from_annotation_id(
    annotation_id, acquisition_id, conn
):
    """Given an annotation id, returns the biomarker expression version.

    Note that biomarker expression version is not unique across the platform,
    but is unique within a study

    Args:
        annotation_id (int): annotation id
        acquisition_id (str): acquisition id, note that this argument is not
            needed for the query, keeping it for backward compatibility
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        int: biomarker expression version

    """


def get_seg_mask(
    acquisition_id,
    segmentation_version=None,
    biomarker_version=None,
    annotation_id=None,
    cur=connect_rds(),
    b3=connect_boto3(),
    mask="nucleus",
):
    """
    Downloads the segmentation mask for an acquisition

    Args:
        acquisition_id (str): acquisition id to use
        segmentation_version (int, optional): sgementation version to use
        biomarker_expression_version (int, optional): biomarker expression version to use
        annotation_id (int, optional): annotation id to use
        cur (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector
        b3 (boto3.resources.factory.s3.ServiceResource, optional): aws connector
        mask (str, optional): 'nucleus' for nucleus mask, 'cell' for whole-cell mask

    Returns:
        array-like: integer-valued segmentation mask.  elements with value
        0 correspond to background, while positive integers identify cells.
    """


def get_roi_df_for_acquisition_id(
    acquisition_id: str = None, conn=None
) -> pd.DataFrame:
    pass


def get_biomarker_and_segmentation_versions_for_study_acquisitions(study_id, conn):
    """Given a study id, returns a dataframe with the biomarker expression
    version and segmentation version for each acquisition in the study

    Args:
        study_id (int): study id
        conn (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        pd.DataFrame: dataframe with the biomarker expression version and
        segmentation version for each acquisition in the study

    """


def get_all_metadata_for_acquisition_id(
    acquisition_id: Union[list, str] = None, conn=None
):
    """Given an acquisition id, returns a dataframe with all metadata for the acquisition

    Args:
        acquisition_id (str, list): acquisition id
        conn (SnowflakeCursor/sqlalchemy.engine): snowflake/postgres connector

    Returns:
        pd.DataFrame: dataframe with all metadata for the acquisition

    """
