from emobject import emobject as emo
from emobject.emlayer import BaseLayer
from emobject.errors import EMObjectException
from emobject.core import save
import emobject.emimage as emi

from scipy import sparse
import pandas as pd
from anndata import AnnData
from typing import Optional
from lxml import etree

# from glob import glob
import os
import json
import zipfile
from pathlib import Path
import numpy as np
from ome_types import from_xml
import ome_types
import codecs
import re
import base64


def to_anndata(E: emo.EMObject) -> AnnData:
    """Converts an EMObject to an anndata object.

    Args:
        E : EMObject to convert
    """
    try:
        import anndata as ad
    except ImportError:
        raise EMObjectException("anndata not installed")

    adata = ad.AnnData(X=E.data)
    # make obs axis string
    temp_obs = E.obs.copy()
    temp_obs.index = temp_obs.index.astype(str)
    adata.obs = temp_obs
    adata.var = E.var

    if E.meta is not None:
        # convert df to dict
        adata.uns = E.meta.to_dict()

    return adata


def from_anndata(
    adata: AnnData,
    dtype=int,
    include_uns: Optional[bool] = False,
    name: Optional[str] = None,
    assay: Optional[str] = "visium",
) -> emo.EMObject:
    """Converts an anndata object to an EMObject.

    Args:
        adata : anndata object to convert
    """

    new_idx = [j for j in range(1, adata.shape[0] + 1)]

    if type(adata.X) == sparse._csr.csr_matrix:
        df = pd.DataFrame(adata.X.todense(), dtype=dtype)
    else:
        df = pd.DataFrame(adata.X, dtype=dtype)

    # see if there's position data
    try:
        pos = adata.obsm["spatial"]
        pos = pd.DataFrame(pos, dtype=dtype, index=new_idx)

    except KeyError:
        pos = None

    if include_uns:
        meta = adata.uns
    else:
        meta = None

    obs = adata.obs
    obs.index = new_idx

    E = emo.EMObject(
        data=df, obs=obs, var=adata.var, meta=meta, pos=pos, name=name, assay=assay
    )
    return E


def layer_from_anndata(
    adata: AnnData,
    dtype=int,
    include_uns: Optional[bool] = False,
    name: str = None,
    assay: Optional[str] = "visium",
    spot_size: Optional[float] = None,
    scale_factor: Optional[float] = None,
) -> emo.EMObject:
    """Converts an anndata object to an EMObject.

    Args:
        adata : anndata object to convert
    """
    new_idx = [j for j in range(1, adata.shape[0] + 1)]
    #  old_idx = adata.obs.index

    if type(adata.X) == sparse._csr.csr_matrix:
        df = pd.DataFrame(adata.X.todense(), dtype=dtype)
    else:
        df = pd.DataFrame(adata.X, dtype=dtype, index=new_idx)

    # see if there's position data
    try:
        pos = adata.obsm["spatial"]
        pos = pd.DataFrame(pos, dtype=dtype, index=new_idx)
        # pos.index = new_idx

    except KeyError:
        pos = None

    if name is None:
        raise EMObjectException("Must provide a name for the layer")

    obs = adata.obs
    obs.index = new_idx

    return BaseLayer(
        data=df,
        obs=obs,
        var=adata.var,
        pos=pos,
        name=name,
        assay=assay,
        spot_size=spot_size,
        scale_factor=scale_factor,
    )


def from_10x_visium(path: str, name: Optional[str] = None) -> emo.EMObject:
    """Converts a 10x Visium directory to an EMObject.

    Args:
        path : path to 10x Visium directory
    """

    assert os.path.exists(path), f"Path {path} does not exist."
    # TODO: Parse visium directory


def object_from_files(
    data: str,
    obs: str,
    var: str,
    meta: Optional[str] = None,
    pos: Optional[str] = None,
    name: Optional[str] = None,
    assay: Optional[str] = None,
    delimiter: Optional[str] = ",",
) -> emo.EMObject:
    """Converts files to an EMObject.

    Args:
        data : path to data file
        obs : path to obs file
        var : path to var file
        meta : path to meta file
        pos : path to pos file
        name : name of the EMObject
        assay : assay type
    """

    data = pd.read_csv(data, index_col=0, delimiter=delimiter)
    obs = pd.read_csv(obs, index_col=0, delimiter=delimiter)
    var = pd.read_csv(var, index_col=0, delimiter=delimiter)

    if meta is not None:
        meta = pd.read_csv(meta, index_col=0, delimiter=delimiter)
    else:
        meta = None

    if pos is not None:
        pos = pd.read_csv(pos, index_col=0, delimiter=delimiter)
    else:
        pos = None

    E = emo.EMObject(
        data=data, obs=obs, var=var, meta=meta, pos=pos, name=name, assay=assay
    )
    return E


def layer_from_files(
    data: str,
    obs: str,
    var: str,
    pos: Optional[str] = None,
    name: Optional[str] = None,
    assay: Optional[str] = None,
    delimiter: Optional[str] = ",",
    spot_size: Optional[float] = None,
    scale_factor: Optional[float] = None,
) -> BaseLayer:
    """Converts files to an EMObject.

    Args:
        data : path to data file
        obs : path to obs file
        var : path to var file
        meta : path to meta file
        pos : path to pos file
        name : name of the layer
        assay : assay type
    """

    data = pd.read_csv(data, index_col=0, delimiter=delimiter)
    obs = pd.read_csv(obs, index_col=0, delimiter=delimiter)
    var = pd.read_csv(var, index_col=0, delimiter=delimiter)

    if pos is not None:
        pos = pd.read_csv(pos, index_col=0, delimiter=delimiter)
    else:
        pos = None

    return BaseLayer(
        data=data,
        obs=obs,
        var=var,
        pos=pos,
        name=name,
        assay=assay,
        spot_size=None,
        scale_factor=None,
    )


def from_geomx(workflow_directory, image_directory, save_directory):
    """
    Parse Nanostring GeoMX data into emObject, including DCC files, PKC
    files, OME-XML metadata (ROIs), and images.

    Args:
        workflow_directory (str): The path of the directory containing the
        GeoMX data outputs (often referred to as 'workflow' files).
        image_directory (str): The path of the directory containing GeoMX
        image data
        save_directory (str): The path of the directory where Zarr data will
        be stored.

    Returns:
        A list of emObjects
    """
    # From top level 'Workflow' directory, find DCC directory
    dcc_dir = __find_dirs_with_ext(workflow_directory, ".dcc")

    # Find PKC file
    pkc_files = __find_files_with_ext(workflow_directory, ".pkc")
    pkc_files = [
        file for file in pkc_files if not os.path.basename(file).startswith(".")
    ]

    # Find XML files
    xml_paths = __find_files_with_ext(image_directory, ".xml")
    xml_fnames = [os.path.basename(x) for x in xml_paths]
    xml_names = [x.split(".", 1)[0] for x in xml_fnames]

    # Check for duplicates
    assert len(dcc_dir) == 1, "More than one DCC directory found"
    assert len(pkc_files) == 1, "More than one .PKC file found in directory"

    # Parse files:
    annos = _read_region_annotations(workflow_directory)
    segments = _read_segment_properties(workflow_directory)
    obs = pd.merge(annos, segments, how="left")
    mat = _create_counts_matrix(dcc_dir=dcc_dir[0], pkc_file=pkc_files[0])
    mat.reindex(obs.index)

    # Load images and create emObjects
    image_file_names = set(xml_names) & set(obs["SlideName"])
    xml_file_paths = [
        os.path.join(image_directory, "".join([x, ".ome.xml"]))
        for x in image_file_names
    ]
    img_file_paths = [
        os.path.join(image_directory, "".join([x, ".ome.tiff"]))
        for x in image_file_names
    ]

    zarr_paths = []
    for name, path, img_path in zip(image_file_names, xml_file_paths, img_file_paths):
        combined_mask, mask_inds, mask_positions, dims = _extract_rois_from_xml(path)
        these_obs = obs[obs["SlideName"].isin([name])]
        this_mat = mat[mat.index.isin(these_obs["Sample_ID"])]
        # position_dict = {m: mask_positions[i] for i, m in enumerate(mask_inds)}

        M = emi.EMMask(
            masks=combined_mask,
            mask_idx=np.array([name]),
            # dims=dims,
            # pos=position_dict,
            to_disk=True,
        )

        E = emo.EMObject(
            data=this_mat,
            obs=these_obs,
            var=None,
            pos=mask_positions,
            mask=M,
            img=None,
            meta=None,
            name=name,
        )

        save(E, out_dir=save_directory, name=name)
        zarr_path = zarr_path = os.path.join(save_directory, name + ".zarr")

        zarr_paths.append(zarr_path)

    return zarr_paths


def combine_masks(mask_list, xy, W, H):
    """
    Combine multiple binary masks into a single 2D array.

    Each mask in mask_list is represented by a tuple: (top_left_x, top_left_y, mask_array),
    where mask_array is a 2D 1-bit numpy array of known width and height.

    max_x and max_y are the dimensions of the final combined mask.
    """

    # Coerce ints
    W = int(W)
    H = int(H)

    # Create an empty 2D numpy array of the required dimensions
    combined_mask = np.zeros((H, W), dtype=int)

    # Iterate over each mask, adding its values into the combined mask
    for i, mask in enumerate(mask_list, start=1):
        i1 = i - 1
        x1 = xy[i1][0]
        y1 = xy[i1][1]
        combined_mask[y1 : y1 + mask.shape[0], x1 : x1 + mask.shape[1]] += i * mask

    return combined_mask


def _init_EMMask_from_dict(mask_dictionary):
    first_key = next(iter(mask_dictionary))
    first_mask = mask_dictionary[first_key]
    M = emi.EMMask(masks=first_mask, mask_idx=first_key, to_disk=True)
    return M


def _add_mask_from_dict(mask_dictionary: dict = None, M: emi.EMMask = None):
    for i, m in enumerate(mask_dictionary.keys()):
        print(m)
        if m in M.mask_names:
            continue
        M.add_mask(mask=mask_dictionary[m], mask_name=m)
    return M


def _extract_rois_from_xml(xml_fpath, validate=False):
    """
    Ingests an OME-XML (or XML) file as a path, parses the file, then extracts
    ROI/AOIs as binary masks. This function uses the ome-types library to parse
    XML and to model the different data structures needed.

    Binary base64 data from the BinData model are extracted and bit unpacked
    into a 1-bit binary 2D numpy array.

    Args:
        xml_fpath: A string defining the XML file path
        validate: A logical, defining whether or not the ome-types library
            should perform XML validation on input. Not recommended, since
            GeoMX outputs may contain non standard metadata.

    Returns:
        A tuple of two dictionaries. The first dictionary contains the binary
        ROI masks, the second contains the centroid of the ROI. The dictionary
        keys are a comma-separated string of the 'ROI' and column of the GeoMX annotation input.
    """

    # parse ome-xml
    try:
        types = from_xml(xml_fpath, validate=validate, parser="lxml")
    except etree.XMLSyntaxError:
        __clean_xml_file(xml_fpath, xml_fpath)
        types = from_xml(xml_fpath, validate=validate, parser="lxml")

    # retrieve full image dimensions
    pixels_dict = dict(dict(types.images[0])["pixels"])
    X = pixels_dict["size_x"]
    Y = pixels_dict["size_y"]

    # retrieve image name (slide name)
    slide_name = dict(dict(types)["images"][0])["name"]

    # extract rois
    rois = types.rois

    masks = {}
    mask_inds = []
    mask_positions = []

    for i in range(len(rois)):
        roi = rois[i]
        # get ID information
        roi_dict = dict(roi)
        roi_id = int(roi_dict["id"].split(":")[1]) + 1
        roi_id_str = f"{roi_id:0>3}"

        union = roi_dict["union"]

        # get mask information
        models = [dict(u) for u in union if isinstance(u, ome_types.model.mask.Mask)]

        for mask in models:
            mask_id_str = mask["text"]
            mh = mask["height"]
            mw = mask["width"]
            mx = mask["x"]
            my = mask["y"]

            dict_key = " | ".join([slide_name, roi_id_str, mask_id_str])

            bin_mask = _read_bindata_mask(
                dict(mask["bin_data"])["value"], width=mw, height=mh
            )

            masks[dict_key] = bin_mask
            mask_inds.append(dict_key)
            mask_positions.append(np.array([mx, my], dtype=int))

    mask_position_array = np.vstack(mask_positions)

    dims = (X, Y)
    combined_mask = combine_masks(masks.values(), mask_position_array, X, Y)
    return combined_mask, mask_inds, mask_position_array, dims


def _read_bindata_mask(base64_data, width, height):
    width = int(width)
    height = int(height)
    # Decode the base64 data
    decoded_data = base64.b64decode(base64_data)

    # Convert the binary data to a NumPy array of 8-bit unsigned integers (0-255)
    data_array = np.frombuffer(decoded_data, dtype=np.uint8)

    # Unpack bits to 1-bit binary
    np_array = np.unpackbits(data_array)

    # Reshape the 1D array into a 2D array based on the dimensions of the image
    mask = np_array[0 : height * width].reshape((height, width))

    return mask


def __combine_rows_by_index(df, indices_to_combine, new_index):
    """
    Combine specified rows in a pandas DataFrame by summing column values.

    Args:
        df (DataFrame): pandas DataFrame
        indices_to_combine (list): list of indices to combine
        new_index (str): new index for the combined row
    Returns:
        pandas DataFrame with combined rows
    """

    # Create a mapping from old index to new index
    index_mapping = {
        idx: new_index if idx in indices_to_combine else idx for idx in df.index
    }

    # Set the new index
    df.index = df.index.to_series().map(index_mapping)

    # Group by the new index and sum
    df = df.groupby(df.index).sum()

    return df


def __find_dirs_with_ext(top_dir, ext):
    dirs_with_ext = set()

    for root, dirs, files in os.walk(top_dir):
        for file in files:
            if file.lower().endswith(ext.lower()):
                dirs_with_ext.add(root)

    return list(dirs_with_ext)


def __find_files_with_ext(top_dir, ext):
    files_with_ext = []

    for root, dirs, files in os.walk(top_dir):
        for file in files:
            if file.lower().endswith(ext.lower()):
                files_with_ext.append(os.path.join(root, file))

    return files_with_ext


def _parse_dcc(file_path):
    """
    Parse a DCC (Digital Cancer Capture) file into a nested dictionary
    structure.

    The DCC file format is used by NanoString Technologies for their nCounter
    and GeoMx platforms.  The file contains sections with key-value pairs
    separated by commas. Each section starts with a tag in the format
    <SectionName> and ends with a tag in the format </SectionName>.

    Example DCC file content:

    <Header>
    FileVersion,0.02
    SoftwareVersion,"GeoMx_NGS_Pipeline_2.3.4"
    Date,2021-5-20
    </Header>

    <Scan_Attributes>
    ID,DSP-1005330000011-D-A01
    Plate_ID,1005330000011
    Well,A01
    </Scan_Attributes>

    Args:
        file_path (str): The path of the DCC file to parse.

    Returns:
        dict: A nested dictionary representing the DCC file content, where the
        outer dictionary keys are section names, and the inner dictionaries
        contain the key-value pairs within each section.

    Example usage:

    dcc_file_path = 'example.dcc'
    parsed_dcc = _parse_dcc(dcc_file_path)
    print(parsed_dcc)

    Output:

    {
        'Header': {
            'FileVersion': '0.02',
            'SoftwareVersion': '"GeoMx_NGS_Pipeline_2.3.4"',
            'Date': '2021-5-20'
        },
        'Scan_Attributes': {
            'ID': 'DSP-1005330000011-D-A01',
            'Plate_ID': '1005330000011',
            'Well': 'A01'
        }
    }
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    dcc_dict = {}
    current_section = None

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Start a new section
        if line.startswith("<") and not line.startswith("</") and line.endswith(">"):
            section_name = line[1:-1]
            current_section = section_name
            dcc_dict[current_section] = {}

        # Close the current section
        elif line.startswith("</") and line.endswith(">"):
            current_section = None

        # Process key-value pairs within the current section
        elif current_section is not None:
            key, value = line.split(",", 1)
            dcc_dict[current_section][key] = value

    return dcc_dict


def _parse_pkc(file_path):
    """
    Parse a PKC (Probe Key Collection) file and extract the RTS_ID to gene
    name mapping.

    The PKC file is a JSON-formatted file containing information about probes
    and their associated genes. This function extracts the 'RTS_ID' and gene
    name from the PKC file and returns a dictionary where the RTS_ID is the
    key, and the gene name is the value.

    Args:
        file_path (str): The path of the PKC file to parse.

    Returns:
        dict: A dictionary containing the RTS_ID to gene name mapping, where
        the RTS_ID is the key, and the gene name is the value.

    Example usage:

    pkc_file_path = 'example.pkc'
    parsed_pkc = parse_pkc(pkc_file_path)
    print(parsed_pkc)

    Output (example):

    {
        'RTS0021170': 'GOLPH3L',
        'RTS0021193': 'ACTB',
        ...
    }
    """
    # Parse PKC as JSON (same format)
    with open(file_path, "r") as file:
        data = json.load(file)

    # Initialize dictionary
    mapping = dict()

    # Extract RTS ID - Gene name mapping
    for target in data["Targets"]:
        rts = target["Probes"][0]["RTS_ID"]
        gene = target["Probes"][0]["DisplayName"].split("_")[0]
        mapping[rts] = gene

    return mapping


def _read_dcc_files(directory, counts_key="Code_Summary"):
    """
    Read and parse .dcc files in a directory, unzip .zip files if necessary.

    Given a directory name, this function checks for .dcc and .zip files.
    If only .zip files are found, it unzips them. If both .zip and .dcc files
    are found, it assumes unzipping has already occurred. If no .dcc files are
    found, even after unzipping, the function raises an error.

    Args:
        directory (str): The directory path containing .dcc and/or .zip files.
        counts_key (str): The name of the key from `_parse_dcc` output that contains counts data.

    Returns:
        dict: A dictionary with .dcc file basenames as keys and _parse_dcc output
              as values.

    Raises:
        FileNotFoundError: If no .dcc files are found in the directory.
    """
    dcc_files = list(Path(directory).glob("*.dcc"))
    zip_files = list(Path(directory).glob("*.zip"))

    # Unzip .zip files if necessary
    if not dcc_files and zip_files:
        for zip_file in zip_files:
            with zipfile.ZipFile(zip_file, "r") as zf:
                zf.extractall(directory)
        dcc_files = list(Path(directory).glob("*.dcc"))

    # Check for .dcc files
    if not dcc_files:
        raise FileNotFoundError("No .dcc files found in the directory.")

    # Read and parse .dcc files
    parsed_files = {}
    for dcc_file in dcc_files:
        basename = dcc_file.stem
        parsed_files[basename] = _parse_dcc(dcc_file)[counts_key]

    df = pd.DataFrame.from_dict(parsed_files, orient="index").fillna(0)

    return df


def _create_counts_matrix(dcc_dir, pkc_file, counts_key="Code_Summary"):
    """
    Create a counts matrix from GeoMx data output: DCC and PKC files.

    Args:
        dcc_dir (str): A directory to search for DCC files in
        pkc_file (str): A path to the PKC file

    Returns:
        pd.DataFrame: The cleaned data inputs as a pandas DataFrame

    """

    dcc = _read_dcc_files(dcc_dir, counts_key=counts_key)
    mapping = _parse_pkc(pkc_file)
    dcc.rename(columns=mapping, inplace=True)
    return dcc


def _read_region_annotations(
    directory,
    file_name_pattern="LabWorksheet",
    file_extension=".txt",
    text_matching_pattern="Annotations",
):
    """
    Read files matching a file name pattern and extension, and parse data
    following a text matching pattern into a pandas DataFrame. If multiple
    matching files are found, concatenate the data by rows.

    Args:
        directory (str): The directory path to search for files.
        file_name_pattern (str): The file name pattern to match.
        file_extension (str): The file extension to match.
        text_matching_pattern (str): The text pattern to search for in the file.

    Returns:
        pd.DataFrame: The parsed data as a pandas DataFrame.

    Raises:
        FileNotFoundError: If no matching files are found.
    """

    search_pattern = f"*{file_name_pattern}*{file_extension}"
    matching_files = list(Path(directory).rglob(search_pattern))

    if not matching_files:
        raise FileNotFoundError(
            f"No files matching the pattern {search_pattern} were found."
        )

    dataframes = []

    for file in matching_files:
        with open(file, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if text_matching_pattern in line:
                    # Read the file into a DataFrame starting from the next line
                    df = pd.read_csv(file, sep="\t", skiprows=i + 1)
                    dataframes.append(df)
                    break

    if not dataframes:
        raise ValueError(
            f"No matching text pattern '{text_matching_pattern}' found in the matching files."
        )

    # Concatenate DataFrames by rows
    combined_df = pd.concat(dataframes, axis=0, ignore_index=True, sort=False)

    # Clean ROI column
    combined_df["ROI"] = combined_df["roi"].str.extract(r"(\d+)")

    return combined_df


def _read_segment_properties(
    directory, file_name_pattern="Export1", sheet_name="SegmentProperties"
):
    search_pattern = f"{file_name_pattern}*.xlsx"
    matching_files = list(Path(directory).rglob(search_pattern))

    seg_properties = pd.read_excel(matching_files[0], sheet_name=sheet_name)

    seg_properties[["slide name", "ROI", "segment"]] = seg_properties[
        "SegmentDisplayName"
    ].str.split(
        " \| ", expand=True  # noqa: W605
    )

    return seg_properties


def __clean_xml_file(input_filename, output_filename):
    # Open the file using codecs to ensure correct encoding handling
    with codecs.open(input_filename, "r", encoding="utf-8", errors="replace") as file:
        content = file.read()

    # Using regex to find non-UTF-8 characters and replace them
    content = re.sub(r"[^\x00-\x7F]+", "\u00b5", content)

    # Writing the cleaned content to a new file
    with codecs.open(output_filename, "w", encoding="utf-8") as file:
        file.write(content)


def __get_rectangle_corners(x, y, width, height):
    top_left = (x, y)
    top_right = (x + width, y)
    bottom_left = (x, y + height)
    bottom_right = (x + width, y + height)
    return np.array([top_left, top_right, bottom_left, bottom_right])


def __aggregate_columns(column):
    if np.issubdtype(column.dtype, np.number):
        return column.sum()
    elif np.issubdtype(column.dtype, np.object):
        return ",".join(column.unique())
    elif np.issubdtype(column.dtype, np.bool):
        return column.any()
    else:
        return column.iloc[0]
