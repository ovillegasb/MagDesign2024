# MagDesign2024

MagDesign2024 is a repository that records different tools, scripts and programs during my participation in this project in my Postdoc.

## Scripts included in `MagDesign2024` repertoire

### `./BASHscripts`

BASH script compilation, help to configure or automate some tasks.

- `conda_env_SimMOL.sh` Useful commands used to configure with SimMOL env conda.
- `jupyterLab_server.sh` Run jupyterlab in the system backgroud.

### `./PythonScripts`

Python script compilation.

- `MACE_relax.py`

- `DFTB+relax.py`

- `Download_struct_MP.py` Download any structure from MaterialProject from its molecular formula to a cif.

- `SymmetrizeStructures.py`

- `RemoveDuplicatesFilter.py`

- `Structural_filter.py`:

```
Structural_filter.py -i system_107_I4mm_Z_2_fIxRHfkP.cif --metal_center Ca -cutoff 2.8

```


### `./PyQChem-2.0`

Python application/module to visualize and classify inorganic structures.

- `Main.py` to run the application.
- `QChemPlot` functions to generate energy plots as a function of generation or index.
- `QChemView` functions to view chemical structures.
- `QChemFile` functions to process different file types used in quantum chemistry.
- `QChemNGL` functions to view chemical structures in an more enhanced way.
- `HoverObject` class that represents the hovering message we get when we fly over a button with the mouse cursor.