#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Symmetrizes and obtains primitive cell of a set of structures.

Create by Orlando Villegas - Jul 2024
"""

import glob
import os
import spglib
import time
import ase.io
from ase.data import chemical_symbols
import ase

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='ase.io.extxyz')


def symmetrize_structure(file, initial_symprec=1e-3, final_symprec=1e-5, output="symm_out"):
    """Read the structure."""
    atoms = ase.io.read(file)
    name = file.split("/")[-1].split(".")[0]

    # Convert the structure to a format compatible with spglib
    cell = (atoms.get_cell(), atoms.get_scaled_positions(), atoms.get_atomic_numbers())

    # spacegroup = spglib.get_spacegroup(cell, symprec=initial_symprec, symbol_type=0)
    # print("Spacegroup init:", spacegroup)

    # Standardize the cell to a conventional representation
    # This ensures the cell follows standard conventions based on symmetry
    standarized_cell = spglib.standardize_cell(cell, to_primitive=True, no_idealize=False, symprec=1e-3)

    # Refine the primitive cell
    # Adjust atomic positions and lattice vectors for consistency with symmetry operations
    refined_cell = spglib.refine_cell(standarized_cell, symprec=1e-3)

    # Search primitive cell
    prim_cell = spglib.find_primitive(refined_cell, symprec=1e-3, angle_tolerance=-1.0)

    spacegroup = spglib.get_spacegroup(prim_cell, symprec=initial_symprec, symbol_type=0)
    print("Spacegroup refined cell:", spacegroup)
    print(f"N atoms init: {len(atoms)}")

    # Create a new ASE Atoms object with the refined cell
    new_atoms = ase.Atoms(
        symbols=[chemical_symbols[Z] for Z in prim_cell[2]],  # Convert atomic numbers to symbols
        scaled_positions=prim_cell[1],                        # Use the scaled positions
        cell=prim_cell[0],                                    # Use the new cell
        pbc=True                                                 # Ensure periodic boundary conditions
    )
    print(f"N atoms end: {len(new_atoms)}")

    ase.io.write(f"{output}/{name}.cif", new_atoms, format="cif")


def main():
    """Run program."""
    start_time = time.time()

    print("Structural symmetrizer for MOF")
    print("------------------------------")

    file_types = "*.extxyz"
    print(f"\tFile types:              {file_types}")
    structures = glob.glob(file_types)
    n_structures = len(structures)
    print(f"\tTotal number of files:   {n_structures}")

    output_folder = "symm_out"
    print(f"\tOutput folder:           {output_folder}")
    try:
        os.mkdir(output_folder)
    except FileExistsError:
        pass

    n = len(structures)
    for i, struc in enumerate(structures, start=1):
        print("---------------------------------------------------")
        print("File:  %s  (%04d/%04d)" % (struc, i, n))
        print("---------------------------------------------------")
        print(struc)
        symmetrize_structure(struc, initial_symprec=1e-6, final_symprec=1e-6, output=output_folder)
        print("Done!")

    end_time = time.time()
    execution_time = end_time - start_time
    print("Done {:.3f}s".format(execution_time))


if __name__ == '__main__':
    main()
