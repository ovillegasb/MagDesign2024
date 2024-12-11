# Installing PyXtal

## The environment

Version python used is `3.11.10`, pip version is `24.3.1`.

```
python -m venv PyXtal --copies --prompt PyXtal

export PYTHONUSERBASE=/new/path/PyXtal >> PyXtal/bin/activate
export PYTHONNOUSERSITE=1 >> PyXtal/bin/activate

source PyXtal/bin/activate
```

## Install dependencies

```
pip install pyxtal
pip install func_timeout
```

## Testing PyXtal

### Run PyXtal executables

Currently, we provide several utilities to the users so that they can run the code from command line with Python scripting. They include:

- `Pyxtal_main.py`: a tool to generate atomic/molecular crystals

- `Pyxtal_symmetry.py`: a tool to access the symmetry information


```shell
pyxtal_main.py -h
```

### A quick example of C60

```shell
pyxtal_main.py -e C -n 60 -d 0 -s Ih
```

### 3D crystals

```shell
pyxtal_main.py -e C -n 8 -s 227
```

### 2D and 1D crystals

```sh
pyxtal_main.py -e Mo,S -n 1,2 -s 77 -d 2 -t 2.4
```

### Molecular crystal from database

```sh
pyxtal_main.py -m -e ROY -n 4 -s 19
```

## Specifying molecules outside the database

```sh
GencrysMol.py -h

GencrysMol.py H2O.xyz

GencrysMol.py H2O.xyz Na.xyz -n_struct 10 -ratio 6:1

GencrysMol.py CO3.xyz -atom Ca -n_struct 10 --parallel

GencrysMol.py CO3.xyz -atom Na -n_struct 20 -ratio 1:2 -z_value 5 --parallel

# GencrysMol.py CO3.xyz -n_struct 10 -atom Ca -atom_oxidation 2
```

