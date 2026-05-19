import tkinter as tk
import os

root = tk.Tk()
img = tk.PhotoImage(file="ramat_efal_map.png").subsample(2, 2)
width = img.width()
height = img.height()

print(f"Image is {width}x{height}")

# Find black or very dark pixels
dark_pixels = []
for y in range(0, height, 5): # sample every 5 pixels
    for x in range(0, width, 5):
        rgb = img.get(x, y)
        if type(rgb) == str:
            # hex string
            r = int(rgb[1:3], 16)
            g = int(rgb[3:5], 16)
            b = int(rgb[5:7], 16)
        else:
            r, g, b = rgb
        if r < 30 and g < 30 and b < 30:
            dark_pixels.append((x, y))

print(f"Found {len(dark_pixels)} dark pixels (sampled).")
if len(dark_pixels) > 0:
    for i in range(0, len(dark_pixels), max(1, len(dark_pixels)//20)):
        print(dark_pixels[i])

