#Assignment 3 Question 1

from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import font
from PIL import Image, ImageTk
import cv2
import numpy as np


class photo_app(Tk):




    def __init__(self):
        super().__init__()


        self.image = None
        self.image_rgb = None
        self.crop_mode = BooleanVar()
        self.edited_image = None
        self.crop_start = None
        self.crop_end = None
        self.image_frame = None
        self.canvas = None
        self.rect = None
        self.brightness = 0
        self.contrast = 1.0
        self.colourmode = None

        # Tkinter Variables
        self.image_size = DoubleVar(value=100)
        self.brightness = DoubleVar(value=100)
        self.contrast = DoubleVar(value=100)
        self.preview_resize_var = DoubleVar(value=100)

        self.title("TKinter/OpenCV Image Editor")

        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry('%dx%d+0+0' % (width,height))


        # Layout containers
        
        self.title_panel = title_frame(self)
        self.title_panel.pack(side=TOP, fill=X)

        self.control_panel = control_frame(self)
        self.control_panel.pack(side=LEFT, padx=10, pady=10, fill=Y)

        self.image_frame = preview_frame(self)
        self.image_frame.pack(side=LEFT, padx=10, pady=10, expand=True, fill=BOTH)
        self.set_image_frame(self.image_frame)

        #Enable Key/Mouse Binds
        self.key_binds()


    def key_binds(self):

        #Canvas Mouse Binds
        self.image_frame.original_image_panel.bind('<ButtonPress-1>', self.start_crop)
        self.image_frame.original_image_panel.bind('<B1-Motion>', self.draw_crop_rect)
        self.image_frame.original_image_panel.bind('<ButtonRelease-1>', self.finish_crop)

        #Keyboard Shortcuts
        self.bind_all('<Control-o>', lambda event: self.open_file())
        self.bind_all('<Control-s>', lambda event: self.save_file())
        self.bind_all('<Control-z>', lambda event: self.undo())
        self.bind_all('<Control-y>', lambda event: self.redo())
        self.bind_all('<c>', lambda event: self.set_colour_mode())
        self.bind_all('<g>', lambda event: self.set_greyscale_mode())

    def open_file(self):
        file_path = fd.askopenfilename(filetypes=[('Image files', '*.jpg *.jpeg *.png')])
        if file_path:
            self.image = cv2.imread(file_path)
            self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.edited_image = self.image

            self.display_image()


    def save_file(self):
        if self.edited_image is None:
            messagebox.showwarning('No Image', 'No cropped image to save.')
            return
        file_path = fd.asksaveasfilename(defaultextension='.png',filetypes=[('PNG files', '*.png'),('JPEG files', '*.jpg'),('All files', '*.*')])
        if not file_path:
            return
        try:
            img_pil = Image.fromarray(self.edited_image)
            img_pil.save(file_path)
            messagebox.showinfo('Save Successful', f'Image saved to:\n{file_path}')
        except Exception as e:
            messagebox.showerror('Save Error', f'Failed to save image: {e}')

    def set_image_frame(self, frame):
        self.image_frame = frame

    def display_image(self):
        img = cv2.resize(self.image_rgb, (600, 400))
        self.displayed_image = img
        img_pil = Image.fromarray(img)
        self.img_tk = ImageTk.PhotoImage(img_pil)

        self.image_frame.original_image_panel.delete('all')
        self.image_frame.original_image_panel.create_image(0, 0, anchor=NW, image=self.img_tk)
        self.update_preview()

    def start_crop(self, event):
        if self.rect:
            self.rect = None
        if self.crop_mode.get():
            self.crop_start = (event.x, event.y)
            self.rect = self.image_frame.original_image_panel.create_rectangle(event.x, event.y, event.x, event.y, outline='red')

    def draw_crop_rect(self, event):
        if self.rect:
            self.image_frame.original_image_panel.coords(self.rect, self.crop_start[0], self.crop_start[1], event.x, event.y)

    def finish_crop(self, event):
        if self.crop_mode.get():
            self.crop_end = (event.x, event.y)
            x1, y1 = self.crop_start
            x2, y2 = self.crop_end

            scale_x = self.image.shape[1] / 600
            scale_y = self.image.shape[0] / 400
            x1, x2 = sorted([int(x1 * scale_x), int(x2 * scale_x)])
            y1, y2 = sorted([int(y1 * scale_y), int(y2 * scale_y)])

            self.image_frame.original_image_panel.delete(self.rect)
            self.edited_image = self.image[y1:y2, x1:x2]
            self.update_preview()

    def update_preview(self, _=None):
        if self.edited_image is not None and self.image_frame:
            try:
                scale_percent = float(self.preview_resize_var.get())
                width = int(self.edited_image.shape[1] * scale_percent / 100)
                height = int(self.edited_image.shape[0] * scale_percent / 100)
                resized = cv2.resize(self.edited_image, (width, height), interpolation=cv2.INTER_AREA)
                resized = self.adjust_image(resized)

                img_pil = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
                img_tk = ImageTk.PhotoImage(img_pil)

                self.image_frame.edited_image_panel.config(image=img_tk)
                self.image_frame.edited_image_panel.image = img_tk
        
            except Exception as e:
                print('Error resizing preview:', e)

    def adjust_image(self, img):
        if img is None:
            return None

        brightness = self.control_panel.brightness_scale.get() - 100
        contrast = self.control_panel.contrast_scale.get() / 100

        adjusted_img = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)

        if self.colourmode == 'G':
            adjusted_img = cv2.cvtColor(adjusted_img, cv2.COLOR_RGB2GRAY)
        else:
            pass

        return adjusted_img




    def set_colour_mode(self, _=None):
        self.colourmode = 'C'
        self.update_preview()

    def set_greyscale_mode(self, _=None):
        self.colourmode = 'G'
        self.update_preview()


    def reset_image(self):
        self.edited_image = self.image
        self.image_size.set(100)
        self.display_image()

class title_frame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        title_font = font.Font(family='Arial', size=25)
        self.title_label = Label(text='TKinter/OpenCV Image Editor', font=title_font)
        self.title_label.pack()

class control_frame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        #Widgets
        self.open_button = Button(self, text='Open File', command=parent.open_file)
        self.save_button = Button(self, text='Save File', command=parent.save_file)
        self.crop_label = Label(self, text='Crop Mode')
        self.crop_toggle = Checkbutton(self, variable=parent.crop_mode)
        self.resize_label = Label(self, text='Resize image', padx=10)
        self.resize_scale = Scale(self, from_=10, to=200, variable=parent.preview_resize_var, orient=HORIZONTAL,command=parent.update_preview)
        self.brightness_label = Label(self, text='Brightness', padx=10)
        self.brightness_scale = Scale(self, variable=parent.brightness, from_ = 10, to = 200, orient=HORIZONTAL,command=parent.update_preview)
        self.contrast_label = Label(self, text='Contrast', padx=10)
        self.contrast_scale = Scale(self, variable=parent.contrast, from_ = 10, to = 200, orient=HORIZONTAL,command=parent.update_preview)
        self.colour_label = Label(self, text='Colouring', padx=10)
        self.colour_button = Button(self, text='Colour', command=parent.set_colour_mode)
        self.greyscale_button = Button(self, text='Greyscale', command=parent.set_greyscale_mode)
        self.reset_button = Button(self, text='Reset Image', command=parent.reset_image)

        #Control Panel Grid Layout
        self.open_button.grid(row=0, column=0, padx=10, pady=10, sticky=NW)
        self.save_button.grid(row=0, column=1, padx=10, pady=10)
        self.crop_label.grid(row=1, column=0, padx=10, pady=10)
        self.crop_toggle.grid(row=1, column=1, padx=10, pady=10)
        self.resize_label.grid(row=2, column=0, columnspan=2, padx=10)
        self.resize_scale.grid(row=3, column=0, columnspan=2, padx=10)
        self.brightness_label.grid(row=4, column=0, columnspan=2, padx=10)
        self.brightness_scale.grid(row=5, column=0, columnspan=2, padx=10)
        self.contrast_label.grid(row=6, column=0, columnspan=2, padx=10)
        self.contrast_scale.grid(row=7, column=0, columnspan=2, padx=10)
        self.colour_label.grid(row=8, column=0, columnspan=2, padx=10, pady=10)
        self.colour_button.grid(row=9, column=0, padx=10)
        self.greyscale_button.grid(row=9, column=1, padx=10)
        self.reset_button.grid(row=10, column=0, columnspan=2, padx=10, pady=30)

class preview_frame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        #Widgets
        self.original_label = Label(self, text='Original Image')
        self.original_image_panel = Canvas(self, width=600, height=400)
        self.edited_label = Label(self, text='Edited Image')
        self.edited_image_panel = Label(self, image=None)

        #Layout
        self.original_label.grid(row=0, column=0)
        self.edited_label.grid(row=0, column=1)
        self.original_image_panel.grid(row=1, column=0)        
        self.edited_image_panel.grid(row=1, column=1)



if __name__=='__main__':
    app = photo_app()
    app.mainloop()
