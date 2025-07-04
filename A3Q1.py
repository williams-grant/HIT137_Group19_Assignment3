#Assignment 3 Question 1

from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import font
from PIL import Image, ImageTk
import cv2

class PhotoApp(Tk):
    def __init__(self):
        super().__init__()

        #Image variables
        self.image = None
        self.image_rgb = None
        self.edited_image = None
        self.resized = None

        #Canvas variables
        self.canvas = None
        self.max_canvas_x = 600
        self.max_canvas_y = 400
        self.canvas_x = 0
        self.canvas_y = 0
        self.canvas_scale = 1


        #tkinter Scale variables
        self.scale_min = 10
        self.scale_max = 200

        self.default_brightness = 100
        self.default_contrast = 100
        self.default_resize_var = 100

        #Image adjustment variables
        self.crop_mode = BooleanVar()
        self.crop_start = None
        self.crop_end = None
        self.rect = None
        self.brightness = DoubleVar(value=self.default_brightness)
        self.contrast = DoubleVar(value=self.default_contrast)
        self.preview_resize_var = DoubleVar(value=self.default_resize_var)
        self.colourmode = None
        self.brightness_conversion = 100
        self.contrast_conversion = 100

        self.undo_list = []
        self.redo_list = []

        #Set up the tkinter window
        self.title("TKinter/OpenCV Image Editor")
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry('%dx%d+0+0' % (width,height))


        # Build layout using frame classes
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

        #Scale Mouse Binds
        self.control_panel.resize_scale.bind("<ButtonPress-1>", self.set_undo_point)
        self.control_panel.brightness_scale.bind("<ButtonPress-1>", self.set_undo_point)
        self.control_panel.contrast_scale.bind("<ButtonPress-1>", self.set_undo_point)

        #Colour Mode Mouse Binds
        self.control_panel.colour_button.bind("<ButtonPress-1>", self.set_undo_point)
        self.control_panel.greyscale_button.bind("<ButtonPress-1>", self.set_undo_point)

        #Keyboard Shortcuts
        self.bind_all('<Control-o>', lambda event: self.open_file())
        self.bind_all('<Control-s>', lambda event: self.save_file())
        self.bind_all('<Control-z>', lambda event: self.undo_change())
        self.bind_all('<Control-y>', lambda event: self.redo_change())
        self.bind_all('<c>', lambda event: self.set_colour_mode())
        self.bind_all('<g>', lambda event: self.set_greyscale_mode())


    def open_file(self):
        file_path = fd.askopenfilename(filetypes=[('Image files', '*.jpg *.jpeg *.png')])
        if file_path:
            self.image = cv2.imread(file_path)

            if self.image is None:
                messagebox.showerror('Error','File selected was not an image file.')
                return

            self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.edited_image = self.image

            self.display_image()


    def save_file(self):
        if self.edited_image is None:
            messagebox.showwarning('No Image', 'No image to save.')
            return
        file_path = fd.asksaveasfilename(defaultextension='.png',filetypes=[('PNG files', '*.png'),('JPEG files', '*.jpg'),('All files', '*.*')])
        if not file_path:
            return
        try:
            img_pil = Image.fromarray(cv2.cvtColor(self.resized, cv2.COLOR_BGR2RGB))
            img_pil.save(file_path)
            messagebox.showinfo('Save Successful', f'Image saved to:\n{file_path}')
        except Exception as e:
            messagebox.showerror('Save Error', f'Failed to save image: {e}')


    def set_image_frame(self, frame):
        self.image_frame = frame


    def display_image(self):
        height, width, channel = self.image.shape
        scale_x = width / self.max_canvas_x
        scale_y = height / self.max_canvas_y
        self.canvas_scale = max(scale_x, scale_y, 1)

        self.canvas_x = int(width / self.canvas_scale)
        self.canvas_y = int(height / self.canvas_scale)

        self.image_frame.original_image_panel.config(width=self.canvas_x, height=self.canvas_y)
            
        img = cv2.resize(self.image_rgb, (self.canvas_x, self.canvas_y))
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

            x1, x2 = sorted([int(x1 * self.canvas_scale), int(x2 * self.canvas_scale)])
            y1, y2 = sorted([int(y1 * self.canvas_scale), int(y2 * self.canvas_scale)])

            self.set_undo_point()
            
            self.image_frame.original_image_panel.delete(self.rect)
            self.edited_image = self.image[y1:y2, x1:x2]
            self.update_preview()


    def update_preview(self, _=None):
        if self.edited_image is not None and self.image_frame:

            try:
                scale_percent = float(self.preview_resize_var.get())
                width = int(self.edited_image.shape[1] * scale_percent / 100)
                height = int(self.edited_image.shape[0] * scale_percent / 100)
                self.resized = cv2.resize(self.edited_image, (width, height), interpolation=cv2.INTER_AREA)
                self.resized = self.adjust_image(self.resized)

                img_pil = Image.fromarray(cv2.cvtColor(self.resized, cv2.COLOR_BGR2RGB))
                img_tk = ImageTk.PhotoImage(img_pil)

                self.image_frame.edited_image_panel.config(image=img_tk)
                self.image_frame.edited_image_panel.image = img_tk
        
            except Exception as e:
                print('Error resizing preview:', e)


    def adjust_image(self, img):
        if img is None:
            return None

        brightness = self.control_panel.brightness_scale.get() - self.brightness_conversion
        contrast = self.control_panel.contrast_scale.get() / self.contrast_conversion

        adjusted_img = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)

        if self.colourmode == 'G':
            adjusted_img = cv2.cvtColor(adjusted_img, cv2.COLOR_BGR2GRAY)

        return adjusted_img


    def set_colour_mode(self, _=None):
        self.colourmode = 'C'
        self.update_preview()


    def set_greyscale_mode(self, _=None):
        self.colourmode = 'G'
        self.update_preview()


    def set_undo_point(self, _=None):
        if not self.edited_image is None:
            self.undo_list.append((
                self.edited_image.copy(),
                self.preview_resize_var.get(),
                self.brightness.get(),
                self.contrast.get(),
                self.colourmode
            ))
            self.redo_list.clear()


    def undo_change(self, _=None):
        if len(self.undo_list) == 0:
            messagebox.showwarning('Nothing to undo', 'There is nothing to undo')
        else:
            self.redo_list.append((self.edited_image.copy(),
                self.preview_resize_var.get(),
                self.brightness.get(),
                self.contrast.get(),
                self.colourmode
            ))
            
            img, resize_var, brightness, contrast, colourmode = self.undo_list.pop()

            self.edited_image = img
            self.preview_resize_var.set(resize_var)
            self.brightness.set(brightness)
            self.contrast.set(contrast)
            self.colourmode = colourmode

            self.update_preview()
            

    def redo_change(self, _=None):
        if len(self.redo_list) == 0:
            messagebox.showwarning('Nothing to redo', 'There is nothing to redo')
        else:
            self.undo_list.append((self.edited_image.copy(),
                self.preview_resize_var.get(),
                self.brightness.get(),
                self.contrast.get(),
                self.colourmode
            ))

            img, resize_var, brightness, contrast, colourmode = self.redo_list.pop()

            self.edited_image = img
            self.preview_resize_var.set(resize_var)
            self.brightness.set(brightness)
            self.contrast.set(contrast)
            self.colourmode = colourmode

            self.update_preview()


    def reset_image(self, _=None):

        self.preview_resize_var.set(self.default_resize_var)
        self.brightness.set(self.default_brightness)
        self.contrast.set(self.default_contrast)
        self.colourmode = None

        self.edited_image = self.image

        self.undo_list.clear()
        self.redo_list.clear()

        self.display_image()


class title_frame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        title_font = font.Font(family='Arial', size=25)
        self.title_label = Label(text='TKinter/OpenCV Image Editor', font=title_font)
        self.title_label.pack(pady=20)


class control_frame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        #Widgets
        self.open_button = Button(self, text='Open File', command=parent.open_file)
        self.save_button = Button(self, text='Save File', command=parent.save_file)
        self.crop_label = Label(self, text='Crop Mode')
        self.crop_toggle = Checkbutton(self, variable=parent.crop_mode)
        self.resize_label = Label(self, text='Resize image', padx=10)
        self.resize_scale = Scale(self, variable=parent.preview_resize_var, from_ = parent.scale_min, to = parent.scale_max, orient=HORIZONTAL,command=parent.update_preview)
        self.brightness_label = Label(self, text='Brightness', padx=10)
        self.brightness_scale = Scale(self, variable=parent.brightness, from_ = parent.scale_min, to = parent.scale_max, orient=HORIZONTAL,command=parent.update_preview)
        self.contrast_label = Label(self, text='Contrast', padx=10)
        self.contrast_scale = Scale(self, variable=parent.contrast, from_ = parent.scale_min, to = parent.scale_max, orient=HORIZONTAL,command=parent.update_preview)
        self.colour_label = Label(self, text='Colouring', padx=10)
        self.colour_button = Button(self, text='Colour', command=parent.set_colour_mode)
        self.greyscale_button = Button(self, text='Greyscale', command=parent.set_greyscale_mode)
        self.undo_button = Button(self, text='Undo', command=parent.undo_change)
        self.redo_button = Button(self, text='Redo', command=parent.redo_change)
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
        self.undo_button.grid(row=10, column=0, padx=10, pady=(20,10))
        self.redo_button.grid(row=10, column=1, padx=10, pady=(20,10))
        self.reset_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10)


class preview_frame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        #Widgets
        self.original_label = Label(self, text='Original Image')
        self.original_image_panel = Canvas(self, width=parent.max_canvas_x, height=parent.max_canvas_y)
        self.edited_label = Label(self, text='Edited Image')
        self.edited_image_panel = Label(self, image=None)

        #Layout
        self.original_label.grid(row=0, column=0)
        self.edited_label.grid(row=0, column=1)
        self.original_image_panel.grid(row=1, column=0)        
        self.edited_image_panel.grid(row=1, column=1)


if __name__=='__main__':
    app = PhotoApp()
    app.mainloop()
