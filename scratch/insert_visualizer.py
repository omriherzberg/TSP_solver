import os

lib_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
filepath = os.path.join(lib_dir, "visualize_ui.py")

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Locate MainApp definition
main_app_token = "class MainApp(tk.Tk):"
main_app_idx = content.find(main_app_token)

if main_app_idx == -1:
    print("Error: MainApp token not found!")
    exit(1)

# The new IsraelRoadTSPVisualizer class
israel_class = """class IsraelRoadTSPVisualizer(tk.Frame):
    MAP_W = 373
    MAP_H = 512

    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self.pinned_nodes = []
        self.current_tour = None
        self._anim_id = None
        self.path_lines = []
        self.stage_lines = []
        self.is_running = False
        
        # Load the background map image with 2x subsampling
        try:
            self.bg_photo = tk.PhotoImage(file=os.path.join(lib_dir, "ramat_efal_map.png")).subsample(2, 2)
        except Exception as e:
            print(f"Error loading map background: {e}")
            self.bg_photo = None

        # topological street graph definition (25 intersections)
        self.nodes = {
            0: (35, 100),   # Route 4 - 1
            1: (45, 250),   # Route 4 - 2 (Aluf Sade)
            2: (25, 450),   # Route 4 - 3
            3: (15, 650),   # Route 4 - 4
            4: (10, 850),   # Route 4 - 5
            
            5: (190, 100),  # Main Spine - 1 (near Shula)
            6: (190, 200),  # Main Spine - 2 (near Neve Ef'al)
            7: (180, 300),  # Main Spine - 3 (Agmon St)
            8: (170, 420),  # Main Spine - 4 (Seminary Center)
            9: (160, 550),  # Main Spine - 5 (Yasmin St)
            10: (150, 700), # Main Spine - 6 (Argaman St)
            11: (140, 850), # Main Spine - 7 (Roundabout)
            
            12: (90, 260),  # Agmon St - 1
            13: (140, 280), # Agmon St - 2
            14: (230, 320), # Agmon St - 4
            15: (270, 340), # Agmon St - 5 (Sheba Area)
            
            16: (80, 450),  # Yasmin St - 1
            17: (210, 500), # Yasmin St - 3
            18: (250, 470), # Yasmin St - 4 (Harduf corner)
            19: (300, 450), # Yasmin St - 5
            
            20: (260, 250), # Harduf St - 1
            21: (230, 680), # Harduf St - 3 (Argaman corner)
            22: (220, 850), # Harduf St - 4
            
            23: (70, 660),  # Argaman St - 1
            24: (310, 650)  # Argaman St - 4
        }

        self.node_names = {
            0: "Route 4 North",
            1: "Aluf Sade/Bar Ilan Interchange",
            2: "Route 4 Mid",
            3: "Route 4 South Exit",
            4: "Route 4 South",
            5: "Shula BaHatzer Restaurant",
            6: "Neve Ef'al Elderly Care",
            7: "Agmon St / Main Spine",
            8: "Ef'al Seminary Center",
            9: "HaYasmin St / Main Spine",
            10: "Argaman St / Main Spine",
            11: "South Exit Roundabout",
            12: "West Agmon St",
            13: "Agmon St Mid-West",
            14: "Agmon St Mid-East",
            15: "East Agmon St (near Sheba)",
            16: "West HaYasmin St",
            17: "HaYasmin St Mid",
            18: "Harduf St / HaYasmin St",
            19: "East HaYasmin St (near Sheba)",
            20: "Harduf St North",
            21: "Harduf St / Argaman St",
            22: "Harduf St South",
            23: "West Argaman St",
            24: "East Argaman St (near Sheba)"
        }

        self.graph = {i: [] for i in range(25)}
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11),
            (12, 13), (13, 7), (7, 14), (14, 15),
            (16, 9), (9, 17), (17, 18), (18, 19),
            (20, 18), (18, 21), (21, 22),
            (23, 10), (10, 21), (21, 24),
            (1, 12), (2, 16), (3, 23), (5, 0)
        ]
        for u, v in edges:
            p1 = self.nodes[u]
            p2 = self.nodes[v]
            w = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
            self.graph[u].append((v, w))
            self.graph[v].append((u, w))

        self._build_ui()
        self._draw_base_map()

    def _build_ui(self):
        top = tk.Frame(self, bg="#1e1e2e")
        top.pack(fill=tk.X, padx=10, pady=(8, 0))
        tk.Label(top, text="📍 Ramat Efal Friend's Router",
                 font=("Helvetica", 18, "bold"), bg="#1e1e2e", fg="#ffd700").pack(side=tk.LEFT)
        self.info_lbl = tk.Label(top, text="Click on the map to place pins representing your friends' houses!",
                                 font=("Helvetica", 11), bg="#1e1e2e", fg="#a9b7c6")
        self.info_lbl.pack(side=tk.LEFT, padx=20)

        body = tk.Frame(self, bg="#1e1e2e")
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Canvas matching exactly the subsampled image dimensions
        self.canvas = tk.Canvas(body, width=self.MAP_W, height=self.MAP_H,
                                bg="#0b132b", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, anchor=tk.N)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        side = tk.Frame(body, bg="#1e1e2e", width=400)
        side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0))
        side.pack_propagate(False)

        # Preset destinations panel
        pf = tk.LabelFrame(side, text="Quick Presets & Actions", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        pf.pack(fill=tk.X, pady=(0, 8))
        
        btn_frame = tk.Frame(pf, bg="#1e1e2e")
        btn_frame.pack(fill=tk.X, pady=2)
        
        tk.Button(btn_frame, text="🏡 Seminary Center", command=lambda: self._add_preset(8),
                  font=("Helvetica", 10), width=18).grid(row=0, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="🍽️ Shula BaHatzer", command=lambda: self._add_preset(5),
                  font=("Helvetica", 10), width=18).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(btn_frame, text="👵 Neve Ef'al Care", command=lambda: self._add_preset(6),
                  font=("Helvetica", 10), width=18).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="🏥 Sheba East Gate", command=lambda: self._add_preset(15),
                  font=("Helvetica", 10), width=18).grid(row=1, column=1, padx=2, pady=2)
        
        tk.Button(pf, text="❌ Clear Pinned Locations", command=self._clear_pins,
                  font=("Helvetica", 10, "bold"), bg="#dc3545", fg="#ffffff", activebackground="#c82333").pack(fill=tk.X, pady=(4, 0))

        # Algorithm panel
        af = tk.LabelFrame(side, text="TSP Algorithms", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        af.pack(fill=tk.X, pady=(0, 8))

        def algo_col(lf, btn_text, comp, cmd, fg_color):
            col = tk.Frame(lf, bg="#1e1e2e")
            col.pack(fill=tk.X, pady=2)
            tk.Button(col, text=btn_text, command=cmd,
                      font=("Helvetica", 11), width=32).pack()
            lbl = tk.Label(col, text="", font=("Courier", 10), bg="#1e1e2e", fg=fg_color)
            lbl.pack()
            return lbl

        self.lbl_nn    = algo_col(af, "1. Nearest Neighbor (Topological)", "O(N²)",     self._run_nn,     "#4CAF50")
        self.lbl_gr    = algo_col(af, "2. Greedy Edge-Insertion",        "O(N²logN)", self._run_greedy, "#E91E63")
        self.lbl_2opt  = algo_col(af, "Optimize: 2-Opt refinement",      "O(N²)",     self._run_2opt,   "#8A2BE2")

        # Stats
        rf = tk.LabelFrame(side, text="Route Travel Cost", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        rf.pack(fill=tk.X, pady=(0, 8))
        self.lbl_primary   = tk.Label(rf, text="—", font=("Courier", 14, "bold"), bg="#1e1e2e", fg="#ffc66d")
        self.lbl_primary.pack()
        self.lbl_secondary = tk.Label(rf, text="", font=("Courier", 11), bg="#1e1e2e", fg="#a9b7c6")
        self.lbl_secondary.pack()

        # Tour order list
        cf = tk.LabelFrame(side, text="Optimal Path Sequence", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        cf.pack(fill=tk.BOTH, expand=True)
        self.tour_text = tk.Text(cf, font=("Courier", 9), bg="#12171e", fg="#a9b7c6",
                                 height=8, width=32, state=tk.DISABLED, relief=tk.FLAT)
        self.tour_text.pack(fill=tk.BOTH, expand=True)

    def _on_canvas_click(self, event):
        if self.is_running: return
        x, y = event.x, event.y
        best_node = None
        best_dist = float('inf')
        for node_id, pos in self.nodes.items():
            d = ((pos[0]-x)**2 + (pos[1]-y)**2)**0.5
            if d < best_dist:
                best_dist = d
                best_node = node_id
        
        # Snap to nearest intersection if clicked within 60 pixels
        if best_dist < 60:
            if best_node in self.pinned_nodes:
                self.info_lbl.config(text="Location already pinned!")
                return
            self.pinned_nodes.append(best_node)
            self._draw_base_map()
            self.info_lbl.config(text=f"Pinned location: {self.node_names[best_node]}!")
        else:
            self.info_lbl.config(text="Please click closer to a visible street or junction!")

    def _add_preset(self, node_id):
        if self.is_running: return
        if node_id in self.pinned_nodes:
            self.info_lbl.config(text="Location already pinned!")
            return
        self.pinned_nodes.append(node_id)
        self._draw_base_map()
        self.info_lbl.config(text=f"Added Preset: {self.node_names[node_id]}!")

    def _clear_pins(self):
        if self.is_running: return
        self.pinned_nodes = []
        self.current_tour = None
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        self._clear_stage_lines()
        self._clear_path_lines()
        self._draw_base_map()
        self.lbl_nn.config(text="")
        self.lbl_gr.config(text="")
        self.lbl_2opt.config(text="")
        self.lbl_primary.config(text="—")
        self.lbl_secondary.config(text="")
        self.tour_text.config(state=tk.NORMAL)
        self.tour_text.delete("1.0", tk.END)
        self.tour_text.config(state=tk.DISABLED)
        self.info_lbl.config(text="All pins cleared. Click the map to add homes!")

    def get_shortest_path(self, start, end):
        if start == end:
            return [start], 0.0
        dist = {i: float('inf') for i in range(25)}
        prev = {i: None for i in range(25)}
        dist[start] = 0.0
        Q = list(range(25))
        while Q:
            u = min(Q, key=lambda n: dist[n])
            Q.remove(u)
            if u == end:
                break
            for v, weight in self.graph[u]:
                alt = dist[u] + weight
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
        
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = prev[curr]
        path.reverse()
        return path, dist[end]

    def _draw_base_map(self):
        self.canvas.delete("all")
        if self.bg_photo:
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor=tk.NW, tags="bg_map")
        else:
            self.canvas.create_rectangle(0, 0, self.MAP_W, self.MAP_H, fill="#0b132b")

        # Draw road network overlay slightly translucent
        for u in self.graph:
            for v, _ in self.graph[u]:
                if u < v:
                    p1 = self.nodes[u]
                    p2 = self.nodes[v]
                    self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#4e5d6c", width=1.5, dash=(2, 2))

        # Pinned houses
        for idx, node_id in enumerate(self.pinned_nodes):
            pos = self.nodes[node_id]
            self.canvas.create_oval(pos[0]-11, pos[1]-11, pos[0]+11, pos[1]+11,
                                    fill="", outline="#ff9f43", width=2, tags="pin_pulse")
            self.canvas.create_oval(pos[0]-7, pos[1]-7, pos[0]+7, pos[1]+7,
                                    fill="#ff9f43", outline="#ffffff", width=1.5, tags="pin")
            self.canvas.create_text(pos[0]+13, pos[1], text=f"{idx+1}. {self.node_names[node_id]}",
                                    font=("Helvetica", 8, "bold"), fill="#ffffff",
                                    anchor=tk.W, tags="pin_lbl")

    def _animate_tour(self, tour, color, step=0):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        if not tour or step >= len(tour):
            self.canvas.tag_raise("pin")
            self.canvas.tag_raise("pin_lbl")
            return
        
        u = tour[step]
        v = tour[(step + 1) % len(tour)]
        path, _ = self.get_shortest_path(u, v)
        
        coords = []
        for nid in path:
            pos = self.nodes[nid]
            coords.extend([pos[0], pos[1]])
            
        if len(coords) >= 4:
            line = self.canvas.create_line(*coords, fill=color, width=3.5, smooth=True, tags="tour_line")
            self.path_lines.append(line)
            
        self._anim_id = self.after(300, lambda: self._animate_tour(tour, color, step + 1))

    def _update_results(self, lbl, tour, cost):
        self.current_tour = tour
        # 1 pixel approx 3.2 meters based on neighborhood scale
        scaled_dist_meters = cost * 3.2
        primary = f"{scaled_dist_meters:.0f} meters"
        secondary = f"approx. {scaled_dist_meters/1000:.2f} km driving"
        
        lbl.config(text=primary)
        self.lbl_primary.config(text=primary)
        self.lbl_secondary.config(text=secondary)
        
        self.tour_text.config(state=tk.NORMAL)
        self.tour_text.delete("1.0", tk.END)
        for i, nid in enumerate(tour):
            self.tour_text.insert(tk.END, f"{i+1:2}. {self.node_names[nid]}\\n")
        self.tour_text.insert(tk.END, f" ↩ {self.node_names[tour[0]]}")
        self.tour_text.config(state=tk.DISABLED)

    def _interruptible_pause(self, ms):
        elapsed = 0
        chunk = 50
        while elapsed < ms:
            self.update()
            wait = min(chunk, ms - elapsed)
            var = tk.IntVar()
            self.after(wait, var.set, 1)
            self.wait_variable(var)
            elapsed += wait

    def _clear_stage_lines(self):
        for line in self.stage_lines:
            self.canvas.delete(line)
        self.stage_lines = []

    def _clear_path_lines(self):
        for line in self.path_lines:
            self.canvas.delete(line)
        self.path_lines = []

    def _run_nn(self):
        if len(self.pinned_nodes) < 2:
            self.info_lbl.config(text="Add at least 2 locations first!")
            return
        if self.is_running: return
        self.is_running = True
        
        self._clear_stage_lines()
        self._clear_path_lines()
        self._draw_base_map()
        
        unvisited = list(self.pinned_nodes[1:])
        tour = [self.pinned_nodes[0]]
        total_cost = 0.0
        
        while unvisited:
            curr = tour[-1]
            best_next = None
            best_dist = float('inf')
            for node in unvisited:
                _, d = self.get_shortest_path(curr, node)
                if d < best_dist:
                    best_dist = d
                    best_next = node
            
            # Show progressive street route segment
            path, _ = self.get_shortest_path(curr, best_next)
            coords = []
            for nid in path:
                pos = self.nodes[nid]
                coords.extend([pos[0], pos[1]])
            if len(coords) >= 4:
                line = self.canvas.create_line(*coords, fill="#4CAF50", width=3, smooth=True)
                self.stage_lines.append(line)
            
            tour.append(best_next)
            unvisited.remove(best_next)
            total_cost += best_dist
            self.info_lbl.config(text=f"[Nearest Neighbor] Connected {len(tour)} / {len(self.pinned_nodes)} houses...")
            self.update()
            self._interruptible_pause(300)
            
        _, final_d = self.get_shortest_path(tour[-1], tour[0])
        total_cost += final_d
        
        self._clear_stage_lines()
        self._animate_tour(tour, "#4CAF50")
        self._update_results(self.lbl_nn, tour, total_cost)
        self.info_lbl.config(text="Nearest Neighbor routing solved successfully!")
        self.is_running = False

    def _run_greedy(self):
        if len(self.pinned_nodes) < 2:
            self.info_lbl.config(text="Add at least 2 locations first!")
            return
        if self.is_running: return
        self.is_running = True
        
        self._clear_stage_lines()
        self._clear_path_lines()
        self._draw_base_map()
        
        edges = []
        N = len(self.pinned_nodes)
        for i in range(N):
            for j in range(i+1, N):
                u = self.pinned_nodes[i]
                v = self.pinned_nodes[j]
                _, d = self.get_shortest_path(u, v)
                edges.append((d, u, v))
        edges.sort()
        
        degree = {node: 0 for node in self.pinned_nodes}
        parent = {node: node for node in self.pinned_nodes}
        
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        
        selected = []
        total_cost = 0.0
        
        for cost, u, v in edges:
            if degree[u] >= 2 or degree[v] >= 2:
                continue
            if len(selected) < N - 1 and find(u) == find(v):
                continue
            
            degree[u] += 1
            degree[v] += 1
            parent[find(u)] = find(v)
            selected.append((u, v))
            total_cost += cost
            
            # Show edge highlighted along streets
            path, _ = self.get_shortest_path(u, v)
            coords = []
            for nid in path:
                pos = self.nodes[nid]
                coords.extend([pos[0], pos[1]])
            if len(coords) >= 4:
                line = self.canvas.create_line(*coords, fill="#E91E63", width=3, smooth=True)
                self.stage_lines.append(line)
            
            self.info_lbl.config(text=f"[Greedy Edges] Selected {len(selected)} / {N} path links...")
            self.update()
            self._interruptible_pause(350)
            
        # Complete tour loop reconstruction
        adj = {node: [] for node in self.pinned_nodes}
        for u, v in selected:
            adj[u].append(v)
            adj[v].append(u)
            
        tour = []
        visited = set()
        curr = self.pinned_nodes[0]
        for _ in range(N):
            tour.append(curr)
            visited.add(curr)
            next_nodes = [n for n in adj[curr] if n not in visited]
            if next_nodes:
                curr = next_nodes[0]
            else:
                break
                
        self._clear_stage_lines()
        self._animate_tour(tour, "#E91E63")
        self._update_results(self.lbl_gr, tour, total_cost)
        self.info_lbl.config(text="Greedy edge routing completed successfully!")
        self.is_running = False

    def _run_2opt(self):
        if not self.current_tour or len(self.current_tour) < 3:
            self.info_lbl.config(text="Run NN or Greedy first!"); return
        if self.is_running: return
        self.is_running = True
        
        self._clear_stage_lines()
        self._clear_path_lines()
        self._draw_base_map()
        
        tour = list(self.current_tour)
        N = len(tour)
        improved = True
        
        cost = 0.0
        for i in range(N):
            _, d = self.get_shortest_path(tour[i], tour[(i+1)%N])
            cost += d
            
        self._animate_tour(tour, "#8A2BE2")
        
        passes = 0
        while improved and passes < 1:
            improved = False
            passes += 1
            for i in range(N - 1):
                for j in range(i + 2, N):
                    if i == 0 and j == N - 1:
                        continue
                    
                    u1, v1 = tour[i], tour[i+1]
                    u2, v2 = tour[j], tour[(j+1)%N]
                    
                    _, d_u1_v1 = self.get_shortest_path(u1, v1)
                    _, d_u2_v2 = self.get_shortest_path(u2, v2)
                    _, d_u1_u2 = self.get_shortest_path(u1, u2)
                    _, d_v1_v2 = self.get_shortest_path(v1, v2)
                    
                    db = d_u1_v1 + d_u2_v2
                    da = d_u1_u2 + d_v1_v2
                    
                    if da < db - 1e-9:
                        tour[i+1:j+1] = reversed(tour[i+1:j+1])
                        cost = cost - db + da
                        improved = True
                        
                        self._clear_path_lines()
                        self._animate_tour(tour, "#8A2BE2")
                        self._update_results(self.lbl_2opt, tour, cost)
                        self.info_lbl.config(text=f"[2-Opt Refinement] Optimized Cost: {cost * 3.2:.0f} meters")
                        self.update()
                        self._interruptible_pause(500)
                        
        self.info_lbl.config(text="2-Opt optimization completed successfully!")
        self.is_running = False"""

# The rewritten MainApp class
main_app_class = """class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("C-Integrated Dual-Mode Algorithm Visualizer")
        self.geometry("1400x750")
        self.configure(bg="#2b2b2b")
        
        # Title
        self.title_lbl = tk.Label(self, text="Advanced Algorithmic Graph & Memory Visualizer", font=("Helvetica", 24, "bold"), bg="#2b2b2b", fg="#ffffff")
        self.title_lbl.pack(pady=10)
        
        # Tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#2b2b2b', borderwidth=0)
        style.configure('TNotebook.Tab', font=('Helvetica', 14), padding=[20, 5])
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=10)
        
        self.tsp_tab = TSPVisualizer(self.notebook)
        self.israel_tab = IsraelRoadTSPVisualizer(self.notebook)
        self.sort_tab = SortVisualizer(self.notebook)
        
        self.notebook.add(self.tsp_tab, text="Euclidean TSP")
        self.notebook.add(self.israel_tab, text="Ramat Efal Friend's Router")
        self.notebook.add(self.sort_tab, text="Array Sorting")
"""

# Let's replace MainApp with israel_class + main_app_class!
# We will match from class MainApp(tk.Tk): to the end of MainApp constructor (where self.notebook.add(...) happens).
target_segment_start = content.find("class MainApp(tk.Tk):")
target_segment_end = content.find('self.notebook.add(self.sort_tab, text="Mode 2: Array Sorting Visualizer")')

if target_segment_start == -1 or target_segment_end == -1:
    print(f"Error finding segment boundary! start: {target_segment_start}, end: {target_segment_end}")
    exit(1)

# Find the end of that statement line
line_end_idx = content.find('\\n', target_segment_end)
if line_end_idx == -1:
    line_end_idx = len(content)

new_content = content[:target_segment_start] + israel_class + "\\n\\n\\n" + main_app_class + content[line_end_idx:]

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Insertion completed successfully!")
