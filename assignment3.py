import cv2
import numpy as np
import tkinter as tk

class ImageProcessor:
    def __init__(self):
        self.original_image = None
        self.processed_image = None

from tkinter import filedialog

def load_image(self):
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if file_path:  # Ensure a file was selected
        self.original_image = cv2.imread(file_path)
        self.processed_image = self.original_image.copy()
        return self.processed_image
