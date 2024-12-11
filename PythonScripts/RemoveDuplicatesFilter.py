#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Filter used to remove equivalent structures.

Create by Orlando Villegas - June 2024

"""

import time
import argparse
import glob
import os
import shutil
import spglib
from ase.io import read
import ase
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.alchemy.filters import RemoveDuplicatesFilter
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer


def pymatgen2ase(struc):
    atoms = ase.Atoms(symbols=struc.atomic_numbers, cell=struc.lattice.matrix)
    atoms.set_scaled_positions(struc.frac_coords)
    return atoms


def ase2pymatgen(struc):
    lattice = struc.get_cell()
    coordinates = struc.get_scaled_positions()
    species = struc.get_chemical_symbols()
    return Structure(lattice, species, coordinates)


def symmetrize_cell(struc, mode="C"):
    """
    symmetrize structure from pymatgen, and return the struc in conventional/primitive setting
    Args:
    struc: ase type
    mode: output conventional or primitive cell
    """
    P_struc = ase2pymatgen(struc)
    finder = SpacegroupAnalyzer(P_struc, symprec=0.06, angle_tolerance=5)
    if mode == "C":
        P_struc = finder.get_conventional_standard_structure()
    else:
        P_struc = finder.get_primitive_standard_structure()

    # return pymatgen2ase(P_struc)
    return P_struc


def symmetrize_structure(atoms, initial_symprec=1e-3, final_symprec=1e-8):
    """Return symmetryzed structure."""
    # Convertir la estructura a un formato compatible con spglib
    cell = (atoms.get_cell(), atoms.get_scaled_positions(), atoms.get_atomic_numbers())

    # Detectar la simetría de la estructura
    spacegroup = spglib.get_spacegroup(cell, symprec=initial_symprec, symbol_type=0)
    print("Spacegroup init:", spacegroup)

    # Aplicar la simetría para simetrizar la estructura
    symmetrized_cell = spglib.standardize_cell(
        cell,
        to_primitive=False,
        no_idealize=False,
        symprec=final_symprec
    )
    spacegroup = spglib.get_spacegroup(symmetrized_cell, symprec=initial_symprec, symbol_type=0)
    print("Spacegroup Symmetrized:", spacegroup)

    # refine_cell = spglib.refine_cell(
    #     symmetrized_cell,
    #     to_primitive=False,
    #     no_idealize=False,
    #     symprec=final_symprec
    # )
    # spacegroup = spglib.get_spacegroup(refine_cell, symprec=initial_symprec, symbol_type=0)
    # print("Spacegroup refine:", spacegroup)

    atoms.set_cell(symmetrized_cell[0])
    atoms.set_scaled_positions(symmetrized_cell[1])

    return atoms


def options():
    """Generate command line interface."""
    parser = argparse.ArgumentParser(
        prog="RemoveDuplicatesFilter",
        usage="%(prog)s [-options]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Enjoy the program!"
    )

    fileinput = parser.add_argument_group(
        "\033[1;36mInitial settings\033[m")

    fileinput.add_argument(
        "--file_types",
        help="Format of files to be checked. By default it will read all *.res files. Disabled if \
a particular file is read using the [-i] option.",
        type=str,
        default=".res",
        metavar=".res"
    )

    fileinput.add_argument(
        "--output",
        help="Folder where the refused structures will be moved. By default it is \"./rejected\".",
        type=str,
        default="./rejected"
    )

    return vars(parser.parse_args())


def main():
    """Run program."""
    start_time = time.time()
    args = options()

    print("Structural filtre: Remove Duplicates")
    print("------------------------------------")

    file_types = args["file_types"]
    if not file_types.startswith("*."):
        file_types = file_types.replace(".", "")
        file_types = file_types.replace("*", "")
        file_types = "*." + file_types

    print(f"\tFile types:              {file_types}")
    structures = glob.glob(file_types)
    n_structures = len(structures)
    print(f"\tTotal number of files:   {n_structures}")

    output_folder = args["output"]
    print(f"\tOutput folder:           {output_folder}")
    try:
        os.mkdir(output_folder)
    except FileExistsError:
        pass

    print("--------------------------------------------\n")

    structs_for_test = {}
    for n, file in enumerate(structures, start=1):
        print("---------------------------------------------------")
        print("File name:     %s (%d/%04d)" % (file, n, n_structures))
        print("---------------------------------------------------")

        ase_struct = read(file)
        # ase_struct_symm = symmetrize_structure(ase_struct, initial_symprec=1e-6, final_symprec=1e-8)
        pymatgen_struct = symmetrize_cell(ase_struct, mode="P")
        # pymatgen_struct = AseAtomsAdaptor.get_structure(ase_struct_symm)

        # print(pymatgen_struct)
        structs_for_test[file] = pymatgen_struct.copy()
        # structs_for_test[file] = Structure.from_file(file)

    print("The database loads all the files.")
    print("The next step is to compare.")
    print("Analyzing...")
    time.sleep(2.0)

    # Initializing the StructureMatcher
    matcher = StructureMatcher(
        ltol=0.5,      # Length tolerance
        stol=0.5,      # Site tolerance
        angle_tol=5.0,
        primitive_cell=True,
        scale=True,
        attempt_supercell=False   # True
    )

    # Create the RemoveDuplicatesFilter filter
    duplicate_filter = RemoveDuplicatesFilter(
        structure_matcher=matcher,
        symprec=1e-6
    )

    # Apply the filter to obtain unique structures
    unique_structures = {}
    n_duplicates = 0
    for file in structs_for_test:
        struct = structs_for_test[file]
        # True if structure is not in list.
        is_unique = duplicate_filter.test(struct)
        if is_unique:
            unique_structures[file] = struct
        else:
            n_duplicates += 1
            print("N duplicates detected: %04d" % n_duplicates)

    print(f"Initial list {len(structs_for_test)}")
    print(f"Final list {len(unique_structures)}")
    # Imprimir las estructuras únicas
    # for file in unique_structures:
    #     print(file)
    #     print(struct)
    #     break

    # Selecting ''no duplicates structures'' structues
    n_rejected = 0
    n_tested = 0
    for n, file in enumerate(structures, start=1):
        print("---------------------------------------------------")
        print("File name:     %s (%d/%04d)" % (file, n, n_structures))
        print("---------------------------------------------------")

        if file not in unique_structures:
            shutil.move(f"./{file}", f"./rejected/{file}")
            n_rejected += 1

        n_tested += 1

    print(f"\nTotal number of rejected files:   {n_rejected:04d}/{n_structures:04d}")
    print(f"Total number of preserved files:  {n_tested - n_rejected:04d}/{n_structures:04d}")

    end_time = time.time()
    execution_time = end_time - start_time
    print("Done {:.3f}s".format(execution_time))


if __name__ == '__main__':
    main()
