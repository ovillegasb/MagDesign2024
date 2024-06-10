from tkinter import Toplevel,Label,SOLID,LEFT
'''@source of the class and CreateToolTip function: squareRoot17(stackoverflow username)'''
'''Here we create an object Hover that acts as a message that appears when we hover a specific widget'''
class Hover:
    def __init__(self,b,size=8,text=None):
        self.widget=b #the widget where the message appears on
        self.size=size #the size of the text inside the message
        self.x=0 #coordinates of the message
        self.y=0 #coordinates of the message
        self.text=text #the text inside the message
        self.win=None #the window that holds the message
    def appear(self): #method for the message to appear
        if self.win or not self.text: #to avoid errors
            return
        x=y=0
        #we get the coordinates of the widget to put the message beside it
        x=x+self.widget.winfo_rootx()+25 
        y=y+self.widget.winfo_rooty()+25
        self.x=x
        self.y=y        
        self.win=tw=Toplevel(self.widget) #we create the window
        tw.wm_overrideredirect(1) #this function deletes the window manager of the window
        tw.wm_geometry("+%d+%d" % (x, y)) #this function pads the window at x,y coordinates
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", str(self.size), "normal")) #we create the label
        label.pack(ipadx=1)
    def disappear(self): #method for the message to disappear
        tw=self.win
        self.win=None
        if tw:
            tw.destroy() #we destroy the window
'''here we created two versions of the function that creates a hover message'''
"""version1: the message appears when we pass the widget with the cursor and disappears
when we leave the widget"""
def CreateToolTip(b,size,text):
    hover=Hover(b,size,text)
    def pop(event): #pop=as in appear
        hover.appear()
    def dip(event): #dip=as in disappear
        hover.disappear()
    #we bind the events to the widget
    b.bind('<Enter>',pop)
    b.bind('<Leave>',dip)
"""version2: the message appears when we pass the widget with the cursor and disappears
when we click on the widget"""
def CreateHover(b,size,text):
    hover=Hover(b,size,text) 
    hover.appear()
    def leave(event):
        hover.disappear() 
    b.bind('<Button>',leave)

    

        
        