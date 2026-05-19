import re

def main():
    filepath = "/Users/omriherzberg/Desktop/ex_2_plus/visualize_ui.py"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add FFI bindings for tsp_1opt and tsp_2opt
    target_ffi = """tsp_lib.tsp_max_1_tree.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, TSP_CALLBACK_TYPE]
tsp_lib.tsp_max_1_tree.restype = None"""
    replacement_ffi = """tsp_lib.tsp_max_1_tree.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, TSP_CALLBACK_TYPE]
tsp_lib.tsp_max_1_tree.restype = None

tsp_lib.tsp_1opt.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, ctypes.POINTER(ctypes.c_int), TSP_CALLBACK_TYPE]
tsp_lib.tsp_1opt.restype = ctypes.c_double

tsp_lib.tsp_2opt.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, ctypes.POINTER(ctypes.c_int), TSP_CALLBACK_TYPE]
tsp_lib.tsp_2opt.restype = ctypes.c_double"""
    if target_ffi in content:
        content = content.replace(target_ffi, replacement_ffi)
        print("Successfully injected FFI bindings.")
    else:
        print("ERROR: target_ffi not found.")

    # 2. Update self.algo_result_labels and add btn_1opt / btn_2opt in TSPVisualizer.__init__
    target_lb = """        # Lower Bound column
        lb_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        lb_col.pack(side=tk.LEFT, padx=5)
        self.btn_lower_bound = tk.Button(lb_col, text="5. Lower Bound", command=self.start_lower_bound, font=("Helvetica", 11), width=16)
        self.btn_lower_bound.pack()
        self.lbl_lb_comp = tk.Label(lb_col, text="O(N³)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_lb_comp.pack()
        self.lbl_lb_result = tk.Label(lb_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#FFD700")
        self.lbl_lb_result.pack()"""

    replacement_lb = """        # Lower Bound column
        lb_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        lb_col.pack(side=tk.LEFT, padx=5)
        self.btn_lower_bound = tk.Button(lb_col, text="5. Lower Bound", command=self.start_lower_bound, font=("Helvetica", 11), width=16)
        self.btn_lower_bound.pack()
        self.lbl_lb_comp = tk.Label(lb_col, text="O(N³)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_lb_comp.pack()
        self.lbl_lb_result = tk.Label(lb_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#FFD700")
        self.lbl_lb_result.pack()

        # 1-Opt column
        opt1_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        opt1_col.pack(side=tk.LEFT, padx=5)
        self.btn_1opt = tk.Button(opt1_col, text="6. 1-Opt Refine", command=self.start_1opt, font=("Helvetica", 11), width=16)
        self.btn_1opt.pack()
        self.lbl_1opt_comp = tk.Label(opt1_col, text="O(N²)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_1opt_comp.pack()
        self.lbl_1opt_result = tk.Label(opt1_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#3498db")
        self.lbl_1opt_result.pack()

        # 2-Opt column
        opt2_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        opt2_col.pack(side=tk.LEFT, padx=5)
        self.btn_2opt = tk.Button(opt2_col, text="7. 2-Opt Refine", command=self.start_2opt, font=("Helvetica", 11), width=16)
        self.btn_2opt.pack()
        self.lbl_2opt_comp = tk.Label(opt2_col, text="O(N²)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_2opt_comp.pack()
        self.lbl_2opt_result = tk.Label(opt2_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#8A2BE2")
        self.lbl_2opt_result.pack()"""

    if target_lb in content:
        content = content.replace(target_lb, replacement_lb)
        print("Successfully injected 1-Opt and 2-Opt columns.")
    else:
        print("ERROR: target_lb not found.")

    # 3. Update self.algo_result_labels in TSPVisualizer.__init__
    target_labels = """        self.algo_result_labels = {
            "Nearest Neighbor": self.lbl_nn_result,
            "Greedy": self.lbl_greedy_result,
            "Christofides": self.lbl_ch_result,
            "Brute Force": self.lbl_bf_result,
        }"""
    replacement_labels = """        self.algo_result_labels = {
            "Nearest Neighbor": self.lbl_nn_result,
            "Greedy": self.lbl_greedy_result,
            "Christofides": self.lbl_ch_result,
            "Brute Force": self.lbl_bf_result,
            "1-Opt Refinement": self.lbl_1opt_result,
            "2-Opt Refinement": self.lbl_2opt_result,
        }"""
    if target_labels in content:
        content = content.replace(target_labels, replacement_labels)
        print("Successfully updated self.algo_result_labels.")
    else:
        print("ERROR: target_labels not found.")

    # 4. Initialize self.last_path in TSPVisualizer.__init__
    target_init = """        self.user_path = []
        self.path_lines = []"""
    replacement_init = """        self.user_path = []
        self.last_path = []
        self.path_lines = []"""
    if target_init in content:
        content = content.replace(target_init, replacement_init)
        print("Successfully initialized self.last_path.")
    else:
        print("ERROR: target_init not found.")

    # 5. Populate self.last_path in _on_tsp_cb (event_type == 3)
    target_cb_done = """                    if self.best_dist != float('inf') and path_ptr and path_len == self.num_elements:
                        self._draw_algo_path(path_ptr, path_len, color="#ffc66d", width=2)
                        self._show_distance_badge(f"Final ({self.current_algo})", self.best_dist, "#ffc66d")"""
    replacement_cb_done = """                    if self.best_dist != float('inf') and path_ptr and path_len == self.num_elements:
                        self._draw_algo_path(path_ptr, path_len, color="#ffc66d", width=2)
                        self._show_distance_badge(f"Final ({self.current_algo})", self.best_dist, "#ffc66d")
                        self.last_path = [path_ptr[idx] for idx in range(path_len)]"""
    if target_cb_done in content:
        content = content.replace(target_cb_done, replacement_cb_done)
        print("Successfully updated self.last_path assignment in callback (done).")
    else:
        print("ERROR: target_cb_done not found.")

    # 6. Insert opt uncrossing / move / evaluating event handlers in _on_tsp_cb
    target_cb_lb = """            elif event_type == 8:  # Lower Bound: Final Max 1-Tree Confirmed"""
    replacement_cb_opt = """            elif event_type == 10:  # EVENT_2OPT_SWAP
                self.best_dist = current_dist
                self.last_path = [path_ptr[idx] for idx in range(path_len)]
                self._clear_stage_lines()
                self._draw_algo_path(path_ptr, path_len, color="#8A2BE2", width=2)
                self._show_distance_badge("2-Opt Swap", current_dist, "#8A2BE2")
                self.info_label.config(text=f"[2-Opt Swap!] Dist: {current_dist:.2f} | Paths: {self.eval_count}")
                self.update()
                if self.speed_slider.get() < 500:
                    self._interruptible_pause(300)

            elif event_type == 11:  # EVENT_1OPT_SWAP
                self.best_dist = current_dist
                self.last_path = [path_ptr[idx] for idx in range(path_len)]
                self._clear_stage_lines()
                self._draw_algo_path(path_ptr, path_len, color="#3498db", width=2)
                self._show_distance_badge("1-Opt Move", current_dist, "#3498db")
                self.info_label.config(text=f"[1-Opt Move!] Dist: {current_dist:.2f} | Paths: {self.eval_count}")
                self.update()
                if self.speed_slider.get() < 500:
                    self._interruptible_pause(300)

            elif event_type == 12:  # EVENT_2OPT_EVALUATING
                self.eval_count += 1
                if self.eval_count % 100 == 0:
                    self.update()
                    if self.abort_requested:
                        self._clear_stage_lines()
                        return 1
                self._clear_stage_lines()
                for k in range(0, path_len - 1, 2):
                    n1, n2 = path_ptr[k], path_ptr[k+1]
                    x1, y1 = self.c_array[n1].x, self.c_array[n1].y
                    x2, y2 = self.c_array[n2].x, self.c_array[n2].y
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#FF4081", width=2, dash=(2, 2))
                    self.stage_lines.append(line)
                self.info_label.config(text=f"[2-Opt Evaluating] Dist: {current_dist:.2f} | Checked: {self.eval_count}")
                self.update()
                self.my_sleep()

            elif event_type == 13:  # EVENT_1OPT_EVALUATING
                self.eval_count += 1
                if self.eval_count % 100 == 0:
                    self.update()
                    if self.abort_requested:
                        self._clear_stage_lines()
                        return 1
                self._clear_stage_lines()
                for k in range(0, path_len - 1, 2):
                    n1, n2 = path_ptr[k], path_ptr[k+1]
                    x1, y1 = self.c_array[n1].x, self.c_array[n1].y
                    x2, y2 = self.c_array[n2].x, self.c_array[n2].y
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#FF4081", width=2, dash=(2, 2))
                    self.stage_lines.append(line)
                self.info_label.config(text=f"[1-Opt Evaluating] Dist: {current_dist:.2f} | Checked: {self.eval_count}")
                self.update()
                self.my_sleep()

            elif event_type == 8:  # Lower Bound: Final Max 1-Tree Confirmed"""
    if target_cb_lb in content:
        content = content.replace(target_cb_lb, replacement_cb_opt)
        print("Successfully injected local search uncrossing and evaluation handlers in callback.")
    else:
        print("ERROR: target_cb_lb not found.")

    # 7. Update _finish_run to enable btn_1opt / btn_2opt
    target_finish = """        self.btn_nn.config(state=tk.NORMAL)
        self.btn_greedy.config(state=tk.NORMAL)
        self.btn_christofides.config(state=tk.NORMAL)
        self.btn_brute.config(state=tk.NORMAL)
        self.btn_lower_bound.config(state=tk.NORMAL)
        self.btn_regen.config(state=tk.NORMAL)"""
    replacement_finish = """        self.btn_nn.config(state=tk.NORMAL)
        self.btn_greedy.config(state=tk.NORMAL)
        self.btn_christofides.config(state=tk.NORMAL)
        self.btn_brute.config(state=tk.NORMAL)
        self.btn_lower_bound.config(state=tk.NORMAL)
        self.btn_1opt.config(state=tk.NORMAL)
        self.btn_2opt.config(state=tk.NORMAL)
        self.btn_regen.config(state=tk.NORMAL)"""
    if target_finish in content:
        content = content.replace(target_finish, replacement_finish)
        print("Successfully updated _finish_run.")
    else:
        print("ERROR: target_finish not found.")

    # 8. Update _prepare_run to disable btn_1opt / btn_2opt and map call names
    target_prepare_map = """        algo_map = {
            "start_nearest_neighbor": "Nearest Neighbor",
            "start_greedy": "Greedy",
            "start_christofides": "Christofides",
            "start_brute_force": "Brute Force",
            "start_lower_bound": "Lower Bound"
        }"""
    replacement_prepare_map = """        algo_map = {
            "start_nearest_neighbor": "Nearest Neighbor",
            "start_greedy": "Greedy",
            "start_christofides": "Christofides",
            "start_brute_force": "Brute Force",
            "start_lower_bound": "Lower Bound",
            "start_1opt": "1-Opt Refinement",
            "start_2opt": "2-Opt Refinement"
        }"""
    if target_prepare_map in content:
        content = content.replace(target_prepare_map, replacement_prepare_map)
        print("Successfully updated algo_map in _prepare_run.")
    else:
        print("ERROR: target_prepare_map not found.")

    target_prepare_disable = """        self.btn_nn.config(state=tk.DISABLED)
        self.btn_greedy.config(state=tk.DISABLED)
        self.btn_christofides.config(state=tk.DISABLED)
        self.btn_brute.config(state=tk.DISABLED)
        self.btn_lower_bound.config(state=tk.DISABLED)
        self.btn_regen.config(state=tk.DISABLED)"""
    replacement_prepare_disable = """        self.btn_nn.config(state=tk.DISABLED)
        self.btn_greedy.config(state=tk.DISABLED)
        self.btn_christofides.config(state=tk.DISABLED)
        self.btn_brute.config(state=tk.DISABLED)
        self.btn_lower_bound.config(state=tk.DISABLED)
        self.btn_1opt.config(state=tk.DISABLED)
        self.btn_2opt.config(state=tk.DISABLED)
        self.btn_regen.config(state=tk.DISABLED)"""
    if target_prepare_disable in content:
        content = content.replace(target_prepare_disable, replacement_prepare_disable)
        print("Successfully updated btn disables in _prepare_run.")
    else:
        print("ERROR: target_prepare_disable not found.")

    # 9. Append start_1opt and start_2opt methods to TSPVisualizer
    target_start_lb = """    def start_lower_bound(self):
        if not self._prepare_run(): return
        self.info_label.config(text="Starting Max 1-Tree Lower Bound computation...", fg="#a9b7c6")
        self.update()
        tsp_lib.tsp_max_1_tree(self.c_array, self.num_elements, self.c_callback)"""

    replacement_start_lb = """    def start_lower_bound(self):
        if not self._prepare_run(): return
        self.info_label.config(text="Starting Max 1-Tree Lower Bound computation...", fg="#a9b7c6")
        self.update()
        tsp_lib.tsp_max_1_tree(self.c_array, self.num_elements, self.c_callback)

    def start_1opt(self):
        if not hasattr(self, 'last_path') or not self.last_path or len(self.last_path) != self.num_elements:
            self.info_label.config(text="Run Nearest-Neighbor, Greedy, or Christofides first to construct an initial tour!", fg="#ff5252")
            return
        if not self._prepare_run(): return
        self.info_label.config(text="Starting 1-Opt Node Relocation Local Search...", fg="#a9b7c6")
        self.update()
        
        # Prepare in-place path array
        PathArrType = ctypes.c_int * self.num_elements
        path_arr = PathArrType(*self.last_path)
        
        # Call C library
        tsp_lib.tsp_1opt(self.c_array, self.num_elements, path_arr, self.c_callback)

    def start_2opt(self):
        if not hasattr(self, 'last_path') or not self.last_path or len(self.last_path) != self.num_elements:
            self.info_label.config(text="Run Nearest-Neighbor, Greedy, or Christofides first to construct an initial tour!", fg="#ff5252")
            return
        if not self._prepare_run(): return
        self.info_label.config(text="Starting 2-Opt Edge-Uncrossing Local Search...", fg="#a9b7c6")
        self.update()
        
        # Prepare in-place path array
        PathArrType = ctypes.c_int * self.num_elements
        path_arr = PathArrType(*self.last_path)
        
        # Call C library
        tsp_lib.tsp_2opt(self.c_array, self.num_elements, path_arr, self.c_callback)"""

    if target_start_lb in content:
        content = content.replace(target_start_lb, replacement_start_lb)
        print("Successfully appended start_1opt and start_2opt methods.")
    else:
        print("ERROR: target_start_lb not found.")

    # 10. Rewrite IsraelRoadTSPVisualizer._build_ui to use compact two-column layout
    target_israel_ui = """        # --- TAB 1: TSP ROUTING ---
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
        self.tour_text.pack(fill=tk.BOTH, expand=True)"""

    replacement_israel_ui = """        # --- TAB 1: TSP ROUTING (TWO-COLUMN COMPACT LAYOUT) ---
        left_col = tk.Frame(tab_main, bg="#1e1e2e")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 8), pady=4)

        right_col = tk.Frame(tab_main, bg="#1e1e2e")
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 4), pady=4)

        # LEFT COLUMN ELEMENTS: Presets & Stats
        pf = tk.LabelFrame(left_col, text="Quick Presets & Actions", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        pf.pack(fill=tk.X, pady=(0, 8))

        btn_frame = tk.Frame(pf, bg="#1e1e2e")
        btn_frame.pack(fill=tk.X, pady=2)
        
        tk.Button(btn_frame, text="🏡 Seminary Center", command=lambda: self._add_preset(13),
                  font=("Helvetica", 9), width=16).grid(row=0, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="🍽️ Shula BaHatzer", command=lambda: self._add_preset(0),
                  font=("Helvetica", 9), width=16).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(btn_frame, text="👵 Neve Ef'al Care", command=lambda: self._add_preset(1),
                  font=("Helvetica", 9), width=16).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="🏥 Sheba East Gate", command=lambda: self._add_preset(10),
                  font=("Helvetica", 9), width=16).grid(row=1, column=1, padx=2, pady=2)
        
        tk.Button(pf, text="❌ Clear Pinned Locations", command=self._clear_pins,
                  font=("Helvetica", 10, "bold"), bg="#dc3545", fg="#ffffff", activebackground="#c82333").pack(fill=tk.X, pady=(4, 0))

        rf = tk.LabelFrame(left_col, text="Route Travel Cost", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        rf.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        self.lbl_primary   = tk.Label(rf, text="—", font=("Courier", 14, "bold"), bg="#1e1e2e", fg="#ffc66d")
        self.lbl_primary.pack()
        self.lbl_secondary = tk.Label(rf, text="", font=("Courier", 11), bg="#1e1e2e", fg="#a9b7c6")
        self.lbl_secondary.pack()

        # RIGHT COLUMN ELEMENTS: Algorithms & Tour Sequence
        af = tk.LabelFrame(right_col, text="TSP Algorithms", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        af.pack(fill=tk.X, pady=(0, 8))

        def algo_col(lf, btn_text, comp, cmd, fg_color):
            col = tk.Frame(lf, bg="#1e1e2e")
            col.pack(fill=tk.X, pady=1)
            tk.Button(col, text=btn_text, command=cmd,
                      font=("Helvetica", 10), width=32).pack()
            lbl = tk.Label(col, text="", font=("Courier", 9), bg="#1e1e2e", fg=fg_color)
            lbl.pack()
            return lbl

        self.lbl_nn    = algo_col(af, "1. Nearest Neighbor (Topological)", "O(N²)",     self._run_nn,     "#4CAF50")
        self.lbl_gr    = algo_col(af, "2. Greedy Edge-Insertion",        "O(N²logN)", self._run_greedy, "#E91E63")
        self.lbl_2opt  = algo_col(af, "Optimize: 2-Opt refinement",      "O(N²)",     self._run_2opt,   "#8A2BE2")

        cf = tk.LabelFrame(right_col, text="Optimal Path Sequence", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#ffd700", padx=8, pady=4)
        cf.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        self.tour_text = tk.Text(cf, font=("Courier", 9), bg="#12171e", fg="#a9b7c6",
                                 height=4, width=32, state=tk.DISABLED, relief=tk.FLAT)
        self.tour_text.pack(fill=tk.BOTH, expand=True)"""

    if target_israel_ui in content:
        content = content.replace(target_israel_ui, replacement_israel_ui)
        print("Successfully transformed IsraelRoadTSPVisualizer._build_ui into a beautiful compact two-column layout.")
    else:
        print("ERROR: target_israel_ui not found.")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("ALL REPLACEMENTS COMPLETED!")

if __name__ == "__main__":
    main()
