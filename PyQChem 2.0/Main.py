"""this is the script to run to start with the application"""
from tkinter import *
from functools import partial
import os
from QChem.QChemFile import browse,browse_xyz,back
from QChem.HoverObject import CreateToolTip
if __name__=='__main__':
    w=Tk()
    w.geometry("300x200")
    b1=Button(w,text="import your file")
    b1.place(x=100,y=30)
    b2=Button(w,text="USPEX File here",state='disabled')
    b2.place(x=95,y=90)
    b3=Button(w,text='❎',state='disabled')
    b3.place(x=195,y=90)
    b4=Button(w,text='select multiple files',command=browse_xyz)
    b4.place(x=85,y=150)
    # path="C:\\Users\\br\\Desktop"
    # os.chdir(path)
    b1['command']=partial(browse,b1,b2,b3,b4)
    b3['command']=partial(back,b1,b2,b3,b4)
    b5=Button(w,text="❓")
    b6=Button(w,text="❓")
    b5.place(x=200,y=30)
    b6.place(x=200,y=150)
    CreateToolTip(b3, 10,"Abort")
    CreateToolTip(b5, 10, "supported files alongside possible actions:\n -.Cif,.xyz,.vasp files:structure visualization\n -.res file:molecules are ordered by their energy from low energy to high energy and after\n choosing an index interval a plot is generated(energy=f(index))+the points in the plot are\n clickable and give structure visualization of the specific molecule\n -Gathered POSCAR files:this file format needs a USPEX file to classify the molecules in terms\n of energy and generation in a plot with the same features as the .res file plot")
    CreateToolTip(b6, 10, "here you can choose a folder that contains either .cif,.vasp or .xyz files, when the folder is chosen\n if the files contain information about the respective energies of the structures a plot is generated,\n in the opposite case a list of the files inside the folder is presented and by choosing a file you can simply\n visualize the structure represented in the file.\n P.S:in the plot the points are also clickable and enable visualization of the corresponding molecule. ")
    w.mainloop()
    
