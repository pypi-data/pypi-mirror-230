from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')  # noqa

# get version
exec(open('emobject/version.py').read())


setup(
    name='emobject',
    version=__version__,  # noqa
    description='data abstraction and libraries for spatial omics',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/enable-medicine/rnd-subgroup/emobject/',
    author="Ethan A. G. Baker",
    author_email='ethan.baker@enablemedicine.com',
    packages=find_packages(),
    python_requires='>=3.7, <4',

    install_requires=[
        "numpy",
        "jupyter",
        "pandas",
        "zarr",
        "matplotlib",
        "scipy",
        "scikit-image",
        "zstandard",
        "python-dotenv",
        "networkx",
        "anndata",
        "opencv-python",
        "pyyaml",
        "ome-types",
        "tifffile",
        "opencv-python-headless",
        "openpyxl",
        "seaborn",
        "requests",
        "boto3",
        "emoaccess >= 0.2.1",
    ],
    extras_require={
        'dev': [
            "pdoc3",
            'flake8',
            'pytest',
        ],
    },
)
