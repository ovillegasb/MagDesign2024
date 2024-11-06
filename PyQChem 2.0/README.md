# PyQChem:Python modules for Quantum Chemistry
This Python application is made to **visualize** and **analyze** crisallographic structures by using as an input various types of files used in **quantum chemistry**.
What this application enables:
1. **visualization of molecule structure**.
2. **interactive plots**: structures are classified by their energy and index or group number in a scatter plot with clickable points to enable visualization and a zoom feature (for the energy/group number plot).
3. **read one file at a time:**\
                            1. **cif,xyz and vasp:** can only be visualized.\
                            2. **res:** can generate an energy/index plot.\
                            3. **gathered poscar file+USPEX file:** can generate an energy/generation plot.
5. **read multiple files contained in folder:**\
                                            1. **cif and vasp:** can only be visualized.\
                                            2. **xyz:** if the energy is mentionned in the file an energy/index plot can be generated.
