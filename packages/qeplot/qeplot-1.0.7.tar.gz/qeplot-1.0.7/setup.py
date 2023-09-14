from distutils.core import setup
from setuptools import find_packages
import json
from pathlib import Path
from typing import Optional

setup(
    name = "qeplot",
    version = "1.0.7",
    description = "VASProcar is an open-source package written in the Python 3 programming language, which aims to provide an intuitive tool for the post-processing of the output files produced by the DFT VASP code, through an interactive user interface.",
    author = "Augusto de Lelis Araujo and Renan da Paixao Maciel", 
    author_email = "augusto-lelis@outlook.com, renan.maciel@physics.uu.se",
    url = "https://doi.org/10.5281/zenodo.6343960",
    download_url = "https://doi.org/10.5281/zenodo.6343960",
    license = "GNU GPLv3",
    install_requires=['numpy','scipy','matplotlib','plotly','moviepy','kaleido'],
    package_data={"": ['*.dat', '*.png', '*.jpg']},
)

# python3 -m pip install --upgrade twine

# python setup.py sdist
# python3 -m twine upload dist/*