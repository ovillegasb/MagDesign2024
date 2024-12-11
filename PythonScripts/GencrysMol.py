#!/home/SharedExe/PyXtal/bin/python
# -*- coding: utf-8 -*-

"""Modified code to generate molecular crystals using PyXtal."""

from pyxtal.molecule import pyxtal_molecule, is_compatible_symmetry
from pyxtal import print_logo, pyxtal
from pyxtal.symmetry import get_symbol_and_number
from pyxtal.symmetry import Group
import numpy as np
import os
import psutil
import glob
from pyxtal.msg import Comp_CompatibilityError
from pyxtal.msg import Symm_CompatibilityError
from pyxtal.msg import VolumeError
import argparse
import multiprocessing
import time
import sys
from func_timeout import func_set_timeout, FunctionTimedOut
from pymatgen.core import Molecule

# TODO: Check if the oxidation state affects in the generation process.

one_atom = """1
one atom
ATOM          0.00000        0.00000        0.00000
"""


def options():
    """Parser main options."""
    parser = argparse.ArgumentParser(
        prog='GencryMol',
        description='Run PyXtal in parallel to generate a molecular crystal',
        usage='%(prog)s filename [options]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Enjoy!')

    parser.add_argument(
        "filename",
        help="Files name XYX.",
        nargs="+",
        metavar="mol.xyz [or mol1.xyz mol2.xyz ...]"
    )

    parser.add_argument(
        "--outdir",
        help="File output directory.",
        default="out",
        metavar="./out"
    )

    parser.add_argument(
        "--parallel",
        action='store_true',
        help="Execute parallel generation.",
        default=False
    )

    parser.add_argument(
        "-n_struct",
        default=500,
        type=int,
        metavar="N",
        help="Number of expected structures.",
        dest="attempts"
    )

    parser.add_argument(
        "-z_value",
        default=4,
        type=int,
        metavar="Z",
        help="Maximum value of Z, molecular formula units.",
        dest="Z_max"
    )

    parser.add_argument(
        "-ratio",
        default="1",
        type=str,
        metavar="x:y:z",
        help="Ratio between species, e.g. 1:2:1",
        dest="ratio"
    )

    parser.add_argument(
        "-atom",
        default=None,
        type=str,
        metavar="Atom",
        help="Enter an atom symbol",
        dest="atom"
    )

    parser.add_argument(
        "-atom_oxidation",
        default=0,
        type=int,
        metavar="+N/-N",
        help="Enter the oxidation state of the atom",
        dest="oxidation"
    )

    return parser.parse_args()


def get_cpu_num():
    """Return cpu number."""
    pid = os.getpid()
    p = psutil.Process(pid)
    return p.cpu_num()


def run_generator(
    system, numIons=[], sg_list=[], dimension=3, molecular=True, factor=1.0, conventional=False,
    outdir=".", generated=0, ratio=[1], **kwargs
):
    """Run structure generation."""
    sg = np.random.choice(sg_list)
    n_rand_ion = np.random.choice(numIons)
    symbol, sg = get_symbol_and_number(sg, dimension)
    print(f"Using: {symbol} ({sg})")
    print(f"Z value: {n_rand_ion}")
    # call spacegroup object
    g = Group(sg)
    # print(g)
    # print(len(g))
    # for wp in g:
    #    print(wp)
    #    print(type(wp))
    print("-" * 55)
    print("Checking compatibility")
    for mol in system:
        # print(mol)
        # print(type(mol))
        # print(dir(mol))
        print(mol.mol)
        # print(type(mol.mol))
        # print(sg)
        status = []
        for wp in g:
            status.append(is_compatible_symmetry(mol.mol, wp))

        if sum(status) == 0:
            print("test not passed")
            return False
        else:
            print("passed test")

    rand_crystal = pyxtal(molecular=molecular)
    composition = np.array([n_rand_ion]) * np.array(ratio)

    @func_set_timeout(30.0)
    def random_crystal():
        rand_crystal.from_random(
            dimension,
            sg,
            system,
            composition,
            factor,
            conventional=conventional
        )

    try:
        random_crystal()

    except Comp_CompatibilityError:
        print("Composition",  composition, "not compatible with symmetry", sg)
        return False
    except Symm_CompatibilityError:
        print("Molecular symmetry is not compatible with WP site", sg)
        return False
    except VolumeError:
        print("Failure to adjust volume after 100 cycles.")
        return False
    except RuntimeError:
        print("Long time to generate structure")
        return False
    except FunctionTimedOut:
        print("Funcition time out")
        return False

    outpath = outdir + f"/{generated:05}_{sg}.cif" if dimension > 0 else outdir + f"/{generated:05}_{sg}.xyz"
    rand_crystal.to_file(filename=outpath)

    return True


def run_task(kwargs):
    """Run a task in parallel."""
    seed = get_cpu_num()
    np.random.seed(seed)
    time.sleep(0.1)
    return run_generator(**kwargs)


def main():
    """Run main program."""
    print_logo()
    args = options()
    t_i_total = time.time()

    dimension = 3
    factor = 0.3
    conventional = False
    attempts = args.attempts
    outdir = args.outdir
    molecular = True
    system = []
    for mol in args.filename:
        m = Molecule.from_file(mol)
        # mol_with_oxidation = m.add_oxidation_state_by_element({"O": -2, "C": +4, "H": +1})
        system.append(pyxtal_molecule(m))
        # system.append(pyxtal_molecule(mol_with_oxidation))
    atom = args.atom
    if atom is not None:
        one_atom_str = one_atom.replace("ATOM", atom)
        m = Molecule.from_str(one_atom_str, fmt='xyz')
        # mol_with_oxidation = m.add_oxidation_state_by_element({atom: args.oxidation})
        # system.append(pyxtal_molecule(mol_with_oxidation))
        system.append(pyxtal_molecule(m))

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    ratio = [int(a) for a in args.ratio.split(":")]
    if len(ratio) != len(system):
        ratio *= len(system)

    # check existing files
    n_completed = 0
    files = glob.glob(f"{outdir}/*.cif")
    n_completed += len(files)

    # Spacegroup
    sg_list = np.arange(1, 231)
    # Composition
    numIons = np.array(list(range(1, args.Z_max + 1)))
    print("-" * 55)

    if not args.parallel:
        while n_completed <= attempts:
            struct_ok = run_generator(
                system,
                numIons,
                sg_list,
                dimension,
                molecular,
                factor,
                conventional,
                outdir,
                n_completed,
                ratio
            )

            print("-" * 55)
            if struct_ok:
                print(f"Structure {n_completed:05}/{attempts:05} generated")
                n_completed += 1

        t_f_total = time.time()
        execution_time = t_f_total - t_i_total
        print("\tElapsed time done in %.3f s" % execution_time)
        sys.exit(0)

    # Parallel process
    # arguments preparations
    tasks = [
        {
            "system": system,
            "numIons": numIons,
            "sg_list": sg_list,
            "dimension": dimension,
            "molecular": molecular,
            "factor": factor,
            "conventional": conventional,
            "outdir": outdir,
            "generated": n_completed,
            "ratio": ratio
        }
        for i in range(attempts)
    ]

    n_completed = 0
    while n_completed < attempts:
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            results = pool.map(run_task, tasks[n_completed:])
            n_completed += sum(results)
            print(results)
            print(f"Structure {n_completed:05}/{attempts:05} generated")

    print('\nAll generation are done')
    # print(f"\t\033[1;32mStructures generated: {generated.value:04d}/{attempts:04d}\033[0m")
    t_f_total = time.time()
    execution_time = t_f_total - t_i_total
    print("\tElapsed time done in %.3f s" % execution_time)


if __name__ == '__main__':
    main()
