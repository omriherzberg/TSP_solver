import tkinter as tk

root = tk.Tk()
img = tk.PhotoImage(file="ramat_efal_map.png").subsample(2, 2)
width = img.width()
height = img.height()

scale = 6
w_out = width // scale
h_out = height // scale

grid = [[' ' for _ in range(w_out)] for _ in range(h_out)]

for y in range(0, height, scale):
    for x in range(0, width, scale):
        rgb = img.get(x, y)
        if type(rgb) == str:
            r = int(rgb[1:3], 16)
            g = int(rgb[3:5], 16)
            b = int(rgb[5:7], 16)
        else:
            r, g, b = rgb
            
        if r < 40 and g < 40 and b < 40:
            grid[y//scale][x//scale] = '#'

for row in grid:
    print("".join(row))

