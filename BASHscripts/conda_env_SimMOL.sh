#!/bin/bash

# Creation and configuration of the SimMOL working environment in Anaconda.

# Enviroment SimMOL
conda create --name SimMOL
conda activate SimMOL
conda config --add channels conda-forge

# Basic modules
conda install anaconda::numpy
conda install anaconda::pandas
conda install anaconda::scipy
conda install conda-forge::matplotlib
conda install anaconda::seaborn

conda install conda-forge::notebook
conda install conda-forge::jupyter
conda install conda-forge::jupyterlab
conda install conda-forge::jupyter_contrib_nbextensions
conda install conda-forge::jupyter-lsp

# Useful modules
conda install anaconda::networkx
conda install conda-forge::statsmodels
conda install conda-forge::pymatgen # or -c conda-forge pymatgen
conda install conda-forge::mdtraj
conda install conda-forge::mdanalysis
conda install conda-forge::rdkit
conda install conda-forge::nglview
conda install conda-forge::ase

# Some jupyter commands
jupyter --paths
jupyter --config-dir

# Some conda commands
conda config --show [or channels]

# Some python modules
python -m site --user-site

# To remove
conda env remove --name SimMOL