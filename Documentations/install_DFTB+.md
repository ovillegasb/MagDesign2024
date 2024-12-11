# Installing DFTB+

```sh
source miniconda3/bin/activate
conda create --name DFTBplus
conda activate DFTBplus
conda install dftbplus=24.1=nompi_*
conda install ase
conda install func_timeout


# MPI
# module load intel/2023.2.1
# module load mpi
# conda install dftplus=24.1=mpi_openmpi_* -c conda-forge
# module load openmpi3/3.1.3

```
