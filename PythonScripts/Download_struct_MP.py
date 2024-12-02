#!/bin/env python3
# -*- coding: utf-8 -*-

"""Download structures from the Material Project database."""

from pymatgen.ext.matproj import MPRester

# DOC on https://pymatgen.org/usage.html
# search MPRester

# Structures for CaCO3 from MaterialProject
ChemicalFormula = input("Enter a molecular formula [ex CaCO3] : ")


with MPRester("zmRhiIRqDmXPPWAgJNUYeg8KJXqrW5e1") as m:
    # Some functions:
    # get_structures

    print("----")
    entries = m.get_entries(ChemicalFormula)
    n_entries = len(entries)

    # get_entries_in_chemsys
    # get_structures
    # query

    if n_entries > 0:
        print(f"{n_entries} entries were found")
        material_ids = m.get_material_ids(ChemicalFormula)
        for mat in material_ids:
            id_name = int(mat.replace("mp-", ""))
            struct = m.get_structure_by_material_id(mat)

            print(f"\nStructure {mat}:\n", struct)
            print("-"*50)
            struct.to(filename=f"./{id_name:07}.cif")
            print(f"saved file ./{id_name:07}.cif")
            print("-"*50)
    else:
        print("NO structure was found.")

    # print("----")
    # structures = m.get_structures("CaCO3")
    # print("N structures:", len(structures))

    ## Structure for material id
    #structure = m.get_structure_by_material_id("mp-1234")
    #print(structure)
    #
    #print("\nStructure:\n", struct)
    #struct.to(filename=f"./{i:06}.cif")
    #print(f"saved file ./{i:06}.cif")

print("Done!")
