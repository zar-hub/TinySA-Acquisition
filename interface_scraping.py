import tkinter as tk
from tkinter import *
import pyautogui
import win32gui, time

slave_hwld = 0

# from PIL import ImageGrab
winlist, toplists = [], []

def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

class InterfaceButton():
    def __init__(self, x=0, y=0, text = "" ):
        self.x = x
        self.y = y
        self.text = text
    def click(self):
        global slave_hwld
        # if not foreground, bring to foreground
        if win32gui.GetForegroundWindow() != slave_hwld:
            win32gui.SetForegroundWindow(slave_hwld)
            time.sleep(.1)
        pyautogui.click(self.x, self.y)
        
      
class ScreenOverlay(tk.Tk):
    def __init__(self):
        super().__init__()
    
        self.overlay_handle = self.winfo_id()
        self.title("Screen Overlay")
        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.4)
        self.configure(bg='black')

        # store the buttons
        self.buttons = []
        
        # add wigets
        self.guiCenters = []
        self.guiButtons = []
        self.canvas = Canvas(self, cursor="cross",
                             bg="black", highlightthickness=0)
        
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        
        # bind buttons
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.bind("<Escape>",lambda e: self.destroy())
        

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # this is a trick that pops up a form until enter is pressed
        self.entry_var = StringVar()
        self.wait_var = StringVar()
        self.entry = Entry(self, textvariable=self.entry_var)
        self.entry.pack( )
        self.entry.focus_set()
        # when enter is pressed, set the wait variable 
        self.entry.bind('<Return>', lambda _: self.wait_var.set(""))

        # then it waits for enter to be pressed and destroys the entry
        self.entry.wait_variable(self.wait_var)
        button_text = self.entry.get()
        self.entry.destroy()

        # Print coordinates
        print(f"x: {self.start_x}")
        print(f"y: {self.start_y}")
        print(f"text: {button_text}")
        
        # Create a button
        self.buttons.append(InterfaceButton(x=self.start_x, y=self.start_y, text = button_text))
        self.guiButtons.append(Button(self, text=button_text, bg="white", bd=0))
        self.guiButtons[-1].pack(side=tk.LEFT)
        
        # draw a dot in the center of the button
        self.guiCenters.append(self.canvas.create_oval(self.buttons[-1].x - 5, self.buttons[-1].y - 5, 
                                                       self.buttons[-1].x + 5, self.buttons[-1].y + 5, 
                                                       fill="red"))
        
if __name__ == "__main__":
    # get hwld for chrome
    win32gui.EnumWindows(enum_cb, toplists)
    
    for hwld, title in winlist:
        if "arinst" in title.lower():
            slave_hwld = hwld
            break

    if(slave_hwld == 0):
        print("Arinst not found...")
        raise OSError("device not found")
    
    # resize the slave window
    win32gui.MoveWindow(slave_hwld, -10, 0, 960, 540, True)
    overlay = ScreenOverlay()
    overlay.mainloop()
    
    # save the buttons
    print("Saving buttons...")
    with open("arinstInterface.txt", "w") as f:
        for button in overlay.buttons:
            f.write(f"{button.x},{button.y},{button.text}\n")
    
    
  
    

