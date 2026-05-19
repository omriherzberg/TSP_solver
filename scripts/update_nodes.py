import tkinter as tk

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

nodes = {
    0: (75, 50), 1: (50, 160), 2: (60, 300), 3: (60, 600), 4: (65, 700),
    5: (420, 200), 6: (170, 310), 7: (310, 350), 8: (480, 480), 9: (310, 450),
    10: (310, 550), 11: (150, 580), 12: (220, 350), 13: (450, 350), 14: (560, 350),
    15: (670, 350), 16: (220, 450), 17: (450, 450), 18: (450, 550), 19: (670, 450),
    20: (450, 350), 21: (450, 650), 22: (450, 750), 23: (220, 650), 24: (310, 650)
}

# Run k-means (10 iterations)
K = 25
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

# Print new nodes formatted for python dict
print("        self.nodes = {")
for i in range(K):
    print(f"            {i}: ({int(centroids[i][0])}, {int(centroids[i][1])}),")
print("        }")

