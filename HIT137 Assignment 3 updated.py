import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("HIT137 Assignment 3 Image Editor")
        root.geometry("500x600")

        # Variables
        self.original_image = None
        self.display_image = None
        self.modified_image = None
        self.selection = None
        self.usage_count = 0  # Used for gradually disabling features

        # GUI Layout
        self.canvas = tk.Canvas(root, width=500, height=400, bg="beige")
        self.canvas.pack()
        
        self.load_button = tk.Button(root, text="Select Image", command=self.load_image, fg = "magenta")
        self.load_button.pack()
        
        self.crop_button = tk.Button(root, text="Crop Image or remove selected area", command=self.start_cropping, fg = "red")
        self.crop_button.pack(anchor = "s", padx = 10, pady = 10)
        
        self.resize_slider = tk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, label="Resize/Distort", command=self.apply_resize, fg = "blue")
        self.resize_slider.pack(anchor = "sw")

        ###
        # original_image = Image.open("load_button")
        # original_size = original_image.size[0]

        # tk_image = ImageTk.PhotoImage(original_image)
        # image_label = tk.Label(root, image=tk_image)
        # image_label.pack()
        
        # slider = ttk.Scale(root, from_=50, to= original_size * 2, orient='horizontal', command=lambda value: update_image(int(float(value))))
        # slider.set(original_size)
        # slider.pack()
        # ###
        
        self.save_button = tk.Button(root, text="Save Image", command=self.save_image, fg = "green")
        self.save_button.pack(anchor = "se", side = "right", padx = 10, pady = 10)
        
        ##
        # text_area = tk.Text(root, undo=True)
        # text_area.pack(expand=True, fill='both')

        def undo_action():
            try:
                edit_undo()
            except tk.TclError:
                pass

        undo_button = tk.Button(root, text="Undo", command=undo_action, fg = "orange")
        undo_button.pack(side='bottom', anchor = "se", padx = 10, pady = 10)
        #


        # Canvas Mouse Events for Cropping
        self.canvas.bind("<ButtonPress-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.finalize_selection)
        
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        
        self.original_image = cv2.imread(file_path)
        self.display_image = self.original_image.copy()
        self.show_image()
    
    def show_image(self):
        if self.display_image is not None:
            # Convert image to display format
            img = cv2.cvtColor(self.display_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img.thumbnail((400, 400))  # Display only as a thumbnail
            self.img_tk = ImageTk.PhotoImage(img)
            
            self.canvas.create_image(250, 200, image=self.img_tk)
    
    def start_cropping(self):
        if self.display_image is None:
            return
        self.selection = None  # Reset selection
        
    def start_selection(self, event):
        self.selection = [event.x, event.y, event.x, event.y]
    
    def update_selection(self, event):
        if self.selection:
            self.selection[2], self.selection[3] = event.x, event.y
            self.show_selection()
    
    def show_selection(self):
        # Display inverse of selection (highlight outside the box)
        overlay = self.display_image.copy()
        x1, y1, x2, y2 = self.selection
        
        mask = np.ones(overlay.shape, dtype=np.uint8) * 255
        cv2.rectangle(mask, (x1, y1), (x2, y2), (0, 0, 0), -1)
        self.display_image = cv2.bitwise_and(self.original_image, mask)
        self.show_image()
    
    def finalize_selection(self, event):
        if self.selection:
            x1, y1, x2, y2 = self.selection
            cv2.rectangle(self.display_image, (x1, y1), (x2, y2), (255, 255, 255), -1)  # Remove selected area
            self.show_image()
    
    def apply_resize(self, value):
        if self.display_image is None:
            return
        
        # Distort quality rather than resizing
        quality = int(value)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), max(1, 100 - quality)]
        _, encoded_img = cv2.imencode('.jpg', self.original_image, encode_param)
        self.display_image = cv2.imdecode(encoded_img, 1)
        self.show_image()
    
    def save_image(self):
        if self.display_image is None:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path:
            cv2.imwrite(file_path, self.display_image)
    
    def remove_features_progressively(self):
        self.usage_count += 1
        if self.usage_count == 3:
            self.crop_button.config(state=tk.DISABLED)
        elif self.usage_count == 5:
            self.resize_slider.config(state=tk.DISABLED)
    
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()