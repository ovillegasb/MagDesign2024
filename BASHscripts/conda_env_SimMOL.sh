#!/bin/bash

# Creation and configuration of the SimMOL working environment in Anaconda.

# Enviroment SimMOL
conda create --name SimMOL scipy jupyterlab numpy matplotlib seaborn pandas
conda activate SimMOL
conda config --add channels conda-forge

# Useful modules
conda install pymatgen
conda install mdtraj
conda install mdanalysis
conda install networkx
conda install statsmodels
conda install rdkit