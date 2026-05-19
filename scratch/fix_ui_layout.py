import os

lib_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
filepath = os.path.join(lib_dir, "visualize_ui.py")

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update get_shortest_path to dynamically support all nodes
old_path = """    def get_shortest_path(self, start, end):
        if start == end:
            return [start], 0.0
        dist = {i: float('inf') for i in range(25)}
        prev = {i: None for i in range(25)}
        dist[start] = 0.0
        Q = list(range(25))"""

new_path = """    def get_shortest_path(self, start, end):
        if start == end:
            return [start], 0.0
        dist = {i: float('inf') for i in self.nodes.keys()}
        prev = {i: None for i in self.nodes.keys()}
        dist[start] = 0.0
        Q = list(self.nodes.keys())"""

content = content.replace(old_path, new_path)

# 2. Extract _build_ui block
start_idx = content.find("    def _build_ui(self):")
end_idx = content.find("    def _on_canvas_click(self, event):")

if start_idx != -1 and end_idx != -1:
    new_build_ui = """    def _build_ui(self):
        from tkinter import ttk
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
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Double-Button-1>", self._on_canvas_double_click)
        self.canvas.bind("<Button-2>", self._on_canvas_right_click)
        self.canvas.bind("<Button-3>", self._on_canvas_right_click)
        self.canvas.bind("<Shift-Button-1>", getattr(self, '_on_canvas_shift_click', self._on_canvas_click))

        side = tk.Frame(body, bg="#1e1e2e", width=420)
        side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0))
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1e1e2e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2c3e50', foreground='#ffffff', padding=[10, 5], font=('Helvetica', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#007bff')])
        
        notebook = ttk.Notebook(side)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        tab_main = tk.Frame(notebook, bg="#1e1e2e")
        tab_editor = tk.Frame(notebook, bg="#1e1e2e")
        
        notebook.add(tab_main, text="TSP Routing Algorithms")
        notebook.add(tab_editor, text="Graph Alignment Editor")

        # --- TAB 1: TSP ROUTING ---
        pf = tk.LabelFrame(tab_main, text="Quick Presets & Actions", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        pf.pack(fill=tk.X, pady=(4, 8))

        btn_frame = tk.Frame(pf, bg="#1e1e2e")
        btn_frame.pack(fill=tk.X, pady=2)
        
        tk.Button(btn_frame, text="🏡 Seminary Center", command=lambda: self._add_preset(13),
                  font=("Helvetica", 10), width=18).grid(row=0, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="🍽️ Shula BaHatzer", command=lambda: self._add_preset(0),
                  font=("Helvetica", 10), width=18).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(btn_frame, text="👵 Neve Ef'al Care", command=lambda: self._add_preset(1),
                  font=("Helvetica", 10), width=18).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="🏥 Sheba East Gate", command=lambda: self._add_preset(10),
                  font=("Helvetica", 10), width=18).grid(row=1, column=1, padx=2, pady=2)
        
        tk.Button(pf, text="❌ Clear Pinned Locations", command=self._clear_pins,
                  font=("Helvetica", 10, "bold"), bg="#dc3545", fg="#ffffff", activebackground="#c82333").pack(fill=tk.X, pady=(4, 0))

        # Algorithm panel
        af = tk.LabelFrame(tab_main, text="TSP Algorithms", font=("Helvetica", 11, "bold"),
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
        rf = tk.LabelFrame(tab_main, text="Route Travel Cost", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        rf.pack(fill=tk.X, pady=(0, 8))
        self.lbl_primary   = tk.Label(rf, text="—", font=("Courier", 14, "bold"), bg="#1e1e2e", fg="#ffc66d")
        self.lbl_primary.pack()
        self.lbl_secondary = tk.Label(rf, text="", font=("Courier", 11), bg="#1e1e2e", fg="#a9b7c6")
        self.lbl_secondary.pack()

        # Tour order list
        cf = tk.LabelFrame(tab_main, text="Optimal Path Sequence", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        cf.pack(fill=tk.BOTH, expand=True)
        self.tour_text = tk.Text(cf, font=("Courier", 9), bg="#12171e", fg="#a9b7c6",
                                 height=8, width=32, state=tk.DISABLED, relief=tk.FLAT)
        self.tour_text.pack(fill=tk.BOTH, expand=True)

        # --- TAB 2: GRAPH EDITOR ---
        ef = tk.LabelFrame(tab_editor, text="🗺️ Interactive Alignment Tools", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#54a0ff", padx=8, pady=4)
        ef.pack(fill=tk.BOTH, expand=True, pady=(4, 8))
        
        self.btn_edit_mode = tk.Button(ef, text="Edit Mode: Pin Houses", command=self._toggle_edit_mode,
                                       font=("Helvetica", 11, "bold"), width=32, bg="#54a0ff", pady=8)
        self.btn_edit_mode.pack(pady=(10, 20))
        
        help_text = "Instructions for Graph Editor:\\n\\n1. Toggle Edit Mode on.\\n2. Drag yellow dots to position them on roads.\\n3. Double-click empty space to Add Node.\\n4. Right-click a dot to Delete Node.\\n5. Shift + Click dot A, then Shift + Click dot B to connect or disconnect them.\\n6. Click Save below to permanently update code!"
        tk.Label(ef, text=help_text, font=("Helvetica", 10), bg="#1e1e2e", fg="#a9b7c6",
                 justify=tk.LEFT, wraplength=340).pack(fill=tk.X, pady=10, padx=10)
                 
        tk.Button(ef, text="💾 Save Graph Coordinates Permanently", command=self._save_graph_to_file,
                  font=("Helvetica", 11, "bold"), width=32, bg="#2ecc71", fg="black", pady=8).pack(pady=(20, 10))

"""
    content = content[:start_idx] + new_build_ui + content[end_idx:]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed UI layout successfully!")
else:
    print("Error: Could not locate _build_ui method bounds.")
    exit(1)
