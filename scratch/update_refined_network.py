import os

lib_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
filepath = os.path.join(lib_dir, "visualize_ui.py")

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Define the new graph constructor code
new_graph_init = """        # topological street graph definition (31 intersections)
        self.nodes = {
            0: (270, 60),    # Shula Gate
            1: (235, 140),   # Neve Efal junction
            2: (200, 220),   # Agmon St / Main Spine
            3: (180, 310),   # Yasmin St / Main Spine
            4: (155, 415),   # Argaman St / Main Spine
            5: (145, 460),   # Main Spine South exit roundabout
            6: (220, 500),   # Main Spine South exit end

            7: (150, 150),   # Upper left branch end
            8: (100, 220),   # Agmon St West end
            9: (90, 310),    # Yasmin St West end
            10: (70, 415),   # Argaman St West end
            11: (100, 270),  # West vertical connector top
            12: (90, 360),   # West vertical connector bottom

            13: (330, 90),   # Upper East Gate
            14: (355, 140),  # Upper East corner curve
            15: (325, 190),  # Upper East branch inner end
            
            16: (260, 180),  # Seminary Center east loop top
            17: (260, 280),  # Seminary Center east loop bottom
            
            18: (240, 220),  # Agmon St East / Harduf corner
            19: (235, 310),  # Yasmin St East / Harduf corner
            20: (300, 305),  # Yasmin St Far East end
            
            21: (250, 150),  # Harduf St North end
            
            22: (325, 170),  # Far East vertical street top
            23: (295, 270),  # Far East vertical street bottom

            24: (90, 390),   # Argaman St parallel left
            25: (160, 400),  # Argaman St parallel mid
            
            26: (50, 470),   # U-shape bottom-left
            27: (110, 470),  # U-shape bottom-right
            
            28: (130, 490),  # South Grid Center
            29: (175, 490),  # South Grid East
            30: (230, 480)   # South Grid Gate
        }

        self.node_names = {
            0: "Shula BaHatzer Entrance",
            1: "Neve Ef'al Junction",
            2: "Agmon St / Main Spine",
            3: "Yasmin St / Main Spine",
            4: "Argaman St / Main Spine",
            5: "South Exit Roundabout",
            6: "South Gate Exit",
            7: "Neve Ef'al Upper West",
            8: "West Agmon St",
            9: "West Yasmin St",
            10: "West Argaman St",
            11: "West Connector North",
            12: "West Connector South",
            13: "East Gate (Shopping Area)",
            14: "East Curve Corner",
            15: "East Loop Inner End",
            16: "Seminary Center North",
            17: "Seminary Center South",
            18: "Agmon St / Harduf St",
            19: "Yasmin St / Harduf St",
            20: "Yasmin St East Gate",
            21: "Harduf St North End",
            22: "Far East Street North",
            23: "Far East Street South",
            24: "Argaman Parallel West",
            25: "Argaman Parallel Mid",
            26: "U-Shape West Corner",
            27: "U-Shape East Corner",
            28: "South Grid Center",
            29: "South Grid East",
            30: "South Grid Gate"
        }

        self.graph = {i: [] for i in range(len(self.nodes))}
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6),
            (1, 7), (2, 8), (3, 9), (4, 10),
            (8, 11), (11, 12), (12, 9),
            (0, 13), (13, 14), (14, 15),
            (2, 16), (16, 17), (17, 3),
            (2, 18), (18, 19), (19, 4), (19, 20),
            (18, 21),
            (22, 23),
            (24, 25),
            (10, 26), (26, 27), (27, 4),
            (4, 28), (28, 29), (29, 5), (5, 30), (30, 19)
        ]
        for u, v in edges:
            p1 = self.nodes[u]
            p2 = self.nodes[v]
            w = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
            self.graph[u].append((v, w))
            self.graph[v].append((u, w))"""

# Let's replace the constructor nodes definition
start_token = "# topological street graph definition (25 intersections)"
end_token = "self._build_ui()"
start_idx = content.find(start_token)
end_idx = content.find(end_token)

if start_idx == -1 or end_idx == -1:
    print(f"Error finding constructor tokens! start: {start_idx}, end: {end_idx}")
    exit(1)

content = content[:start_idx] + new_graph_init + "\n\n        " + content[end_idx:]

# Update the preset buttons inside _build_ui
old_presets = """        tk.Button(btn_frame, text="🏡 Seminary Center", command=lambda: self._add_preset(8),
                  font=("Helvetica", 10), width=18).grid(row=0, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="🍽️ Shula BaHatzer", command=lambda: self._add_preset(5),
                  font=("Helvetica", 10), width=18).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(btn_frame, text="👵 Neve Ef'al Care", command=lambda: self._add_preset(6),
                  font=("Helvetica", 10), width=18).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="🏥 Sheba East Gate", command=lambda: self._add_preset(15),
                  font=("Helvetica", 10), width=18).grid(row=1, column=1, padx=2, pady=2)"""

new_presets = """        tk.Button(btn_frame, text="🏡 Seminary Center", command=lambda: self._add_preset(16),
                  font=("Helvetica", 10), width=18).grid(row=0, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="🍽️ Shula BaHatzer", command=lambda: self._add_preset(0),
                  font=("Helvetica", 10), width=18).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(btn_frame, text="👵 Neve Ef'al Care", command=lambda: self._add_preset(1),
                  font=("Helvetica", 10), width=18).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="🏥 Sheba East Gate", command=lambda: self._add_preset(13),
                  font=("Helvetica", 10), width=18).grid(row=1, column=1, padx=2, pady=2)"""

content = content.replace(old_presets, new_presets)

# Update get_shortest_path hardcoded range(25) -> range(len(self.nodes))
old_shortest_path = """        dist = {i: float('inf') for i in range(25)}
        prev = {i: None for i in range(25)}
        dist[start] = 0.0
        Q = list(range(25))"""

new_shortest_path = """        dist = {i: float('inf') for i in range(len(self.nodes))}
        prev = {i: None for i in range(len(self.nodes))}
        dist[start] = 0.0
        Q = list(range(len(self.nodes)))"""

content = content.replace(old_shortest_path, new_shortest_path)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Programmatic network update completed successfully!")
