#!/bin/bash

# Creation and configuration of the SimMOL working environment in Anaconda.

# Enviroment SimMOL
conda create --name SimMOL
conda activate SimMOL
conda config --add channels conda-forge

# Basic modules
conda install anaconda:pip
conda install anaconda::numpy
conda install anaconda::pandas
conda install anaconda::scipy
conda install conda-forge::matplotlib
conda install anaconda::seaborn
conda install anaconda::networkx

# For notebooks
conda install -c conda-forge jupyterlab
conda install -c conda-forge jupyter_contrib_nbextensions
## conda install -c conda-forge notebook
## conda install -c conda-forge jupyter_contrib_nbextensions
## conda install -c conda-forge widgetsnbextension
## conda install -c conda-forge jupyter-lsp
## conda install conda-forge::jupyter
## conda install conda-forge::jupyterlab

# Useful modules
conda install conda-forge::statsmodels
conda install conda-forge::pymatgen # or -c conda-forge pymatgen
conda install conda-forge::mdtraj
conda install conda-forge::mdanalysis
conda install conda-forge::rdkit
conda install conda-forge::ase

# For NGLview
pip install nglview
conda install anaconda::ipywidgets
## jupyter-nbextension enable --py --sys-prefix widgetsnbextension
## jupyter-nbextension enable --py --sys-prefix nglview

# Some jupyter commands
# https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/install.html
jupyter --paths
jupyter --config-dir
jupyter-nbextension list
jupyter-labextension update --all
jupyter-labextension list
jupyter-labextension install @jupyterlab/celltags
jupyter-serverextension enable --py jupyterlab --sys-prefix

# Some conda commands
conda config --show [or channels]

# Some python modules
python -m site --user-site

# To remove
conda env remove --name SimMOL

# To remove using pip
pip freeze | xargs pip uninstall -y