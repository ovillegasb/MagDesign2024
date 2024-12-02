#!/bin/env python3

"""Interface script connecting to DFTB+."""

import glob
import argparse
import os
import time
import random
import shutil
from ase.calculators.dftb import Dftb
import ase.io
from ase.optimize import LBFGS
import numpy as np
from func_timeout import func_set_timeout, FunctionTimedOut
from ase.calculators.singlepoint import SinglePointCalculator
from ase.calculators.calculator import CalculationFailed
from ase.filters import FrechetCellFilter
from ase.units import GPa


TITLE = """\033[1;36m
 ______   ________  _________  ______
|_   _ `.|_   __  ||  _   _  ||_   _ \\    .-.
  | | `. \\ | |_ \\_||_/ | | \\_|  | |_) | __| |__
  | |  | | |  _|       | |      |  __'.|__   __|
 _| |_.' /_| |_       _| |_    _| |__) |  | |
|______.'|_____|     |_____|  |_______/   '-'
\033[m

Script created to run DFTB+ by taking a set of structures from a repertoire.

Created by Orlando Villegas

Date: 2024-11-27

Usage:

    python DFTB_relax.py [options] [-h for helps]

Examples:

    python mace_relax.py

"""


def options():
    """Generate command line interface."""
    parser = argparse.ArgumentParser(
        prog="DFTB_relax",
        usage="%(prog)s [-options]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Enjoy the program!"
    )

    parser.add_argument(
        "--tolerance",
        type=np.float64,
        default=1e-2,
        metavar="val",
        dest="tol",
        help="Tolerance between minimization steps (default tol=1e-2)"
    )

    parser.add_argument(
        "-method",
        type=str,
        default="GFN1-xTB",
        metavar="xTB method",
        choices=['GFN1-xTB', 'GFN2-xTB'],
        help="You can choose between \'GFN1-xTB\' and \'GFN2-xTB\'"

    )

    parser.add_argument(
        "--single_point",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "--no_relax_cell",
        action="store_false",
        default=True,
        help="Don't relax the cell parameters."
    )

    return vars(parser.parse_args())


@func_set_timeout(1200.0)
def relax_config(
        atoms, tol=1e-3, max_steps=1000, relax_cell=True, strain_mask=None,
        constant_volume=False, applied_P=0.1, hydrostatic_strain=False):
    """Relax the structure."""
    print("atoms are", atoms)
    print("tol is", tol)

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

    opt = LBFGS(atoms)
    opt.run(tol, max_steps)

    fmax = max(np.linalg.norm(atoms.get_forces(), axis=1))
    good = True
    if fmax > tol:
        good = False

    return good, atoms


def relax_fname(
    fname, method="GFN1-xTB", good_fol="completed", bad_fol="fail", input_fol="input",
    only_sp=False, tol=1e-2, relax_cell=True
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
    name = fname.split("/")[-1].split(".")[0]
    print("="*60)

    calc = Dftb(
        label=name,
        Hamiltonian_="xTB",
        Hamiltonian_Method=method,
        Hamiltonian_SCC='Yes',
        Hamiltonian_SCCTolerance=1e-7,
        Hamiltonian_MaxSCCIterations=5000,
        Charge=0,
        RestartFrequency=20,
        kpts=(1, 1, 1)
    )

    struc = ase.io.read(fname)
    struc.calc = calc

    if only_sp:
        outfile = name + "_sp.extxyz"
        try:
            E = struc.get_potential_energy()
            output_fol = good_fol
            print("E (eV) is", E, "----", "E/atom", E / len(struc))
            # Crear un SinglePointCalculator solo con la energía
            struc.calc = SinglePointCalculator(struc, energy=E)
            struc.info = {}
        except CalculationFailed:
            print("Calculation failed!")
            output_fol = bad_fol

    else:
        good = False
        try:
            good, struc = relax_config(struc, tol=tol, relax_cell=relax_cell)
        except FunctionTimedOut:
            good = False
        except ValueError:
            good = False

        # write final structure to relavent folder
        if good:
            output_fol = good_fol
        else:
            output_fol = bad_fol

        outfile = name + ".extxyz"

    outname = output_fol + "/" + outfile
    ase.io.write(outname, struc)
    print(f"writing final struc to {outname}")
    print("Finished!")

    # move input file to inputs
    if os.path.isfile(fname):
        print("using shutil to move with", fname, input_fol)
        # try:
        shutil.move(fname, input_fol)


def main():
    """Run main program."""
    print(TITLE)
    args = options()

    files = glob.glob("*.cif")
    files += glob.glob("*.extxyz")
    random.shuffle(files)
    print("="*60)
    total_files = len(files)
    count = 0
    for file in files:
        count += 1
        start_time = time.time()
        print("Doing something!")
        relax_fname(
            file,
            method=args["method"],
            only_sp=args["single_point"],
            tol=args["tol"],
            relax_cell=args["no_relax_cell"]
        )
        end_time = time.time()
        execution_time = end_time - start_time

        print("="*60)
        print(f"File number: {count}/{total_files} - done in {execution_time:.3f} s")
        print("="*60)
    print("MACE job done!")


if __name__ == '__main__':
    main()
