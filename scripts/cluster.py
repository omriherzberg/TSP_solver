import tkinter as tk
import math
import json

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

# Simple K-Means
K = 25
import random
random.seed(42)
centroids = random.sample(dark_pixels, K)

for _ in range(20):
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
            centroids[i] = (cx, cy)

nodes = {i: (int(c[0]), int(c[1])) for i, c in enumerate(centroids)}

# Connect nearest neighbors (e.g. Gabriel Graph or simple threshold)
edges = set()
for i in range(K):
    # Connect to 2 nearest neighbors
    dists = []
    for j in range(K):
        if i != j:
            d = (centroids[i][0]-centroids[j][0])**2 + (centroids[i][1]-centroids[j][1])**2
            dists.append((d, j))
    dists.sort()
    edges.add(tuple(sorted((i, dists[0][1]))))
    edges.add(tuple(sorted((i, dists[1][1]))))

print(json.dumps({"nodes": nodes, "edges": list(edges)}))

