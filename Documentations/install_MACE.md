# Installing MACE

## The environment

Version python used is `3.11.10`, pip version is `24.3.1`.

```sh
python -m venv MACE --copies --prompt MACE

# Modify the activation file
# export PYTHONUSERBASE=/new/path/MACE >> MACE/bin/activate
# export PYTHONNOUSERSITE=1 >> MACE/bin/activate

source MACE/bin/activate
```

## Install dependencies

```sh
pip install torch torchvision torchaudio
pip install mace-torch
pip install torch-dftd
pip install func_timeout
pip install spglib==2.4.0
pip install pymatgen
pip install mp-api
pip install ase
```