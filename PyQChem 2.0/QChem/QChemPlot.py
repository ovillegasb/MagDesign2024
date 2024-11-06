"""This module encompasses all the functions needed to generate the plots 
required in the app
also the plot functions are kind of redundant so to check the full comments refer to the
motion function in difficulty of understanding the why and how"""
from tkinter import Frame,Button,Toplevel
from functools import partial
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from QChem.HoverObject import CreateToolTip
from QChem.QChemView import letmesee_poscar,letmesee_res,view_xyz
dir = os.path.dirname(__file__)
os.chdir(dir)

def str_ab(s):
    """
    this function turns a range/interval written as a string into 2 integers
    """
    try:
        t=s.split("-")
        return [int(t[0]),int(t[1])]
    except:
        return
"""the following commented version of coordinate_calcul and reverse_coordinate_calcul
has slightly adjusted constants that i'd rather keep just in case"""
#JUPYTER COORDINATES
# def coordinate_calcul(x,y,minx,maxx,miny,maxy):
#     new_xy=[]
#     new_xy.append(167+(((x-minx)/(maxx-minx))*1059))
#     new_xy.append(681-(((y-miny)/(maxy-miny))*580))
#     return(new_xy)
# def reverse_coordinate_calcul(x,y,minx,maxx,miny,maxy):
#     new_xy=[]
#     new_xy.append(((x-167)/1059)*(maxx-minx)+minx)
#     new_xy.append(((681-y)/580)*(maxy-miny)+miny)
#     return(new_xy)
def coordinate_calcul(x,y,minx,maxx,miny,maxy):
    '''
    this function takes normalized coordinates of the point(coordinates  on 
    the actual plot) and turns them into coordinates of the point on the window
    x,y:the wanted coordinates;
    minx,maxx:the limits of the x-axis;
    miny,maxy:the limits of the y-axis
    '''
    new_xy=[]
    #the following equations are merely normalizations/linear transformations
    #the constants are approximations of the actual coordinates of the plot in the window
    new_xy.append(167+(((x-minx)/(maxx-minx))*1059)) 
    new_xy.append(669-(((y-miny)/(maxy-miny))*580))
    return(new_xy)
def reverse_coordinate_calcul(x,y,minx,maxx,miny,maxy):
    """
    this function is the reverse of the previous one and therefore
    turns window coordinates into plot coordinates
    """
    new_xy=[]
    new_xy.append(((x-167)/1059)*(maxx-minx)+minx)
    new_xy.append(((669-y)/580)*(maxy-miny)+miny)
    return(new_xy)
def new_xlim_ylim(x,y,minx,maxx,miny,maxy):
    """
    this function takes a point (x,y) which represents where the mouse clicked
    on the screen/window and turns this point into plot coordinates which are later used
    to implement the zoom functionality later on in another function
    """
    a,b=reverse_coordinate_calcul(x,y,minx,maxx,miny,maxy) #plot coordinates of the click
    xx=(maxx-minx)*0.1 #step calculation in x-axis
    yy=(maxy-miny)*0.1 #step calculation in y-axis
    #returns new limits of the x and y-axis which emulates zooming in the plot around the click
    return [a-xx,a+xx,b-yy,b+yy] 
def sortir(w):
    """
    event functions used later on to leave a current window
    """
    w.destroy() 
def srt(event,win):
    """
    event functions used later on to leave a current window
    """
    sortir(win)
def raise_frame(frame):
    """
    function used to make a frame the top/visible one in a window
    """
    frame.tkraise()
def motion(a1,a2,b1,b2,event,win,frame,ph,nrj,xy,l_poscar,phx):
    """
    function used to extract the clicking point of the mouse cursor (providing that
    this point is inside the plot) and builds a new plot with the new axis bounds which are 
    much smaller than the previous ones to make it seem like we zoomed in a specific area
    a1,a2,b1,b2:former limits of x and y-axis
    event:to make this an event function
    ph:image used to represent the points
    nrj,xy:coordinates of the points
    l_poscar:list of vasp written molecules in strings
    phx:image used to represent the points zoomed in
    """
    x, y = event.x, event.y #we extract the click-point
    bornes=reverse_coordinate_calcul(x,y,a1,a2,b1,b2) #we calculate the buonds of the plot
    #we make sure the point is inside the plot
    if bornes[0]>a1 and bornes[0]<a2 and bornes[1]>b1 and bornes[1]<b2:
        win.bind('<Button-1>',nothing) #we stop the zooming process once we zoom in 
        xa1,xa2,xb1,xb2=new_xlim_ylim(x,y,a1,a2,b1,b2) #we calculate the new bounds
        fig1,ax1=plt.rcParams['figure.figsize'] = [15, 15] #dimensions of the plot
        fig1,ax1=plt.subplots() #plot template creation
        ax1.set_xlim([xa1,xa2]) #new x-axis
        ax1.set_ylim([xb1,xb2]) #new y-axis
        ax1.set_xlabel('generation number')
        ax1.set_ylabel('energy[eV/Atom]')
        fig1.suptitle('classification of different structures by their energy and generation number [to quit the window right-click mouse+enter button]')
        frame1=Frame(win,width=1500,height=700) #creating a frame to put the plot in
        frame1.place(relheight=1.0, relwidth=1.0) 
        canvax=FigureCanvasTkAgg(fig1,master=frame1) #embedding the plot in tkinter interface
        canvax.get_tk_widget().pack(side="top",fill='both',expand=True)
        x2=0 #index of the button list
        button_list2=[] #initializing a button list e.g: the list of points on the plot
        new_xyx=[] #new coordinates of the points
        #calculating the new coordinates
        for i in range(0,len(xy)):
            new_xyx.append(coordinate_calcul(xy[i][0],xy[i][1],xa1,xa2,xb1,xb2))
        #calculating the new bounds
        xxa1,xxb1=coordinate_calcul(xa1,xb1,xa1,xa2,xb1,xb2) 
        xxa2,xxb2=coordinate_calcul(xa2,xb2,xa1,xa2,xb1,xb2)
        #creation of the points/buttons and positioning them on the plot
        for i in range(len(new_xyx)):
             #we make sure the points that are put are withing the new plot limits
             #we also give each button the function to show the corresponding molecule
             if new_xyx[i][0]>xxa1 and new_xyx[i][0]<xxa2 and new_xyx[i][1]>xxb2 and new_xyx[i][1]<xxb1:
                button_list2.append(Button(frame1,image=phx,height=10,width=10,borderwidth=0)) 
                button_list2[x2]['command']=partial(letmesee_poscar,i+a1,l_poscar) 
                button_list2[x2].place(x=new_xyx[i][0],y=new_xyx[i][1]) 
                #we add a hovering message that gives the corresponding energy of the point
                CreateToolTip(button_list2[x2],12,text="energy:"+str(nrj[i+a1])+"eV/Atom")
                x2+=1 #we increment the index each time
        #we create a button to come back from the zoom (de-zoom it if you want)
        b2x=Button(frame1,text='back',command=lambda:raise_frame(frame)) 
        b2x.place(x=650,y=50)
        frame['cursor']='arrow'
        raise_frame(frame1) #we finally make the frame with the zoomed plot appear 
    else:
        return #in case the point clicked was outside the plot we don't do anything
def zoom(frame,win,a1,a2,b1,b2,ph,nrj,xy,l_poscar,phx):
    """
    function used to zoom in, it essentially just uses the motion function as an event
    """
    frame['cursor']='target' #we change the cursor to signify that we are in zoom mode
    #when we enter the zoom mode the left-click of the mouse triggers the zoom
    win.bind('<Button-1>',lambda event: motion(a1,a2,b1,b2,event,win,frame,ph,nrj,xy,l_poscar,phx))
def normal_cursor(frame,win):
    """
    used to turn back the cursor when we finish or 
    exit the zoom mode, the nothing function might not be necessary but i found no other way
    to disable the zoom
    """
    frame['cursor']='arrow'
    win.bind('<Button-1>',nothing)
def normal_cursor_event(event,frame,win):
    """
    used to turn back the cursor when we finish or 
    exit the zoom mode, the nothing function might not be necessary but i found no other way
    to disable the zoom
    """
    normal_cursor(frame,win)
def nothing(event):
    return
def generate_plot_generation(xy,nrj,begining_index,l_poscar,value_inside):
    """
    function used to generate energy-generation plot using tkinter
    as an interface and buttons as points in the plot
    """
    img=Image.open('here.gif') #image for the normal points
    ph=ImageTk.PhotoImage(img)
    imgx=Image.open('here2.gif') #image for the zoomed points
    phx=ImageTk.PhotoImage(imgx)
    interval=value_inside.get() #interval chosen
    #ab=str_ab(interval[2:len(interval)-3])
    ab=str_ab(interval) #turn string interval to two numbers
    try:
        a=ab[0]
        b=ab[1]+1
    except:
        return
    new_xyx=[]
    if len(xy)<=10:
        r=len(begining_index)
    else:
        r=10
    for i in range(0,len(xy)):
        new_xyx.append(coordinate_calcul(xy[i][0],xy[i][1],0,r,np.min(nrj),np.max(nrj)))
    win=Toplevel()
    win.title("Rounded Button") 
    fig,ax=plt.rcParams['figure.figsize'] = [15, 15] 
    fig,ax=plt.subplots() 
    ax.set_xlim([a, b]) 
    ax.set_ylim([np.min(nrj),np.max(nrj)])
    ax.set_xlabel('generation number') 
    ax.set_ylabel('energy[eV/Atom]')
    fig.suptitle('classification of different structures by their energy and generation number [to quit the window right-click mouse+enter button]')
    win.geometry("1500x900") 
    win.attributes('-fullscreen', True)
    win.bind('<Button-3>',lambda event:normal_cursor_event(event,frame,win)) #leave zoom
    win.bind('<Return>',lambda event:srt(event,win)) #leave window
    frame=Frame(win,width=1500,height=700)
    frame.place(relheight=1.0, relwidth=1.0)
    canva=FigureCanvasTkAgg(fig,master=frame) 
    canva.get_tk_widget().pack(side="top",fill='both',expand=True)
    button_list=[]
    x=0
    #creation of the points/buttons and positioning them on the plot
    for i in range(len(new_xyx)):
        #we also give each button the function to show the corresponding molecule
        button_list.append(Button(frame,image=ph,height=5,width=5,borderwidth=0)) 
        button_list[x]['command']=partial(letmesee_poscar,i+a,l_poscar) 
        button_list[x].place(x=new_xyx[i][0],y=new_xyx[i][1]) 
        CreateToolTip(button_list[x],12,text="energy:"+str(nrj[i+a])+"eV/Atom")
        x+=1
    #we make a button to enable the zoom mode
    b1xx=Button(frame,text='zoom',command=lambda:zoom(frame,win,a,b,np.min(nrj),np.max(nrj),ph,nrj,xy,l_poscar,phx))
    b1xx.place(x=650,y=50)
    win.update()
    win.mainloop()
def generate_plot_index(xy,nrj,l_res,value_inside):
    """
    function used to generate energy-index plot using tkinter
    as an interface and buttons as points in the plot
    N.B: the structures are ordered in energy value before put on the plot
    """
    img=Image.open('here.gif')
    ph=ImageTk.PhotoImage(img) #image used for points
    interval=value_inside.get() #extracting chosen interval
    ab=str_ab(interval[2:len(interval)-3]) #excluding the parenthesis
    try:
        a=ab[0]
        b=ab[1]
    except:
        return
    win=Toplevel()
    win.title("Rounded Button")
    fig,ax=plt.rcParams['figure.figsize'] = [15, 15]
    plt.rcParams['font.weight'] =1000          
    fig,ax=plt.subplots() 
    ax.set_xlim([a, b]) 
    ax.set_ylim([np.min(nrj),np.max(nrj)])
    ax.set_xlabel('index')
    ax.set_ylabel('energy[eV/Atom]')
    fig.suptitle('classification of different structures by their energy and index number [to quit the window right-click mouse+enter button]')
    win.geometry("1500x900") 
    win.attributes('-fullscreen', True)
    win.bind('<Button-3>',lambda event:normal_cursor_event(event,frame,win))
    win.bind('<Return>',lambda event:srt(event,win))
    frame=Frame(win,width=1500,height=700)
    frame.place(relheight=1.0, relwidth=1.0)
    canva=FigureCanvasTkAgg(fig,master=frame)
    canva.get_tk_widget().pack(side="top",fill='both',expand=True)
    button_list=[]
    x=0
    #we create a list with both index & energy so that when we order it we know the original index
    real_nrj=[]
    nrj2=nrj.copy()
    index=0
    for axx in nrj2:
        real_nrj.append([axx,index+1])
        index+=1
    #ordering the two lists in term of energy from low energy to high energy
    real_nrj.sort()
    nrj2.sort()
    new_xyx=[]
    xyx=[]
    for i in range(len(xy)):
        xyx.append([xy[i][0],nrj2[i]])
    for i in range(a,b+1):
        new_xyx.append(coordinate_calcul(xyx[i][0],xyx[i][1],a,b,np.min(nrj),np.max(nrj)))
    #creation of the points/buttons and positioning them on the plot
    for i in range(len(new_xyx)):
        #we also give each button the function to show the corresponding molecule
        button_list.append(Button(frame,image=ph,height=5,width=5,borderwidth=0))
        button_list[x]['command']=partial(letmesee_res,i+a,l_res) 
        button_list[x].place(x=new_xyx[i][0],y=new_xyx[i][1]) 
        CreateToolTip(button_list[x],12,text="energy:"+str(nrj2[i+a])+"eV/Atom"+"\n"+"index:"+str(real_nrj[i+a][1]))
        x+=1
    win.update()
    win.mainloop()
def generate_plot_xyz(xy,nrj,datalist,file_list,path,value_inside):
    """
    function used to generate energy-index plot using tkinter
    as an interface and buttons as points in the plot, the only difference from the previous 
    that this one takes as an input a list of files (xyz,cif,vasp) and plots them like the res
    file providing that energy is stated
    N.B: the structures are ordered in energy value before put on the plot
    """
    #os.chdir("C:\\Users\\br\\Desktop")
    dir = os.path.dirname(__file__)
    os.chdir(dir)
    img=Image.open('here.gif')
    ph=ImageTk.PhotoImage(img)
    interval=value_inside.get()
    try:
        try:
            a,b=str_ab(interval[2:len(interval)-3])         
        except:
            a,b=str_ab(interval)
    except:
        return
    win=Toplevel()
    win.title("Rounded Button")
    fig,ax=plt.rcParams['figure.figsize'] = [15, 15]
    plt.rcParams['font.weight'] =1000          
    fig,ax=plt.subplots() 
    ax.set_xlim([a, b])
    ax.set_ylim([np.min(nrj),np.max(nrj)])
    ax.set_xlabel('index')
    ax.set_ylabel('energy[eV/Atom]')
    fig.suptitle('classification of different structures by their energy and index number [to quit the window right-click mouse+enter button]')
    win.geometry("1500x900")
    win.attributes('-fullscreen', True)
    #we bind the window so that the right click in the mouse leaves the zoom mode if active
    win.bind('<Button-3>',lambda event:normal_cursor_event(event,frame,win))
    win.bind('<Return>',lambda event:srt(event,win)) 
    frame=Frame(win,width=1500,height=700)
    frame.place(relheight=1.0, relwidth=1.0)
    canva=FigureCanvasTkAgg(fig,master=frame) 
    canva.get_tk_widget().pack(side="top",fill='both',expand=True)
    button_list=[]
    x=0
    real_nrj=[]
    nrj2=nrj.copy()
    index=0
    for axx in nrj2:
        real_nrj.append([axx,file_list[index]])
        index+=1
    real_nrj.sort()
    nrj2.sort()
    new_xyx=[]
    xyx=[]
    for i in range(len(xy)):
        xyx.append([xy[i][0],nrj2[i]])
    for i in range(a,b+1):
        new_xyx.append(coordinate_calcul(xyx[i][0]-1,xyx[i][1],a,b,np.min(nrj),np.max(nrj)))
    os.chdir(path)
    #creation of the points/buttons and positioning them on the plot
    for i in range(len(new_xyx)):
        #we also give each button the function to show the corresponding molecule
        button_list.append(Button(frame,image=ph,height=5,width=5,borderwidth=0)) 
        button_list[x]['command']=partial(view_xyz,real_nrj[i+a][1]) 
        button_list[x].place(x=new_xyx[i][0],y=new_xyx[i][1]) 
        CreateToolTip(button_list[x],12,text="energy:"+str(nrj2[i+a])+"eV/Atom"+"\n"+"filename:"+str(real_nrj[i+a][1])+"\n"+"spacegroup:"+datalist[i+a][2])
        x+=1
    win.update()
    win.mainloop()