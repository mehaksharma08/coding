import cv2
import numpy as np
import tkinter as tk
from PIL import Image
from tkinter import filedialog

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("image creater")

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack()

        self.load_button = tk.Button(self.root, text="download image ", command=self.load_image)
        self.load_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.root, text="save ", command=self.save_image)
        self.save_button.pack(side=tk.RIGHT)

        self.undo_button = tk.Button(self.root, text="Undo", command=self.undo)
        self.undo_button.pack(side=tk.RIGHT)

        self.slider = tk.Scale(self.root, from_=10, to_=100, orient="horizontal", label="Resize", command=self.resize_image)
        self.slider.pack(side=tk.LEFT)

        self.img = None
        self.original_img = None
        self.cropped_img = None
        self.undo_stack = []
        self.selected_area = None
        self.rect_id = None
        self.start_x = self.start_y = None

        self.root.bind("<Control-s>", lambda e: "break")
        self.root.bind("<Control-z>", lambda e: "break")

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.img = cv2.imread(file_path)
            self.original_img = self.img.copy()

            img_rgb = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = Image.TK.PhotoImage(img_pil)

            self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
            self.canvas.img_tk = img_tk
            self.canvas.config(width=img_tk.width(), height=img_tk.height())

    def on_click(self, event):
        self.start_x, self.start_y = event.x, event.y

    def on_drag(self, event):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", width=2)

    def crop_image(self):
        if self.selected_area:
            x1, y1, x2, y2 = self.selected_area
            self.cropped_img = self.img.copy()
            self.cropped_img[y1:y2, x1:x2] = 255  

            self.show_image_on_canvas(self.cropped_img)

    def resize_image(self, val):
        if self.cropped_img is not None:
            new_width = int(self.cropped_img.shape[1] * int(val) / 100)
            new_height = int(self.cropped_img.shape[0] * int(val) / 100)
            resized_img = cv2.resize(self.cropped_img, (new_width, new_height))

            img_rgb = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)

            self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
            self.canvas.img_tk = img_tk

    def save_image(self):
        if self.cropped_img is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
            if file_path:
                cv2.imwrite(file_path, self.cropped_img)
                messagebox.showinfo("Save", "Image saved successfully!")

    def undo(self):
        if self.undo_stack:
            self.img = self.undo_stack.pop()
            self.show_image_on_canvas(self.img)
        else:
            messagebox.showwarning("Undo", "No actions to undo.")

    def show_image_on_canvas(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)

        self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
        self.canvas.img_tk = img_tk
        self.canvas.config(width=img_tk.width(), height=img_tk.height())

    def save_for_undo(self):
        if self.img is not None:
            self.undo_stack.append(self.img.copy())

    def on_mouse_click(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.selected_area = (self.start_x, self.start_y, self.start_x, self.start_y)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_release(self, event):
        end_x, end_y = event.x, event.y
        self.selected_area = (self.start_x, self.start_y, end_x, end_y)
        self.crop_image()

    def enable_rectangle_drawing(self):
        self.canvas.bind("<Button-1>", self.on_mouse_click)


if __name__ == "__main__":
    root = tk.Tk()
    editor = ImageEditor(root)
    editor.enable_rectangle_drawing()
    root.mainloop()



