#Assignment 3 Question 1

from tkinter import as tk
from tkinter import filedialog as fd
from tkinter import HORIZONTAL, DoubleVar
import cv2
from PIL import Image, ImageTk

class photo_app(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry('1680x800')

        control_frame(self)
        



class control_frame(tk.Frame):
     def __init__(self, parent):
        super().__init__(parent)

        self.pack(side=LEFT,  pady=20)

        #Tkinter Variables
        image_size = DoubleVar()
        image_size.set(100)
        brightness = DoubleVar()
        brightness.set(100)
        contrast = DoubleVar()
        contrast.set(100)

        # Widgets
        self.open_button = Button(self, text='Open File', command=self.open_file)
        self.save_button = Button(self, text='Save File', command='')  # To be implemented
        self.crop_label = Label(self, text='Crop Mode')
        self.crop_toggle = Checkbutton(self, onvalue=True, offvalue=False)
        self.resize_label = Label(self, text='Resize image', padx=10)
        self.resize_scale = Scale(self, variable=self.image_size, from_=1, to=100, orient=HORIZONTAL, command=self.degrade_image_preview)
        self.brightness_label = Label(self, text='Brightness', padx=10)
        self.brightness_scale = Scale(self, variable=self.brightness, from_=1, to=200, orient=HORIZONTAL)
        self.contrast_label = Label(self, text='Contrast', padx=10)
        self.contrast_scale = Scale(self, variable=self.contrast, from_=1, to=200, orient=HORIZONTAL)

        # Grid Layout
        self.open_button.grid(row=0, column=0, padx=10, pady=10)
        self.save_button.grid(row=0, column=1, padx=10, pady=10)
        self.crop_label.grid(row=1, column=0, padx=10, pady=10)
        self.crop_toggle.grid(row=1, column=1, padx=10, pady=10)
        self.resize_label.grid(row=2, column=0, columnspan=2, padx=10)
        self.resize_scale.grid(row=3, column=0, columnspan=2, padx=10)
        self.brightness_label.grid(row=4, column=0, columnspan=2, padx=10)
        self.brightness_scale.grid(row=5, column=0, columnspan=2, padx=10)
        self.contrast_label.grid(row=6, column=0, columnspan=2, padx=10)
        self.contrast_scale.grid(row=7, column=0, columnspan=2, padx=10)

def open_file(self):
        file_path = fd.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.image = cv2.imread(file_path)
            self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

            # Resize for thumbnail preview
            resized = cv2.resize(self.image_rgb, (400, 300))
            img_pil = Image.fromarray(resized)
            img_tk = ImageTk.PhotoImage(img_pil)

            if hasattr(self, 'img_label'):
                self.img_label.config(image=img_tk)
                self.img_label.image = img_tk
            else:
                self.img_label = tk.Label(self, image=img_tk)
                self.img_label.image = img_tk
                self.img_label.grid(row=8, column=0, columnspan=2, pady=10)

    def degrade_image_preview(self, scale_value):
        # Placeholder method for slider callback
        # You can implement progressive degradation of the image here
        pass

    def save_file(self):
        # Placeholder for save functionality
        pass


class file_frame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        pass
        #scroller = Scrollbar(file_frame, orient='horizontal')
        #scroller.pack(side='bottom')




if __name__=="__main__":
    app = photo_app()
    app.mainloop()
