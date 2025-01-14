'''This module encompasses all the functions needed for visualization of the different 
structures described in each file type'''
import os
from ase.io import read
from ase.io.res import Res,SinglePointCalculator
from pymatgen.io.cif import CifWriter
from pymatgen.io.vasp import Poscar
from QChem.QChemNGL import view_ngl
def read_resx(fn, index=-1):
    """
    The read_resx function is a tweaked version of the reas_res functionof the ase module,
    it is modified so that it reads a string as res file rather than read an actual res file
    """
    images = []
    res = Res.from_string(fn) #reading a res file from a string
    if res.energy:
        calc = SinglePointCalculator(res.atoms,energy=res.energy)
        res.atoms.calc = calc
    images.append(res.atoms)
    return images[index]
def letmesee_poscar(n,l_poscar):
    """
    the letmesee_poscar function reads a string as a poscar/vasp file and enables visualization
    of the corresponding structure, here the l_poscar is a list of molecules written in vasp format
    therefore alongside the list an index (n) must be present as well
    """
    poscar = Poscar.from_str(l_poscar[n]) #reading a vasp file from a string
    w = CifWriter(poscar.structure, symprec=1e-6) #conversion from vasp to cif
    w.write_file('ouioui.cif') #creation of a temporary cif file
    x=read('ouioui.cif') #reading the file
    view_ngl(x) #visualization
    os.remove('ouioui.cif') #temporary file deletion
def letmesee_res(n,l_res):
    """
    the letmesee_res function is similar to the previous with no conversions needed though
    """
    view_ngl(read_resx(l_res[n]))
def view_xyz(path):
    """
    the view_xyz and view_xyz2 functions allows visualization of 
    .xyz files and takes a path as an argument
    """
    try:
        y=read(path)
        view_ngl(y)
    except:
        return
def view_xyz2(p,value_inside):
    s=str(p)+'/'+value_inside.get()
    view_xyz(s) 