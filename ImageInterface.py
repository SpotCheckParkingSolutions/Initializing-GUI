import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk, ImageDraw
from tkinter import messagebox
import math

# initialize app 
parking_app = tk.Tk()
parking_app.eval('tk::PlaceWindow %s center' % parking_app.winfo_toplevel())

# initialize global variables
spot_array = []
name_array = []
canvas = None
f = None
spot = None
file_counter = 1
spot_counter = 1
processed = False 


class Spot: # 'Spot' class; holds data for each processed spot by maintaining pointers to respective object attributes.  

    def __init__(self, name):

        self.id = None
        self.type = None
        self.verify = None
        self.name = name
        self.name_reference = None
        self.array = []
        self.points_array = []
        self.line_array = []

    def id_get(self):
        return self.id

    def type_get(self):
        return self.spot_type

    def verify_get(self):
        return self.verify

    def name_get(self):
        return self.name

    

def finish_cb(): # 'finish' button callback function

    global f, file_counter, spot_array 

    for spot in spot_array: # write the data of each spot object to an existing file
        f = open("camera_data" + str(file_counter) + ".txt", "a+")
        f.write(spot.id + " | " + spot.type + " | " + spot.verify + " | " + str(spot.array) + "\n")
        
    f.close()
    f = None
    file_counter += 1
    

def process_cb(): # 'process spot' button callback function
    
    global id_entry, spot_typeEntry, verify_entry, spot, spot_array, processed

    if spot != None:

        # assign respective Spot object attributes to the current entry values
        spot.id = str(id_entry.get())
        spot.type = str(spot_typeEntry.get())
        spot.verify = str(verify_entry.get())
        spot_array.append(spot)

        #clear entry fields
        id_entry.delete(0, END)
        spot_typeEntry.delete(0, END)
        verify_entry.delete(0, END)
    
        spot = None
        processed = True


def selection_tool(event): # selection tool function (how the points and lines are plotted).
    
    global spot, spot_counter

    # initialize a new Spot object, assuming there isn't an unprocessed spot currently being processed
    if spot == None:
        name = "Spot " + str(spot_counter)
        spot = Spot(name)
        spot_counter += 1
        processed = False
    
    if len(spot.array) < 4:        
        x, y = event.x, event.y
        point = canvas.create_rectangle(x, y, x, y)
        spot.points_array.append(point)
        spot.array.append((x,y))

    # if an attempt to add a fifth point is made before the previous spot has been processed, display an error message
    else:
        tk.messagebox.showerror("Process Error","Please Process Previous Spot Before Attempting to Continue")


    # system for creating lines that connect the four corners of the points to create a box. Kinda sketch but works. 
    if len(spot.array) >= 2:
            
        line = canvas.create_line(spot.array[len(spot.array) - 2][0], spot.array[len(spot.array) - 2][1], spot.array[-1][0], spot.array[-1][1])
        spot.line_array.append(line)
        
        if len(spot.array) == 4:
            line = canvas.create_line(spot.array[0][0], spot.array[0][1], spot.array[-1][0], spot.array[-1][1])
            spot.line_array.append(line)

            min_x = 100000000000
            min_y = 100000000000
            
            '''
            Turns out its really hard to determine where the center of a box is for all general cases where the
            orientation of the box can vary. As such, this code simply determines the top left corner of the box,
            and places a label for the spot there (so that its name can be referenced for deletion).
            '''
            for i in range(len(spot.array)):

                if spot.array[i][0] < min_x:
                    min_x = spot.array[i][0]

                if spot.array[i][1] < min_y:
                    min_y = spot.array[i][1]
                
                
            
            spot_name = canvas.create_text(min_x + 20, min_y + 20, font = ('Helvetica', 12), text = str(spot.name_get()))
            spot.name_reference = spot_name
            


def undo_cb(): # 'undo' button callback function 

    global spot

    if spot != None:

        if spot.name_reference != None:
            canvas.delete(spot.name_reference)
            spot.name_reference = None
        
        # delete edge incident with point that was just deleted, assuming there there is more than one point
        if len(spot.array) >= 1:
            if len(spot.array) == 1:
                canvas.delete(spot.points_array.pop())
                spot.array.pop()
            
            elif len(spot.array) == 4:
                canvas.delete(spot.line_array.pop())
                canvas.delete(spot.line_array.pop())
                canvas.delete(spot.points_array.pop())
                spot.array.pop()
            
            else:
                canvas.delete(spot.points_array.pop())
                spot.array.pop()
                canvas.delete(spot.line_array.pop())
            
def delete_cb():

    global spot_array, delete_entry, processed

    '''
    assuming there has been at least one spot processed, delete all instances of the specified object from the canvas,
    and remove the respective Spot object from the list of spots that will ultimately be written to the file
    '''

    if len(spot_array) != 0 and processed == True:
    
        for spot in spot_array:
            if spot.name_get() == delete_entry.get():
                for i in range(len(spot.array)):
                    canvas.delete(spot.line_array.pop())
                    canvas.delete(spot.points_array.pop())

                canvas.delete(spot.name_reference)
                spot_array.remove(spot)

    else:
        tk.messagebox.showerror("Process Error","Please Process Previous Spot Before Attempting to Continue")




def image_select_cb(): # 'image selection' button callback function 

    # prompt the user for the image file they wish to use
    path = tk.filedialog.askopenfilename()
    image = Image.open(path)
    photo = ImageTk.PhotoImage(image)
    photo_width, photo_height = image.size
    photo.image = photo
    
    '''
    If the 'Upload' button has been invoked, create a new blank file which will be written to. From here, create the
    entries where the Spot attributes are listed, as well as the "Process Spot" button, "Delete" button, and "Undo"
    button.
    '''
    global canvas, f, file_counter
    
    f = open("camera_data" + str(file_counter) + ".txt", "w+")
    
    canvas = tk.Canvas(parking_app, width = photo_width, height = photo_height)
    canvas.grid(row = 2, column = 0, padx = 5, pady = 10, sticky = N+E+W+S)
    canvas.bind('<Button-1>', selection_tool)
    canvas.create_image(0, 0, anchor = NW, image = photo)

    global id_entry, verify_entry, spot_typeEntry, delete_entry

    # this is literally just initializing all the labels/buttons. Nothing special
    tools_frame = tk.Frame(parking_app, width = 40, highlightbackground= 'light blue', highlightcolor = 'light blue', highlightthickness = 5)

    process_button = tk.Button(tools_frame, text = "Process Spot", command = process_cb)
    process_button.grid(row = 0, column = 0, pady = 5)
    
    spot_typeLabel = tk.Label(tools_frame, text = "Enter Spot Type:")
    spot_typeLabel.grid(row = 1, column = 0)
    spot_typeEntry = tk.Entry(tools_frame)
    spot_typeEntry.grid(row = 2, column = 0)
 
    verify_label = tk.Label(tools_frame, text = "Verify Filled (Boolean):")
    verify_label.grid(row = 3, column = 0)
    verify_entry = tk.Entry(tools_frame)
    verify_entry.grid(row = 4, column = 0)

    id_label = tk.Label(tools_frame, text = "Specify Camera ID:")
    id_label.grid(row = 5, column = 0)
    id_entry = tk.Entry(tools_frame)
    id_entry.grid(row = 6, column = 0)

    blank_label = tk.Label(tools_frame, text = '')
    blank_label.grid(row = 7, column = 0)
    
    delete_button = tk.Button(tools_frame, text = "Delete Spot", command = delete_cb)
    delete_button.grid(row = 8, column = 0)
    delete_entry = tk.Entry(tools_frame)
    delete_entry.grid(row = 9, column = 0)

    undo_button = tk.Button(tools_frame, text = "Undo", command = undo_cb)
    undo_button.grid(row = 10, column = 0, pady = 10)
    
    tools_frame.grid(row = 2, column = 4)

    parking_app.eval('tk::PlaceWindow %s center' % parking_app.winfo_toplevel())

# set up initial GUI labels and buttons. This includes 'image select' label/button and 'finish' label/button
parking_app.title("SpotCheck Initializer")
frame = tk.Frame(parking_app, width = 200)
tk.Label(frame, text = "Select an Image for Processing:").grid(row = 1, column = 0,sticky = W,  pady = 20, padx = 10)
tk.Button(frame, text='Image Upload', command=image_select_cb).grid(row=1, column=1, sticky = W, pady = 20, padx = 5)
tk.Label(frame, text = "Send Data: ").grid(row = 1, column = 2,sticky = W,  pady = 20, padx = 10)
tk.Button(frame, text='Finish', command=finish_cb).grid(row=1, column=3, sticky = W, pady = 20, padx = 5)

frame.grid(row = 0, column = 0, sticky = W, padx = 10, pady = 10)



