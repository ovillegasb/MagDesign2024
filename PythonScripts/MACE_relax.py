#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Script used to perform a structural relaxation using MACE to a group of .res structures.

James Darby, modified by Orlando Villegas.

"""

import glob
import argparse
import copy
import random
import os
import shutil
import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

import numpy as np
from func_timeout import func_set_timeout, FunctionTimedOut
from mace.calculators import mace_mp

import ase.io
from ase.units import GPa
from ase.constraints import FixSymmetry
from ase.spacegroup.symmetrize import check_symmetry, refine_symmetry
# from ase.constraints import FixAtoms
from ase.filters import FrechetCellFilter

# from ase.optimize.precon import PreconLBFGS
from ase.optimize import LBFGS
import torch

# warnings.filterwarnings("ignore", category=DeprecationWarning)
# warnings.filterwarnings(
#     'ignore',
#     message='The system is likely too small to benefit from the standard preconditioner')

# warnings.filterwarnings("ignore")

TITLE = """\033[1;36m
  __  __          _____ ______
 |  \\/  |   /\\   / ____|  ____|
 | \\  / |  /  \\ | |    | |__
 | |\\/| | / /\\ \\| |    |  __|
 | |  | |/ ____ \\ |____| |____
 |_|  |_/_/    \\_\\_____|______|
\033[m

Script created to run MACE using GPU by taking a set of .res structures.

Initial Script created by James Darby.
Modified by Orlando Villegas

Date: 2024-05-22

Usage:

    python mace_relax.py [options] [-h for helps]

Examples:

    python mace_relax.py

"""


def options():
    """Generate command line interface."""
    parser = argparse.ArgumentParser(
        prog="mace_relax",
        usage="%(prog)s [-options]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Enjoy the program!"
    )

    parser.add_argument(
        '--pressure',
        type=float,
        help='Pressure value (float)',
        default=0.1,
        metavar="val GPa"
    )

    # parser.add_argument(
    #     "--time_limit", "-t",
    #     default=5000,
    #     type=float,
    #     help='Time limit in seconds for geometric optimization.'
    # )

    parser.add_argument(
        "--relax_cell",
        action="store_true",
        default=False,
        help="Relax the cell parameters."
    )

    parser.add_argument(
        "--keep_symmetry",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "--tolerance",
        type=np.float64,
        default=1e-4,
        metavar="val"
    )

    parser.add_argument(
        "--double_relax",
        action="store_true",
        default=False,
        help="Performs two relaxation steps, (1) relaxes the structure while maintaining symmetry\
 (2) relaxes without constraint."
    )

    # parser.add_argument(
    #     "-nc",
    #     type=int,
    #     default=1
    # )

    # parser.add_argument(
    #     "-nt",
    #     type=int,
    #     default=1
    # )

    parser.add_argument(
        "--use_gpu",
        action="store_true",
        default=False,
        help="Configure MACE to use GPU. By default is CPU setup."
    )

    parser.add_argument(
        "--single_point",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "--format_output",
        default="extxyz",
        metavar="format",
        help="Specify the output format, default is extxyz, you can use cif for example."
    )

    return vars(parser.parse_args())


@func_set_timeout(3600.0)
def relax_config(
        atoms, relax_pos=True, relax_cell=True, tol=1e-3, method='lbfgs', max_steps=10000,
        constant_volume=False, refine_symmetry_tol=None, keep_symmetry=False, strain_mask=None,
        config_label=None, from_base_model=False, save_config=False, try_restart=False,
        fix_cell_dependence=False, applied_P=0.0, hydrostatic_strain=False, **kwargs):
    """Relaxes the structure and returns the state of relaxation and new structure."""
    print("atoms are", atoms)
    print("applied P is", applied_P)
    print("tol is", tol)
    print("keep symmetry is", keep_symmetry)
    E = atoms.get_potential_energy()

    print("E (eV) is", E, "----", "E/atom", E / len(atoms))

    print("relax_config symmetry before refinement at default tol 1.0e-6")
    check_symmetry(atoms, 1.0e-6, verbose=True)
    if refine_symmetry_tol is not None:
        refine_symmetry(atoms, refine_symmetry_tol)
        print("relax_config symmetry after refinement")
        check_symmetry(atoms, refine_symmetry_tol, verbose=True)
    if keep_symmetry:
        print("relax_config trying to maintain symmetry")
        atoms.set_constraint(FixSymmetry(atoms))

    print("after keeping symmetry atoms are", atoms)
    if method == 'lbfgs':
        # if 'move_mask' in atoms.arrays:
        #     atoms.set_constraint(FixAtoms(np.where(atoms.arrays['move_mask'] == 0)[0]))
        if relax_cell:
            print("setting atoms_cell")
            atoms_cell = FrechetCellFilter(
                            atoms,
                            mask=strain_mask,
                            constant_volume=constant_volume,
                            scalar_pressure=applied_P*GPa,
                            hydrostatic_strain=hydrostatic_strain
                        )
            print("atom_cell is", atoms_cell)
        else:
            atoms_cell = atoms
        # atoms.info["n_minim_iter"] = 0

        print("constructing opt...")
        # opt = PreconLBFGS(atoms_cell, use_armijo=False, **kwargs)
        # opt = LBFGS(atoms_cell, **kwargs)
        opt = LBFGS(atoms, **kwargs)

    else:
        raise ValueError('unknown method %s!' % method)
    print(f"trying to run..., tolerance: {tol:.2e}")
    opt.run(tol, max_steps)

    """

    if refine_symmetry_tol is not None:
        print("symmetry at end of relaxation at desired tol")
        check_symmetry(atoms, refine_symmetry_tol, verbose=True)
    print("symmetry at end of relaxation at default tol 1e-6")
    check_symmetry(atoms, 1.0e-6, verbose=True)

    if keep_symmetry:
        for (i_c, c) in enumerate(atoms.constraints):
            if isinstance(c, FixSymmetry):
                del atoms.constraints[i_c]
                break

    """

    fmax = max(np.linalg.norm(atoms.get_forces(), axis=1))
    good = True
    if fmax > tol:
        good = False

    return good, atoms


def relax_fname(
    fname, model_file, relax_arg_dict, good_fol="completed", bad_fol="fail", input_fol="input",
    device="cpu", only_sp=False, format_output="extxyz", double_relax=False
):
    """."""
    # create the folders
    for fol in [good_fol, bad_fol, input_fol]:
        if not os.path.isdir(fol):
            try:
                os.mkdir(fol)
            except FileExistsError:
                pass

    print("File name: {}".format(fname))
    print("="*60)
    # if model_file is not None:
    #     calculator = MACECalculator(model_paths=model_file, device=device, default_dtype="float64")
    # else:
    #     calculator = mace_mp(
    #         model="medium",
    #         dispersion=False,
    #         default_dtype="float64",
    #         device=device
    #     )

    # print(help(MACECalculator))
    calculator = mace_mp(model="medium", dispersion=True, default_dtype="float64", device=device)

    good_read = False
    if os.path.isfile(fname):
        input_struc = ase.io.read(fname)
        good_read = True

    if not good_read:
        print(f"failed to read {fname}")
        return False

    struc = copy.deepcopy(input_struc)
    struc.calc = calculator

    if only_sp:
        E = struc.get_potential_energy()
        print("E (eV) is", E, "----", "E/atom", E / len(struc))
        output_fol = good_fol
        outfile = fname.split("/")[-1].split(".")[0] + "_sp.extxyz"
        outname = output_fol + "/" + outfile
        ase.io.write(outname, struc)
        print(f"writing final struc to {outname}")

        return

    relax_kwargs = {
        "tol": 1e-4,
        "applied_P": 0.1,
        "keep_symmetry": True,
        "relax_cell": True
    }

    good_1 = True
    if double_relax:
        good_1 = False
        try:
            good_1, struc = relax_config(struc, **relax_kwargs)
        except FunctionTimedOut:
            good_1 = False
            # struc = input_struc
            print("Funcition time out")
        except RuntimeError:
            good_1 = False
            # struc = input_struc
            print("Run time erro")
        print(f"good = {good_1} and struc is {struc}")
        relax_arg_dict["keep_symmetry"] = False
        relax_arg_dict["relax_cell"] = True

    good = False
    if good_1:
        # TESTING
        # Second optimization, Very tight
        relax_kwargs.update(relax_arg_dict)

        try:
            # good, struc = relax_config(struc, **relax_arg_dict)
            good, struc = relax_config(struc, **relax_kwargs)
        except FunctionTimedOut:
            good = False
            # struc = input_struc
            print("Funcition time out")
        except RuntimeError:
            good = False
            # struc = input_struc
            print("Run time erro")

    print(f"good = {good} and struc is {struc}")
    E = struc.get_potential_energy()
    print("E (eV) is", E, "----", "E/atom", E / len(struc))
    struc.info = {}

    # write final structure to relavent folder
    if good:
        output_fol = good_fol
    else:
        output_fol = bad_fol

    outfile = fname.split("/")[-1].split(".")[0] + "." + format_output
    outname = output_fol + "/" + outfile
    print(f"writing final struc to {outname}")

    ase.io.write(outname, struc)
    if os.path.isfile(fname):
        print("using shutil to move with", fname, input_fol)
        shutil.move(fname, input_fol)

    return


def main():
    """Run main function."""
    print(TITLE)

    args = options()

    if torch.cuda.is_available():
        print("GPU is available")
    else:
        print("GPU is not available")

    files = glob.glob("*.res")
    files += glob.glob("*.cif")
    files += glob.glob("*.extxyz")

    assert len(files) != 0, "Files not found"
    """
    NOTE:
    CAN PUT PATH TO MODEL FILE HERE IF YOU HAVE IT
    """
    # model_file = "/home/ovillegas/Documents/test_MACE_vs_MProject/2023-12-03-mace-128-L1_epoch-199.model"
    model_file = "/home/ovillegas/Documents/test_MACE_vs_MProject/2024-01-07-mace-128-L2_epoch-199.model"
    if not os.path.isfile(model_file):
        print("Model file not found")
        exit()

    # model_file = None
    if model_file is not None:
        print(f"model_file is {model_file}")

    relax_kwargs = {
        "tol": args["tolerance"],
        "applied_P": args["pressure"],
        "keep_symmetry": args["keep_symmetry"],
        "relax_cell": args["relax_cell"]
    }

    format_output = args["format_output"]

    is_singlepoint = args["single_point"]
    print("Is single point?:", is_singlepoint)

    if len(files) > 0:
        random.shuffle(files)
        # Used for a CPUs set up:
        # with Pool(args.nc) as pool:
        #     items = [(fname, model_file, relax_kwargs) for fname in files_res]
        #     pool.starmap(relax_fname,  items)

        print("="*60)
        total_files = len(files)

        # Using CPUs:
        device = "cpu"
        # for GPU device:
        if args["use_gpu"]:
            device = "cuda"

        count = 0
        for fname in files:
            count += 1
            start_time = time.time()
            print("Doing something!", device)
            relax_fname(fname, model_file, relax_kwargs, device=device, only_sp=is_singlepoint, format_output=format_output, double_relax=args["double_relax"])
            end_time = time.time()
            execution_time = end_time - start_time
            print("="*60)
            print(f"File number: {count}/{total_files} - done in {execution_time:.3f} s")
            print("="*60)

        print("MACE job done!")


if __name__ == "__main__":
    main()
