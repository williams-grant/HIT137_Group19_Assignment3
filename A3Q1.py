#Assignment 3 Question 1

from tkinter import *
from tkinter import filedialog as fd


class photo_app(Tk):
    def __init__(self):
        super().__init__()

        self.geometry('1680x800')

        #Do something
        control_frame(self)
        



class control_frame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

		# Put this sucker on the screen
        self.pack(side=LEFT,  pady=20)

        image_size = DoubleVar()
        image_size.set(100)
        brightness = DoubleVar()
        brightness.set(100)
        contrast = DoubleVar()
        contrast.set(100)

		# Create a few buttons
        self.open_button = Button(self, text='Open File', command='')
        self.save_button = Button(self, text='Save File', command='')
        self.crop_label = Label(self, text='Crop Mode')
        self.crop_toggle = Checkbutton(self, onvalue=True, offvalue=False)
        self.resize_label = Label(self, text='Resize image', padx=10)
        self.resize_scale = Scale(self, variable=image_size, from_ = 1, to = 200,  orient=HORIZONTAL)
        self.brightness_label = Label(self, text='Brightness', padx=10)
        self.brightness_scale = Scale(self, variable=brightness, from_ = 1, to = 200, orient=HORIZONTAL)
        self.contrast_label = Label(self, text='Contrast', padx=10)
        self.contrast_scale = Scale(self, variable=contrast, from_ = 1, to = 200, orient=HORIZONTAL)


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


class file_frame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        pass
        #scroller = Scrollbar(file_frame, orient='horizontal')
        #scroller.pack(side='bottom')




if __name__=="__main__":
    app = photo_app()
    app.mainloop()
