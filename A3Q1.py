#Assignment 3 Question 1

from tkinter import *
from tkinter import filedialog as fd
from PIL import Image, ImageTk
import cv2
import numpy as np


class photo_app(Tk):
    def __init__(self):
        super().__init__()

        self.geometry('1680x800')

        # Layout containers
        self.control_panel = control_frame(self)
        self.control_panel.pack(side=LEFT, padx=10, pady=10, fill=Y)

        self.image_frame = Frame(self)
        self.image_frame.pack(side=LEFT, padx=10, pady=10, expand=True)

        self.control_panel.set_image_frame(self.image_frame)


class control_frame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.image = None
        self.image_rgb = None
        self.cropped_image = None
        self.crop_start = None
        self.crop_end = None
        self.image_frame = None
        self.canvas = None
        self.rect = None

        # Tkinter Variables
        self.image_size = DoubleVar(value=100)
        self.brightness = DoubleVar(value=100)
        self.contrast = DoubleVar(value=100)
        self.preview_resize_var = DoubleVar(value=100)

        # Widgets
        self.open_button = Button(self, text='Open File', command=self.open_file)
        self.save_button = Button(self, text='Save File', command=self.save_file)  # to add feature
        self.crop_label = Label(self, text='Crop Mode')
        self.crop_toggle = Checkbutton(self, onvalue=True, offvalue=False)
        self.resize_label = Label(self, text='Resize Cropped Preview (%)', padx=10)
        self.resize_slider = Scale(self, from_=10, to=200, orient=HORIZONTAL,variable=self.preview_resize_var, command=self.update_preview_resize)
        self.brightness_label = Label(self, text='Brightness', padx=10)
        self.brightness_scale = Scale(self, variable=self.brightness, from_=1, to=200, orient=HORIZONTAL)
        self.contrast_label = Label(self, text='Contrast', padx=10)
        self.contrast_scale = Scale(self, variable=self.contrast, from_=1, to=200, orient=HORIZONTAL)

        # Grid Layout
        self.open_button.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        self.save_button.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
        self.crop_label.grid(row=2, column=0, padx=10, pady=10)
        self.crop_toggle.grid(row=2, column=1, padx=10, pady=10)
        self.resize_label.grid(row=3, column=0, columnspan=2, padx=10)
        self.resize_slider.grid(row=4, column=0, columnspan=2, padx=10)
        self.brightness_label.grid(row=5, column=0, columnspan=2, padx=10)
        self.brightness_scale.grid(row=6, column=0, columnspan=2, padx=10)
        self.contrast_label.grid(row=7, column=0, columnspan=2, padx=10)
        self.contrast_scale.grid(row=8, column=0, columnspan=2, padx=10)

    def set_image_frame(self, frame):
        self.image_frame = frame

    def open_file(self):
        file_path = fd.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.image = cv2.imread(file_path)
            self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

            self.display_image()

    def display_image(self):
        img = cv2.resize(self.image_rgb, (600, 400))
        self.displayed_image = img
        img_pil = Image.fromarray(img)
        self.img_tk = ImageTk.PhotoImage(img_pil)

        if not self.canvas:
            self.canvas = Canvas(self.image_frame, width=600, height=400)
            self.canvas.pack(side=LEFT, padx=10)
            self.canvas.bind("<ButtonPress-1>", self.start_crop)
            self.canvas.bind("<B1-Motion>", self.draw_crop_rect)
            self.canvas.bind("<ButtonRelease-1>", self.finish_crop)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=NW, image=self.img_tk)

    def start_crop(self, event):
        self.crop_start = (event.x, event.y)
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red')

    def draw_crop_rect(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.crop_start[0], self.crop_start[1], event.x, event.y)

    def finish_crop(self, event):
        self.crop_end = (event.x, event.y)
        x1, y1 = self.crop_start
        x2, y2 = self.crop_end

        scale_x = self.image.shape[1] / 600
        scale_y = self.image.shape[0] / 400
        x1, x2 = sorted([int(x1 * scale_x), int(x2 * scale_x)])
        y1, y2 = sorted([int(y1 * scale_y), int(y2 * scale_y)])

        self.cropped_image = self.image[y1:y2, x1:x2]
        self.update_preview_resize(self.preview_resize_var.get())

    def update_preview_resize(self, val):
        if self.cropped_image is not None and self.image_frame:
            try:
                scale_percent = float(val)
                width = int(self.cropped_image.shape[1] * scale_percent / 100)
                height = int(self.cropped_image.shape[0] * scale_percent / 100)
                resized = cv2.resize(self.cropped_image, (width, height), interpolation=cv2.INTER_AREA)

                img_pil = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
                img_tk = ImageTk.PhotoImage(img_pil)

                if hasattr(self, 'preview_label'):
                    self.preview_label.config(image=img_tk)
                    self.preview_label.image = img_tk
                else:
                    self.preview_label = Label(self.image_frame, image=img_tk)
                    self.preview_label.image = img_tk
                    self.preview_label.pack(side=LEFT, padx=10)
            except Exception as e:
                print("Error resizing preview:", e)

    def save_file(self):
        pass  # Placeholder for export logic


if __name__ == "__main__":
    app = photo_app()
    app.mainloop()

