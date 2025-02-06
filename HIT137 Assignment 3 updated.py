import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from tkinter import messagebox


def debug():
    print("here")

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("HIT137 Assignment 3 Image Editor")
        self.root.geometry("600x700")

        # Variables
        self.original_image = None
        self.display_image = None
        self.selection = None

        # GUI Layout
        self.canvas = tk.Canvas(root, width=500, height=400, bg="beige", cursor="cross")
        self.canvas.pack()

        self.load_button = tk.Button(root, text="Select Image", command=self.load_image, fg="magenta")
        self.load_button.pack()

        self.crop_button = tk.Button(root, text="Crop Image", command=self.start_cropping, fg="red")
        self.crop_button.pack(padx=10, pady=10, anchor = "se")

        # Resize slider
        self.resize_slider = tk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, label="Resize/Distort",
                                      command=self.apply_resize, fg="blue")
        self.resize_slider.pack(anchor="sw", padx = 10, pady =10)

        self.save_button = tk.Button(root, text="Save Image", command=self.save_image, fg="green")
        self.save_button.pack(padx=10, pady=10, anchor = "se")
        
        #### undo/redo buttons
        text_widget = tk.Button
        edit_undo = tk.Button
        undo_text = tk.Button
        def undo_action():
            try:
                edit_undo()
            except tk.TclError:
                pass 

        undo_button = tk.Button(root, text="Undo", command=undo_action, fg = "orange")
        undo_button.pack(side='bottom', anchor = "se", padx = 10, pady = 10)
        
        # Redo Key
        def redo_text():
            try:
                text_widget.edit_redo()
            except tk.TclError:
                pass

        
        redo_button = tk.Button(root, text="Redo", command=redo_text , fg = "red")
        redo_button.pack(side="bottom", anchor = "se", padx=10, pady=10)

        root.bind("<Control-z>", lambda event: undo_text())  # Ctrl+Z for undo
        root.bind("<Control-y>", lambda event: redo_text())  # Ctrl+Y for redo
        
        ##### keyboard shortcuts
        root = tk.Tk()
        
        def welcome(event=None):  # For Key Bindings
            messagebox.showinfo("Shortcut", "Welcome! You pressed Ctrl+H")

        def quit_app(event=None):
            root.quit()

        button = tk.Button(root, text="Welcome to the HIT137 Image Editor!", command=welcome)
        button.pack(pady=20)

        root.bind("<Control-h>", welcome)   # Ctrl+H to say Hello
        root.bind("<Control-q>", debug)

    
        # Canvas Mouse Events for Cropping
        self.canvas.bind("<ButtonPress-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.finalize_selection)

        self.rect_id = None
        self.start_x = self.start_y = 0
        self.end_x = self.end_y = 0

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
        if not file_path:
            return
        
        self.original_image = cv2.imread(file_path)
        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.display_image = self.original_image.copy()
        self.show_image()

    def show_image(self):
        """Display the current image on the canvas."""
        if self.display_image is None:
            return
        
        img = Image.fromarray(self.display_image)
        img.thumbnail((500, 400))  # Resize for display
        self.img_tk = ImageTk.PhotoImage(img)
        
        self.canvas.create_image(250, 200, image=self.img_tk)

    def start_cropping(self):
        if self.display_image is None:
            return
        self.selection = None  # Reset selection

    def start_selection(self, event):
        """Start drawing the selection rectangle."""
        self.start_x, self.start_y = event.x, event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", width=2)

    def update_selection(self, event):
        """Update the rectangle as the user drags the mouse."""
        self.end_x, self.end_y = event.x, event.y
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, self.end_x, self.end_y)

    def finalize_selection(self, event):
        """Crop and display the selected area."""
        self.end_x, self.end_y = event.x, event.y

        if self.original_image is None:
            return
        
        # Converting canvas coordinates to image coordinates
        x1, y1, x2, y2 = min(self.start_x, self.end_x), min(self.start_y, self.end_y), \
                         max(self.start_x, self.end_x), max(self.start_y, self.end_y)

        # Getting image dimensions
        img_h, img_w, _ = self.original_image.shape

        # Converting canvas coordinates to image coordinates
        scale_x = img_w / 500  # Canvas width is 500
        scale_y = img_h / 400  # Canvas height is 400

        x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
        y1, y2 = int(y1 * scale_y), int(y2 * scale_y)

        # Ensuring it is a  valid crop
        if x1 < 0 or y1 < 0 or x2 > img_w or y2 > img_h or x1 == x2 or y1 == y2:
            messagebox.showerror("Error", "Invalid selection area. Try again.")
            return
        
        cropped_img = self.original_image[y1:y2, x1:x2]

        if cropped_img.size == 0:
            messagebox.showerror("Error", "Selection area is too small.")
            return

        # Showing cropped image in a totally new window
        self.show_cropped_image(cropped_img)

    def show_cropped_image(self, cropped_img):
        """Display the cropped image in a new Tkinter window."""
        new_window = tk.Toplevel(self.root)
        new_window.title("Cropped Image")

        img = Image.fromarray(cropped_img)
        img.thumbnail((250, 250))  # Resizing for display
        tk_img = ImageTk.PhotoImage(img)

        label = tk.Label(new_window, image=tk_img)
        label.image = tk_img  # Keeping reference
        label.pack()

    def apply_resize(self, value):
        """Dynamically adjust image quality using JPEG compression."""
        if self.display_image is None:
            return
        
        quality = int(value)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), max(1, 100 - quality)]
        _, encoded_img = cv2.imencode('.jpg', self.original_image, encode_param)
        self.display_image = cv2.imdecode(encoded_img, 1)
        self.show_image()

    def save_image(self):
        """Save the displayed image to a file."""
        if self.display_image is None:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path:
            cv2.imwrite(file_path, cv2.cvtColor(self.display_image, cv2.COLOR_RGB2BGR))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()
