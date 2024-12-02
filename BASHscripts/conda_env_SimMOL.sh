#!/bin/bash

# Creation and configuration of the SimMOL working environment in Anaconda/Miniconda.
# The uncommented packages are the base configuration.

# Enviroment SimMOL
conda create --name SimMOL
conda activate SimMOL
conda config --add channels conda-forge

# Basic modules
conda install anaconda:pip
conda install anaconda::numpy
conda install anaconda::pandas
conda install anaconda::scipy
conda install -c conda-forge matplotlib
conda install anaconda::seaborn
conda install anaconda::networkx
conda install -c conda-forge func_timeout
conda install -c conda-forge memory_profiler

# For notebooks
conda install -c conda-forge jupyterlab
conda install -c conda-forge jupyter_contrib_nbextensions
conda install -c conda-forge jupyter-resource-usage
## conda install -c conda-forge widgetsnbextension
## conda install -c conda-forge jupyter-lsp


# Useful modules
conda install conda-forge::statsmodels
conda install -c conda-forge pymatgen
conda install conda-forge::mdtraj
# conda install conda-forge::mdanalysis
# conda install conda-forge::rdkit
conda install conda-forge::ase
# conda install conda-forge::openbabel
conda install -c conda-forge spglib
pip install mp-api

# For MACE
# conda config --add channels conda-forge
# conda install pytorch
# conda install numpy scipy matplotlib ase opt_einsum prettytable pandas e3nn
# conda install func_timeout

# Lammps
# https://docs.lammps.org/Install_conda.html
# conda config --add channels conda-forge
# conda create -n my-lammps-env
# conda install lammps
# conda activate my-lammps-env
# conda install lammps


# Charges
# https://github.com/danieleongari/EQeq
# git clone https://github.com/danieleongari/EQeq.git
# cd EQeq
# g++ main.cpp -O3 -o eqeq
# Python binding
# g++ -c -fPIC main.cpp -O3 -o eqeq.o
# g++ -shared -Wl,-soname,libeqeq.so -O3 -o libeqeq.so eqeq.o
# export PYTHONPATH:/home/ovillegas/gitproyects/EQeq:$PYTHONPATH
# ln -s /home/ovillegas/gitproyects/EQeq/eqeq /home/ovillegas/.local/bin/eqeq

# DFTBplus
# https://dftbplus-recipes.readthedocs.io/en/latest/introduction.html
# conda install -n base conda-forge::mamba
# conda install 'dftbplus=*=mpi_mpich_*' -c conda-forge
# module load mpich
# mpirun -info


# For NGLview
pip install nglview
conda install anaconda::ipywidgets
## jupyter-nbextension enable --py --sys-prefix widgetsnbextension
## jupyter-nbextension enable --py --sys-prefix nglview

# Some jupyter commands
# https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/install.html
# jupyter --paths
# jupyter --config-dir
# jupyter-nbextension list
# jupyter-labextension update --all
# jupyter-labextension list

# Some conda commands
conda config --show [or channels]

# Some python modules
python -m site --user-site

# To remove
conda env remove --name SimMOL

# To remove using pip
pip freeze | xargs pip uninstall -y
