import tkinter as tk
import ast
import re

with open("visualize_ui.py", "r") as f:
    content = f.read()

# Extract self.nodes
match = re.search(r"self\.nodes = (\{[^}]+\})", content)
if not match:
    print("Could not find self.nodes")
    exit(1)

nodes_str = match.group(1)
# Clean up comments to parse
nodes_str = re.sub(r'#.*', '', nodes_str)
nodes = ast.literal_eval(nodes_str)

root = tk.Tk()
img = tk.PhotoImage(file="ramat_efal_map.png").subsample(2, 2)
width = img.width()
height = img.height()

dark_pixels = []
for y in range(0, height, 2):
    for x in range(0, width, 2):
        rgb = img.get(x, y)
        if type(rgb) == str:
            r = int(rgb[1:3], 16)
            g = int(rgb[3:5], 16)
            b = int(rgb[5:7], 16)
        else:
            r, g, b = rgb
        if r < 40 and g < 40 and b < 40:
            dark_pixels.append((x, y))

K = len(nodes)
centroids = [list(nodes[i]) for i in range(K)]

for _ in range(15):
    clusters = [[] for _ in range(K)]
    for p in dark_pixels:
        best_i = 0
        min_d = float('inf')
        for i, c in enumerate(centroids):
            d = (p[0]-c[0])**2 + (p[1]-c[1])**2
            if d < min_d:
                min_d = d
                best_i = i
        clusters[best_i].append(p)
        
    for i in range(K):
        if clusters[i]:
            cx = sum(p[0] for p in clusters[i]) / len(clusters[i])
            cy = sum(p[1] for p in clusters[i]) / len(clusters[i])
            centroids[i] = [cx, cy]

print("        self.nodes = {")
for i in range(K):
    # Keep the original comments!
    # Let's just print the raw coordinates so we can manually replace them
    print(f"            {i}: ({int(centroids[i][0])}, {int(centroids[i][1])}),")
print("        }")

