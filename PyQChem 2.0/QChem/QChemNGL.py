"""This module encompasses functions to allow an enhanced visualization of desired
structures"""
from tkinter import *
from ase.io import write
import threading
import subprocess
import os
from ase.visualize import view
from functools import partial
def run_voila():
    os.chdir(os.getcwd())
    notebook_path = 'viewngl.ipynb'
    command = ['voila', notebook_path]
    subprocess.run(command)
def high_res(x):
    os.chdir(os.getcwd())
    write('test.vasp',x)
    voila_thread = threading.Thread(target=run_voila)
    voila_thread.start()
def low_res(x):
    view(x)
def view_ngl(x):
    win=Tk()
    win.geometry("100x100")
    b1=Button(win,text="high resolution")
    b1.pack()
    b1['command']=partial(high_res,x)
    b2=Button(win,text="low resolution")
    b2.pack()
    b2['command']=partial(low_res,x)
    win.mainloop()
