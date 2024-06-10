#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Module used to filter chemically meaningful samples generated by WAM.

Create by Orlando Villegas - June 2024

"""

import shutil
import argparse
import time
import os
import glob
import ase.io
from ase.neighborlist import NeighborList
from ase.data import covalent_radii
import numpy as np
import pandas as pd

import networkx as nx
import itertools as it
from func_timeout import func_set_timeout, FunctionTimedOut

# TODO:
#     check that all metal centers are connected.
#     check that the distances are not too close.

# Maximum execution time of the function (s).
time_limit = 30


def options():
    """Generate command line interface."""
    parser = argparse.ArgumentParser(
        prog="Structural filtre for MOF",
        usage="%(prog)s [-options]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Enjoy the program!"
    )

    fileinput = parser.add_argument_group(
        "\033[1;36mInitial settings\033[m")

    fileinput.add_argument(
        "--radius",
        help="Radius of cut-off for neighbor search (ang).",
        type=float,
        default=5.0
    )

    fileinput.add_argument(
        "-cutoff",
        help="Cut-off distance between the ligand and the metal (ang).",
        type=float,
        default=3.28
    )

    fileinput.add_argument(
        "-i",
        help="Structure file. It is used to take a particular structure, by default the program\
takes all the structures of a repertoire.",
        type=str,
        default=None
    )

    fileinput.add_argument(
        "--metal_center",
        help="Atomic symbol of the metal center. By default it is Pb.",
        type=str,
        default="Pb"
    )

    fileinput.add_argument(
        "--file_types",
        help="Format of files to be checked. By default it will read all *.res files. Disabled if \
a particular file is read using the [-i] option.",
        type=str,
        default="*.res"
    )

    fileinput.add_argument(
        "--output",
        help="Folder where the refused structures will be moved. By default it is \"./rejected\".",
        type=str,
        default="./rejected"
    )

    fileinput.add_argument(
        "--n_test",
        help="Define a number of test files to be read. These files will not be moved.",
        type=int,
        default=None
    )

    return vars(parser.parse_args())


def classify_directions(direction, neighbor_index, threshold_angle=10):
    """Classify direction."""
    angle_with_x = np.degrees(np.arccos(np.dot(direction, [1, 0, 0])))
    angle_with_y = np.degrees(np.arccos(np.dot(direction, [0, 1, 0])))
    angle_with_z = np.degrees(np.arccos(np.dot(direction, [0, 0, 1])))

    if angle_with_x < threshold_angle or angle_with_x > (180 - threshold_angle):
        return 'x'
    elif angle_with_y < threshold_angle or angle_with_y > (180 - threshold_angle):
        return 'y'
    elif angle_with_z < threshold_angle or angle_with_z > (180 - threshold_angle):
        return 'z'
    else:
        return 'other'


def angle_between_vectors(v1, v2):
    """Compute angle in rad between two vectors."""
    cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    # Asegurar que el valor de cos_theta esté en el rango [-1, 1] para evitar errores numéricos
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    angle = np.arccos(cos_theta)
    return angle


def angle_matrix(vectors):
    """
    Construye una matriz de ángulos entre una lista de vectores de 3 componentes.

    Args:
        vectors (list of np.array): Lista de vectores de 3 componentes.

    Returns:
        np.array: Matriz de ángulos en radianes entre los vectores.
    """
    num_vectors = len(vectors)
    angles = np.zeros((num_vectors, num_vectors))

    for i in range(num_vectors):
        for j in range(i, num_vectors):
            angle = angle_between_vectors(vectors[i], vectors[j])
            angles[i, j] = np.rad2deg(angle)
            angles[j, i] = np.rad2deg(angle)  # La matriz es simétrica

    return angles


def get_neighbor_info(index, atoms, indices, offsets, cutoff):
    """Return distances."""
    positions = atoms.get_positions()
    cell = atoms.get_cell()
    distances = []
    box_offsets = []
    directions = []
    neighbor_position_list = []
    for neighbor_index, offset in zip(indices, offsets):
        neighbor_position = positions[neighbor_index] + np.dot(offset, cell)
        displacement_vector = neighbor_position - positions[index]
        direction = displacement_vector / np.linalg.norm(displacement_vector)
        # print(atoms[index].symbol, atoms[neighbor_index].symbol, direction)
        # print(classify_directions(direction, neighbor_index, threshold_angle=10))
        distance = np.linalg.norm(positions[index] - neighbor_position)
        if distance <= cutoff:
            distances.append(distance)
            box_offsets.append(tuple(offset))
            directions.append(direction)
            neighbor_position_list.append(round(np.dot(neighbor_position, neighbor_position), 3))

    return np.array(sorted(distances)), box_offsets, directions, neighbor_position_list


def get_neighbors(index, atoms, neighbor_list):
    """Return neighbor list from a atom index."""
    indices, offsets = neighbor_list.get_neighbors(index)
    neighbors = []
    for i, offset in zip(indices, offsets):
        neighbor_position = atoms.positions[i] + np.dot(offset, atoms.get_cell())
        neighbors.append((i, neighbor_position))
    return neighbors


def detect_ligand(atoms, indexs):
    """Return dict composed of indices belonging to the ligands of the system."""
    numbers = np.array(atoms.get_atomic_numbers())
    radii = np.array([covalent_radii[n] for n in numbers])
    nl_ligands = NeighborList(
        cutoffs=radii,
        bothways=True,
        self_interaction=False
    )

    nl_ligands.update(atoms)

    connectivity = {}
    conn = nx.DiGraph()
    for atom in atoms:
        # atoms list connected
        i1, _ = nl_ligands.get_neighbors(atom.index)
        connectivity[atom.index] = list(i1)
        conn.add_node(atom.index)

    # Add edges like bonds
    for i in connectivity:
        for ai, aj in it.product([i], connectivity[i]):
            conn.add_edge(ai, aj)
            conn.add_edge(aj, ai)

    atoms_MOL = nx.weakly_connected_components(conn)
    # dict imol : Natoms, indexs
    bulk = dict()
    ipol = 0
    for mol in atoms_MOL:
        mol = list(sorted(mol))
        bulk[ipol] = dict()
        bulk[ipol]["Natoms"] = len(mol)
        bulk[ipol]["index"] = list(np.array(indexs)[mol])
        ipol += 1

    return bulk


@func_set_timeout(time_limit)
def test_mof_structure(file, n, metal_center, radius, cutoff, test_count=None):
    """Read and return if the MOF enviroment is correct from differents criterias."""
    rejected = False
    # Load structure
    mof = ase.io.read(file)
    # select atoms from ligands
    ligands_indexs = []
    metal_index = []
    for at in mof:
        if at.symbol == metal_center:
            metal_index.append(at.index)
        elif at.symbol == "H":
            continue
        else:
            ligands_indexs.append(at.index)

    # ligands = mof[ligands_indexs]
    ligands = detect_ligand(mof[ligands_indexs], ligands_indexs)
    # Compute the neighbor list with a radius cutoff
    nl = NeighborList(
        [radius] * len(mof),
        self_interaction=False,
        bothways=True,
    )
    nl.update(mof)

    # Test connections ligands - metal
    for lig in ligands:
        symbols = mof[ligands[lig]["index"]].symbols
        print(f"Ligand:     {lig} - {symbols}")
        pb_connections = 0
        lig_connectivity = {}
        list_offsets = []
        vectors_to_connect = []
        for lig_index in ligands[lig]["index"]:
            indices, offsets = nl.get_neighbors(lig_index)

            selection_m = []
            for i in indices:
                if i in metal_index:
                    selection_m.append(True)
                else:
                    selection_m.append(False)

            distances, box_offsets, directions, neighbor_position_list = get_neighbor_info(
                lig_index,
                mof,
                indices[selection_m],
                offsets[selection_m],
                cutoff
            )
            # print(lig_index, distances, box_offsets, directions)
            lig_connectivity[lig_index] = {
                "distances": distances,
                "offsets": box_offsets,
                "metal_positions": neighbor_position_list
            }
            list_offsets += box_offsets
            vectors_to_connect += directions
            for _ in distances:
                pb_connections += 1

        angles_m = angle_matrix(vectors_to_connect)
        vectors_mean = np.array(vectors_to_connect).mean(axis=0) if np.array(vectors_to_connect).size > 0 else 0.0
        # COmprobar si estan conectaddos al mismo atomos de metal o no
        metals_neighbors = []
        for l_i in lig_connectivity:
            for val in lig_connectivity[l_i]["metal_positions"]:
                if val not in metals_neighbors:
                    metals_neighbors.append(val)
        # print(metals_neighbors)
        ligands[lig]["n_conn"] = pb_connections
        ligands[lig]["offsets"] = set(list_offsets)
        ligands[lig]["test_direction"] = np.dot(vectors_mean, vectors_mean)
        ligands[lig]["angle_mean"] = angles_m.mean() if angles_m.size > 0 else 0.0
        ligands[lig]["N_metals"] = len(metals_neighbors)

        lignand_connect = pd.DataFrame(lig_connectivity).T
        print(lignand_connect)

    info_ligand_connection = pd.DataFrame(ligands).T
    print("\nSummary of ligand atom connections:")
    print(info_ligand_connection)
    # Structural selection criteria
    # -----------------------------
    # I. Criteria for connectivity generated by cut-off distance.
    # At least one ligand of the system must be connected between two metal centers.
    #
    # II. Criteria for isolated ligands. Ligands not connected to anything.
    condition_I = (info_ligand_connection["N_metals"] >= 2).any()
    condition_II = (info_ligand_connection["N_metals"] == 0).any()
    print("")

    if condition_I and not condition_II:
        print("The structure has been preserved!")
        print("At least one ligand is connected to two different metal centers.")
    else:
        print("No ligand is connected to two different metal centers.")
        print("According to the selected criteria there is no metal-ligand-metal connection.")
        print("The structure will be rejected")
        print(f"{file} --> ./rejected/{file}")
        rejected = True

    return rejected


def main():
    """Run program."""
    start_time = time.time()
    args = options()
    radius = args["radius"]
    metal_center = args["metal_center"]
    cutoff = args["cutoff"]
    test_count = args["n_test"]
    print("Structural filtre for MOF")
    print("-------------------------")
    print("Parameters:")
    print(f"\tNeighbor cut-off radius: {radius:.2f} angs")
    print(f"\tCut-off distance M-L:    {cutoff:.2f} angs")
    print(f"\tMetal center:            {metal_center}")

    if args["i"] is None:
        file_types = args["file_types"]
        if not file_types.startswith("*."):
            file_types = file_types.replace(".", "")
            file_types = file_types.replace("*", "")
            file_types = "*." + file_types

        print(f"\tFile types:              {file_types}")
        structures = glob.glob(file_types)
        n_structures = len(structures)
        print(f"\tTotal number of files:   {n_structures}")

    else:
        file = args["i"]
        print(f"\tFile selected:           {file}")
        structures = [file]
        n_structures = len(structures)

    output_folder = args["output"]
    print(f"\tOutput folder:           {output_folder}")
    try:
        os.mkdir(output_folder)
    except FileExistsError:
        pass

    print("-------------------------\n")
    n_rejected = 0
    n_tested = 0
    for n, file in enumerate(structures, start=1):
        print("---------------------------------------------------")
        print("File name:     %s (%d/%04d)" % (file, n, n_structures))
        print("---------------------------------------------------")
        rejected = False
        try:
            rejected = test_mof_structure(file, n, metal_center, radius, cutoff, test_count)
        except FunctionTimedOut:
            print("Function Timed Out. The file will be rejected")
            rejected = True

        if rejected and test_count is None:
            shutil.move(f"./{file}", f"./rejected/{file}")
            n_rejected += 1

        n_tested += 1

        if n == test_count:
            break

    print(f"\nTotal number of rejected files:   {n_rejected:04d}/{n_structures:04d}")
    print(f"Total number of preserved files:  {n_tested - n_rejected:04d}/{n_structures:04d}")

    end_time = time.time()
    execution_time = end_time - start_time
    print("Done {:.3f}s".format(execution_time))


if __name__ == '__main__':
    main()
