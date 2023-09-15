# emObject 

<img src="./docs/img/emObject_logo.png" alt="emobject logo" width="125"/> 

# What is emObject?

emObject is an abstraction for multimodal spatial omics data in Python. It’s inspired by other data abstractions and data science libraries like Seurat, but purpose-built for multiplexed imaging, spatial transcriptomics, and similar assays. emObject unlocks a seamless data science workflow between the core data types in a spatial dataset: matrix-format data, images, and masks -  via shared indexing and dedicated attributes to hold measurements, featurizations, and annotations on data across spatial scales.

As emObject evolves, we envision this data abstraction providing an expected and efficient format for science and engineering code and as a step towards closing the loop between code and no-code analysis on the Enable platform.

For more info about the design and motivation for emObject, see the manuscript [emObject: domain specific data abstraction for spatial omics](https://www.biorxiv.org/content/10.1101/2023.06.07.543950v1).

# What’s in an emObject?

emObject has dedicated attributes for all the common attributes we encounter in analyzing spatial data. A single emObject represents data at the acquisition level - future functionality is planned to represent experiments.

 Data attributes are aligned along several axes:

1. The observation axis - typically cells or visium spots
2. The variable axis - typically genes or biomarkers
3. The segment axis - unique, contiguous regions of ROI masks

## Layers

Layers are an additional axis within emObjects that stack the core data attributes - data, var, obs, sobs. This allows us to hold multiple versions - or multiple data modalities - within a single object. For example, we could have a raw and normalized data layer, or a layer for CODEX and a layer for H+E data. Annotations are kept within a layer since computations derived from the images may be affected by the numeric values in **data.** 

# What gets stored where?

- Biomarker expression -> **data**
- Notes about biomarkers -> **var**
- Featurization -> **obs**
- Spatial info -> **pos**
- Assignment of cells to segments -> **seg**
- Annotations on segment level -> **sobs**
- Unstructured info, whole image annotations -> **meta**

# Getting started

## Requirements

emObject requires Python 3.8 or higher and is tested on MacOS 13.2 (Ventura) and Ubuntu 18.04 and 22.04.

## Installation

To install emObject, clone this repo:

```
git clone https://gitlab.com/enable-medicine-public/emobject.git
```

and install: 

```
sudo python setup.py install
```

If you use `pipenv` as a package manager, you can install via:

```
pipenv install '-e .' --dev
```
from within the `emobject` repository. 

You can also install directly via PyPI:

```
pip install emobject
```

or, if you use `pipenv` (recommended):

```
pipenv install emobject
```

## Using emObject
See the `./notebooks` directory for tutorials to get started with emObject. The complete emObject documentation is available at [docs.enablemedicine.com](docs.enablemedicine.com).

## Using emMorphology extension
See the morphology extension package [here](https://gitlab.com/enable-medicine-public/emobject-morphology-extension).

# Citing emObject

If you use emObject in your work, please cite: 
```
@article{Baker2023.06.07.543950,
	author = {Ethan Alexander Garc{\'\i}a Baker and Meng-Yao Huang and Amy Lam and Maha K. Rahim and Matthew F. Bieniosek and Bobby Wang and Nancy R. Zhang and Aaron T Mayer and Alexandro E Trevino},
	journal = {bioRxiv},
	title = {emObject: domain specific data abstraction for spatial omics},
	year = {2023}}
```
# Contributing to emObject
We welcome community contributions. Contribution guide to come

# Licence
emObject is available under the MIT License.

**(c)** 2023 Enable Medicine, Inc. 

<img src="./docs/img/em_logo.png" alt="emobject logo" width="350"/> 
