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
   def __init__(self, top = 0, left  = 0, bottom  = 0, right  = 0, text = "" ):
      self.top = top
      self.left = left
      self.bottom = bottom
      self.right = right
      self.centerx = (left + right) / 2
      self.centery = (top + bottom) / 2
      self.text = text
      
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
        self.guiButtons = []
        self.guiCenters = []
        self.canvas = Canvas(self, cursor="cross",
                             bg="black", highlightthickness=0)
        
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        
        self.start_x = None
        self.start_y = None
        self.rect = None

        # bind buttons
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.bind("<Escape>",lambda e: self.destroy())
        

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
    
    def click_button(self, button):
        global slave_hwld
        win32gui.SetForegroundWindow(slave_hwld)
        time.sleep(.1)
        pyautogui.click(button.centerx, button.centery)
        win32gui.SetForegroundWindow(self.overlay_handle)
        time.sleep(.1)  
        
    def on_button_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        self.entry_var = StringVar()
        self.wait_var = StringVar()
        self.entry = Entry(self, textvariable=self.entry_var)
        self.entry.pack( )
        self.entry.focus_set()
        # Bind the Enter key to a function that sets self.entry_var
        self.entry.bind('<Return>', lambda _: self.wait_var.set(""))

        # Wait for the user to press the Enter key
        self.entry.wait_variable(self.wait_var)
        button_text = self.entry.get()
        self.entry.destroy()
        

        # Calculate coordinates of the selected area
        top_left = (self.start_x, self.start_y)
        top_right = (end_x, self.start_y)
        bottom_left = (self.start_x, end_y)
        bottom_right = (end_x, end_y)

        # Print coordinates
        print(f"Top Left: {top_left}")
        print(f"Top Right: {top_right}")
        print(f"Bottom Left: {bottom_left}")
        print(f"Bottom Right: {bottom_right}")
        print(f"Button Text: {button_text}")
        
        # Create a button
        self.buttons.append(InterfaceButton(top = self.start_y, 
                                            left = self.start_x, 
                                            bottom = end_y, 
                                            right = end_x, 
                                            text = button_text))
        self.guiButtons.append(Button(self, text=button_text, bg="white", bd=0))
        self.guiButtons[-1].pack(side=tk.LEFT)
        
        # draw a dot in the center of the button
        self.guiCenters.append(self.canvas.create_oval(self.buttons[-1].centerx - 5, self.buttons[-1].centery - 5, 
                                                       self.buttons[-1].centerx + 5, self.buttons[-1].centery + 5, 
                                                       fill="red"))

        # Add this line after self.guiButtons[-1].pack(side=tk.LEFT)
        self.button_click()
        
if __name__ == "__main__":
    # get hwld for chrome
    win32gui.EnumWindows(enum_cb, toplists)
    
    for hwld, title in winlist:
        if "chrome" in title.lower():
            slave_hwld = hwld
            break

    if(slave_hwld == 0):
        print("Chrome not found")
    
    overlay = ScreenOverlay()
    overlay.mainloop()
    
    
  
    

