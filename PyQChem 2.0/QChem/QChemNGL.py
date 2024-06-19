"""This module encompasses functions to allow an enhanced visualization of desired
structures"""
from tkinter import *
from ase.io import write
import threading
import subprocess
import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from ase.visualize import view
from functools import partial
def run_voila():
    """
    runs in the command line the voila command to view the output of the .jnb file in the folder
    """
    os.chdir(SCRIPT_DIR)
    notebook_path = 'viewngl.ipynb'
    command = ['voila', notebook_path]
    subprocess.run(command)
def high_res(x):
    """
    renders high definition visualization and enables duplication of structures
    """
    os.chdir(SCRIPT_DIR)
    write('test.vasp',x)
    voila_thread = threading.Thread(target=run_voila)
    voila_thread.start()
def low_res(x):
    """
    renders simplistic visualization and enables saving the structure in desired format (.cif,.vasp ...etc.)
    """
    view(x)
def view_ngl(x):
    """
    creates a window that enables choice between the resolutions available.
    """
    win=Tk()
    win.geometry("100x100")
    b1=Button(win,text="high resolution")
    b1.pack()
    b1['command']=partial(high_res,x)
    b2=Button(win,text="low resolution")
    b2.pack()
    b2['command']=partial(low_res,x)
    win.mainloop()
