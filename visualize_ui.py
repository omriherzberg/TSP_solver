import ctypes
import tkinter as tk
from tkinter import ttk
import os
import random
import math

# ==========================================
# CTYPES BINDINGS
# ==========================================
class BusLine(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * 21),
        ("distance", ctypes.c_int),
        ("duration", ctypes.c_int),
        ("frequency", ctypes.c_int)
    ]

class BusStation(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * 21),
        ("x", ctypes.c_double),
        ("y", ctypes.c_double)
    ]

SORT_CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)
TSP_CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_double)

lib_dir = os.path.dirname(os.path.abspath(__file__))
viz_lib = ctypes.CDLL(os.path.join(lib_dir, 'libvisualize.dylib'))
tsp_lib = ctypes.CDLL(os.path.join(lib_dir, 'libtsp.dylib'))

viz_lib.visualize_bubble_sort_c.argtypes = [ctypes.POINTER(BusLine), ctypes.POINTER(BusLine), SORT_CALLBACK_TYPE]
viz_lib.visualize_bubble_sort_c.restype = None

viz_lib.visualize_quick_sort_c.argtypes = [ctypes.POINTER(BusLine), ctypes.POINTER(BusLine), ctypes.c_int, SORT_CALLBACK_TYPE]
viz_lib.visualize_quick_sort_c.restype = None

tsp_lib.tsp_brute_force.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, TSP_CALLBACK_TYPE]
tsp_lib.tsp_brute_force.restype = None

tsp_lib.tsp_christofides.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, TSP_CALLBACK_TYPE]
tsp_lib.tsp_christofides.restype = None

tsp_lib.tsp_greedy.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, TSP_CALLBACK_TYPE]
tsp_lib.tsp_greedy.restype = None

tsp_lib.tsp_nearest_neighbor.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, TSP_CALLBACK_TYPE]
tsp_lib.tsp_nearest_neighbor.restype = None

tsp_lib.tsp_max_1_tree.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, TSP_CALLBACK_TYPE]
tsp_lib.tsp_max_1_tree.restype = None

tsp_lib.tsp_1opt.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, ctypes.POINTER(ctypes.c_int), TSP_CALLBACK_TYPE]
tsp_lib.tsp_1opt.restype = ctypes.c_double

tsp_lib.tsp_2opt.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, ctypes.POINTER(ctypes.c_int), TSP_CALLBACK_TYPE]
tsp_lib.tsp_2opt.restype = ctypes.c_double

tsp_lib.tsp_simulated_annealing.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, ctypes.POINTER(ctypes.c_int), TSP_CALLBACK_TYPE, ctypes.c_double, ctypes.c_double]
tsp_lib.tsp_simulated_annealing.restype = ctypes.c_double

tsp_lib.get_tsp_comparison_count.argtypes = []
tsp_lib.get_tsp_comparison_count.restype = ctypes.c_longlong

tsp_lib.reset_tsp_comparison_count.argtypes = []
tsp_lib.reset_tsp_comparison_count.restype = None

# ==========================================
# UI CLASSES
# ==========================================

class TSPVisualizer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#2b2b2b")
        
        self.canvas_width = 1200
        self.canvas_height = 420
        
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(pady=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        self.info_label = tk.Label(self, text="Ready for TSP. Click nodes to play, or run an algorithm.", font=("Helvetica", 16), bg="#2b2b2b", fg="#a9b7c6")
        self.info_label.pack(pady=5)
        
        # --- Top Control Frame (Map Settings & Game) ---
        self.control_frame = tk.Frame(self, bg="#2b2b2b")
        self.control_frame.pack(pady=5)
        
        tk.Label(self.control_frame, text="Nodes (2-1000):", bg="#2b2b2b", fg="white", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        self.nodes_var = tk.IntVar(value=9)
        self.nodes_spin = tk.Spinbox(self.control_frame, from_=2, to=1000, textvariable=self.nodes_var, width=5, font=("Helvetica", 12))
        self.nodes_spin.pack(side=tk.LEFT, padx=5)
        
        self.btn_regen = tk.Button(self.control_frame, text="Generate Map", command=self.generate_map, font=("Helvetica", 12))
        self.btn_regen.pack(side=tk.LEFT, padx=10)
        
        self.btn_check = tk.Button(self.control_frame, text="Grade My Route", command=self.check_route, font=("Helvetica", 12, "bold"), fg="green", state=tk.DISABLED)
        self.btn_check.pack(side=tk.LEFT, padx=10)
        
        self.btn_reset_user = tk.Button(self.control_frame, text="Reset My Route", command=self.reset_user_route, font=("Helvetica", 12))
        self.btn_reset_user.pack(side=tk.LEFT, padx=10)

        self.btn_random_route = tk.Button(self.control_frame, text="Generate Random Route", command=self.generate_random_route, font=("Helvetica", 12), fg="#ff9800")
        self.btn_random_route.pack(side=tk.LEFT, padx=10)
        
        # --- Algorithm Buttons with result labels ---
        self.algo_frame = tk.Frame(self, bg="#2b2b2b")
        self.algo_frame.pack(pady=5)

        # Nearest Neighbor column
        nn_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        nn_col.grid(row=0, column=0, padx=5, pady=2)
        self.btn_nn = tk.Button(nn_col, text="1. Nearest-Neighbor", command=self.start_nearest_neighbor, font=("Helvetica", 11), width=16)
        self.btn_nn.pack()
        self.lbl_nn_comp = tk.Label(nn_col, text="O(N²)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_nn_comp.pack()
        self.lbl_nn_result = tk.Label(nn_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#4CAF50")
        self.lbl_nn_result.pack()

        # Greedy column
        greedy_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        greedy_col.grid(row=0, column=1, padx=5, pady=2)
        self.btn_greedy = tk.Button(greedy_col, text="2. Greedy (Edge)", command=self.start_greedy, font=("Helvetica", 11), width=16)
        self.btn_greedy.pack()
        self.lbl_greedy_comp = tk.Label(greedy_col, text="O(N² log N)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_greedy_comp.pack()
        self.lbl_greedy_result = tk.Label(greedy_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#E91E63")
        self.lbl_greedy_result.pack()

        # Christofides column
        ch_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        ch_col.grid(row=0, column=2, padx=5, pady=2)
        self.btn_christofides = tk.Button(ch_col, text="3. Christofides", command=self.start_christofides, font=("Helvetica", 11), width=16)
        self.btn_christofides.pack()
        self.lbl_ch_comp = tk.Label(ch_col, text="O(N³)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_ch_comp.pack()
        self.lbl_ch_result = tk.Label(ch_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#03A9F4")
        self.lbl_ch_result.pack()

        # Brute Force column
        bf_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        bf_col.grid(row=0, column=3, padx=5, pady=2)
        self.btn_brute = tk.Button(bf_col, text="4. Brute-Force", command=self.start_brute_force, font=("Helvetica", 11), width=16)
        self.btn_brute.pack()
        self.lbl_bf_comp = tk.Label(bf_col, text="O(N!)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_bf_comp.pack()
        self.lbl_bf_result = tk.Label(bf_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#ffc66d")
        self.lbl_bf_result.pack()

        # Lower Bound column
        lb_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        lb_col.grid(row=0, column=4, padx=5, pady=2)
        self.btn_lower_bound = tk.Button(lb_col, text="5. Lower Bound", command=self.start_lower_bound, font=("Helvetica", 11), width=16)
        self.btn_lower_bound.pack()
        self.lbl_lb_comp = tk.Label(lb_col, text="O(N³)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_lb_comp.pack()
        self.lbl_lb_result = tk.Label(lb_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#FFD700")
        self.lbl_lb_result.pack()

        # 1-Opt column
        opt1_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        opt1_col.grid(row=1, column=0, padx=5, pady=2)
        self.btn_1opt = tk.Button(opt1_col, text="6. 1-Opt Refine", command=self.start_1opt, font=("Helvetica", 11), width=16)
        self.btn_1opt.pack()
        self.lbl_1opt_comp = tk.Label(opt1_col, text="O(N²)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_1opt_comp.pack()
        self.lbl_1opt_result = tk.Label(opt1_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#3498db")
        self.lbl_1opt_result.pack()

        # 2-Opt column
        opt2_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        opt2_col.grid(row=1, column=1, padx=5, pady=2)
        self.btn_2opt = tk.Button(opt2_col, text="7. 2-Opt Refine", command=self.start_2opt, font=("Helvetica", 11), width=16)
        self.btn_2opt.pack()
        self.lbl_2opt_comp = tk.Label(opt2_col, text="O(N²)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_2opt_comp.pack()
        self.lbl_2opt_result = tk.Label(opt2_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#8A2BE2")
        self.lbl_2opt_result.pack()

        # Simulated Annealing column
        sa_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        sa_col.grid(row=1, column=2, padx=5, pady=2)
        self.btn_sa = tk.Button(sa_col, text="8. Anneal Refine", command=self.start_simulated_annealing, font=("Helvetica", 11), width=16)
        self.btn_sa.pack()
        self.lbl_sa_comp = tk.Label(sa_col, text="Metaheuristic", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_sa_comp.pack()
        self.lbl_sa_result = tk.Label(sa_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#FFD700")
        self.lbl_sa_result.pack()

        # Abort + Speed (Moved to the far right of the top control frame)
        ctrl_col = tk.Frame(self.control_frame, bg="#2b2b2b")
        ctrl_col.pack(side=tk.RIGHT, padx=15, fill=tk.Y)
        self.btn_abort = tk.Button(ctrl_col, text="ABORT", command=self.abort_process, font=("Helvetica", 12, "bold"), fg="red")
        self.btn_abort.pack(side=tk.RIGHT, padx=10)
        self.speed_slider = tk.Scale(ctrl_col, from_=1, to=1000, orient=tk.HORIZONTAL, label="Actions/Sec", length=140, bg="#2b2b2b", fg="white", highlightthickness=0)
        self.speed_slider.set(10)
        self.speed_slider.pack(side=tk.RIGHT)
        
        # --- State ---
        self.c_array = None
        self.num_elements = 9
        self.c_callback = TSP_CALLBACK_TYPE(self._on_tsp_cb)
        self.is_running = False
        self.abort_requested = False
        self.current_algo = ""

        # Per-algorithm result tracking
        self.algo_result_labels = {
            "Nearest Neighbor": self.lbl_nn_result,
            "Greedy": self.lbl_greedy_result,
            "Christofides": self.lbl_ch_result,
            "Brute Force": self.lbl_bf_result,
            "1-Opt Refinement": self.lbl_1opt_result,
            "2-Opt Refinement": self.lbl_2opt_result,
            "Simulated Annealing": self.lbl_sa_result,
            "Lower Bound": self.lbl_lb_result,
        }
        
        self.user_path = []
        self.last_path = []
        self.path_lines = []
        self.stage_lines = []
        self.card_lines = []
        self.eval_count = 0
        self.best_dist = float('inf')
        
        self.generate_map()

    def my_sleep(self):
        """Interruptible sleep: wakes every 50ms to check abort_requested."""
        actions_per_sec = self.speed_slider.get()
        if actions_per_sec >= 1000:
            self.update()
            return
        
        delay_ms = int(1000 / actions_per_sec)
        if delay_ms <= 0: delay_ms = 1
        
        elapsed = 0
        chunk = 50  # check abort every 50ms
        while elapsed < delay_ms:
            if self.abort_requested:
                return
            wait = min(chunk, delay_ms - elapsed)
            var = tk.IntVar()
            self.after(wait, var.set, 1)
            self.wait_variable(var)
            elapsed += wait

    def _interruptible_pause(self, ms):
        """Pause for `ms` milliseconds, returning early if aborted."""
        elapsed = 0
        chunk = 50
        while elapsed < ms:
            if self.abort_requested:
                return
            self.update()
            wait = min(chunk, ms - elapsed)
            var = tk.IntVar()
            self.after(wait, var.set, 1)
            self.wait_variable(var)
            elapsed += wait

    def generate_map(self):
        if self.is_running: return
        
        try:
            val = self.nodes_var.get()
            if val < 2: val = 2
            if val > 1000: val = 1000
            self.num_elements = val
        except:
            self.num_elements = 9
            self.nodes_var.set(9)
            
        self.canvas.delete("all")
        self.path_lines = []
        self.stage_lines = []
        self.card_lines = []
        self.user_path = []
        self.last_path = []
        self.dist_badge = None
        # Clear per-algo result labels since the map changed
        for lbl in self.algo_result_labels.values():
            lbl.config(text="")
        self.info_label.config(text=f"Map Generated ({self.num_elements} nodes). Click nodes to play, or run algorithm.", fg="#a9b7c6")
        self.btn_check.config(state=tk.DISABLED)
        
        ArrayType = BusStation * self.num_elements
        self.c_array = ArrayType()
        
        padding = 40
        for i in range(self.num_elements):
            name = f"Stn {i}".encode('utf-8')
            # Leave left 380px empty for the explanation cards and buttons
            x = random.uniform(380, self.canvas_width - padding)
            y = random.uniform(padding, self.canvas_height - padding)
            
            self.c_array[i].name = name
            self.c_array[i].x = x
            self.c_array[i].y = y
            
            # Scale visual elements based on number of nodes
            if self.num_elements <= 30:
                r = 8
                self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#ffc66d", outline="#ffffff", width=2, tags=f"node_{i}")
                self.canvas.create_text(x, y-15, text=f"{i}", fill="#ffffff", font=("Helvetica", 10, "bold"), tags=f"label_{i}")
            else:
                r = 3
                self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#ffc66d", outline="", tags=f"node_{i}")

    def reset_user_route(self):
        if self.is_running: return
        for line in self.path_lines:
            self.canvas.delete(line)
        self.path_lines = []
        self.user_path = []
        self.btn_check.config(state=tk.DISABLED)
        self.info_label.config(text="Route reset. Click any node to start.", fg="#a9b7c6")
        
        for i in range(self.num_elements):
            self.canvas.itemconfig(f"node_{i}", fill="#ffc66d")

    def generate_random_route(self):
        if self.is_running: return
        
        # Clear per-algo result labels since the starting state changed
        for lbl in self.algo_result_labels.values():
            lbl.config(text="")
            
        
        # Shuffle nodes randomly
        self.last_path = list(range(self.num_elements))
        random.shuffle(self.last_path)
        
        # Calculate random path distance
        init_dist = 0.0
        for idx in range(self.num_elements):
            u = self.last_path[idx]
            v = self.last_path[(idx + 1) % self.num_elements]
            dx = self.c_array[u].x - self.c_array[v].x
            dy = self.c_array[u].y - self.c_array[v].y
            init_dist += (dx*dx + dy*dy)**0.5
            
        self.best_dist = init_dist
        
        # Draw path on canvas
        PathArrType = ctypes.c_int * self.num_elements
        path_arr = PathArrType(*self.last_path)
        self._draw_algo_path(path_arr, self.num_elements, color="#ff9800", width=2)
        
        self._show_distance_badge("Random Route", init_dist, "#ff9800")
        self.info_label.config(text=f"Generated Random Route (Cost: {init_dist:.2f} km). Click 1-Opt or 2-Opt to optimize it!", fg="#ff9800")

    def on_canvas_click(self, event):
        if self.is_running: return
        if len(self.user_path) > self.num_elements: return
            
        clicked_idx = -1
        # Dynamic click radius
        min_dist = 25 if self.num_elements <= 30 else 10
        
        for i in range(self.num_elements):
            x, y = self.c_array[i].x, self.c_array[i].y
            dist = math.hypot(x - event.x, y - event.y)
            if dist < min_dist:
                min_dist = dist
                clicked_idx = i
                break
                
        if clicked_idx != -1:
            if len(self.user_path) == 0:
                self.user_path.append(clicked_idx)
                self.canvas.itemconfig(f"node_{clicked_idx}", fill="#4CAF50")
                self.info_label.config(text=f"Started at Node {clicked_idx}. Connect the rest!", fg="#a9b7c6")
            else:
                if clicked_idx in self.user_path:
                    if clicked_idx == self.user_path[0] and len(self.user_path) == self.num_elements:
                        self._add_to_user_path(clicked_idx)
                        self.btn_check.config(state=tk.NORMAL)
                        self.info_label.config(text="Cycle Complete! Click 'Grade My Route' to get your score.", fg="#a9b7c6")
                else:
                    self._add_to_user_path(clicked_idx)
                    self.canvas.itemconfig(f"node_{clicked_idx}", fill="#2196F3")

    def _add_to_user_path(self, idx):
        prev_idx = self.user_path[-1]
        x1, y1 = self.c_array[prev_idx].x, self.c_array[prev_idx].y
        x2, y2 = self.c_array[idx].x, self.c_array[idx].y
        
        line = self.canvas.create_line(x1, y1, x2, y2, fill="#ffffff", width=2)
        self.canvas.tag_lower(line)
        self.path_lines.append(line)
        self.user_path.append(idx)

    def check_route(self):
        user_dist = 0.0
        for i in range(len(self.user_path) - 1):
            idx1 = self.user_path[i]
            idx2 = self.user_path[i+1]
            dx = self.c_array[idx1].x - self.c_array[idx2].x
            dy = self.c_array[idx1].y - self.c_array[idx2].y
            user_dist += math.hypot(dx, dy)
            
        results = {}
        def make_silent_cb(algo_name):
            def silent_cb(event_type, path_ptr, path_len, current_dist):
                if event_type == 2 and path_len == self.num_elements:
                    results[algo_name] = current_dist
                return 0
            return TSP_CALLBACK_TYPE(silent_cb)
            
        self.info_label.config(text="Calculating algorithm scores... Please wait.", fg="#a9b7c6")
        self.update()
        
        c_ch = make_silent_cb("ch")
        tsp_lib.tsp_christofides(self.c_array, self.num_elements, c_ch)
        
        c_gr = make_silent_cb("gr")
        tsp_lib.tsp_greedy(self.c_array, self.num_elements, c_gr)
        
        c_nn = make_silent_cb("nn")
        tsp_lib.tsp_nearest_neighbor(self.c_array, self.num_elements, c_nn)
        
        opt = float('inf')
        if self.num_elements <= 11:
            c_bf = make_silent_cb("bf")
            tsp_lib.tsp_brute_force(self.c_array, self.num_elements, c_bf)
            opt = results.get("bf", float('inf'))
            
        ch = results.get("ch", float('inf'))
        gr = results.get("gr", float('inf'))
        nn = results.get("nn", float('inf'))
        
        msg = f"Your Distance: {user_dist:.1f} | "
        best_ref = opt if self.num_elements <= 11 else min(ch, gr, nn)
        
        if self.num_elements <= 11:
            grade = int((opt / user_dist) * 100) if user_dist > 0 else 0
            if grade > 100: grade = 100
            msg += f"Optimal: {opt:.1f} | Grade: {grade}/100\n"
        else:
            grade = int((best_ref / user_dist) * 100) if user_dist > 0 else 0
            if grade > 100: grade = 100
            msg += f"Best Algorithm: {best_ref:.1f} | Grade: {grade}/100\n"
            
        msg += f"Nearest-Neighbor: {nn:.1f} | Greedy (Edge): {gr:.1f} | Christofides: {ch:.1f}\n"
        
        if self.num_elements <= 11 and math.isclose(user_dist, opt, rel_tol=1e-5):
            msg += "🏆 PERFECT SCORE! You found the absolute optimal path!"
            self.info_label.config(fg="#FFD700")
        elif user_dist <= nn and user_dist <= gr and user_dist <= ch:
            msg += "🥇 Amazing! You beat Nearest-Neighbor, Greedy, and Christofides!"
            self.info_label.config(fg="#4CAF50")
        elif user_dist <= gr:
            msg += "🥈 Great job! You beat the Greedy (Edge) Algorithm!"
            self.info_label.config(fg="#8bc34a")
        elif user_dist <= nn:
            msg += "🥉 Good effort! You beat the Nearest-Neighbor Algorithm!"
            self.info_label.config(fg="#ffeb3b")
        else:
            msg += "❌ You lost to our algorithms. Try again!"
            self.info_label.config(fg="#ff5252")
            
        self.info_label.config(text=msg)
        self.btn_check.config(state=tk.DISABLED)

    def _draw_algo_path(self, path_ptr, path_len, color, width, dash=None):
        for line in self.path_lines:
            self.canvas.delete(line)
        self.path_lines = []
        
        if path_len < 2: return
        
        for i in range(path_len - 1):
            idx1 = path_ptr[i]
            idx2 = path_ptr[i+1]
            x1, y1 = self.c_array[idx1].x, self.c_array[idx1].y
            x2, y2 = self.c_array[idx2].x, self.c_array[idx2].y
            line = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, dash=dash)
            self.path_lines.append(line)
            
        if path_len == self.num_elements:
            idx1 = path_ptr[path_len - 1]
            idx2 = path_ptr[0]
            x1, y1 = self.c_array[idx1].x, self.c_array[idx1].y
            x2, y2 = self.c_array[idx2].x, self.c_array[idx2].y
            line = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, dash=dash)
            self.path_lines.append(line)
            
    def _clear_stage_lines(self):
        if hasattr(self, 'active_step_btn') and self.active_step_btn:
            try:
                self.active_step_btn.destroy()
            except:
                pass
            self.active_step_btn = None
        for line in self.stage_lines:
            self.canvas.delete(line)
        self.stage_lines = []

    def _clear_card_lines(self):
        if hasattr(self, 'card_lines'):
            for line in self.card_lines:
                try:
                    self.canvas.delete(line)
                except:
                    pass
            self.card_lines = []

    def _draw_explanation_card(self, title, steps, fact, color):
        self._clear_card_lines()
        # Coordinates for left side overlay card
        x1 = 10
        y1 = 80
        x2 = 360
        y2 = self.canvas_height - 10
        
        # Draw sleek background rectangle with subtle styling
        bg = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#121212", outline=color, width=2)
        
        # Draw Title
        t = self.canvas.create_text(x1 + 15, y1 + 25, text=title, fill=color, font=("Helvetica", 11, "bold"), anchor="w", width=320)
        
        # Draw Steps
        lines = []
        for i, step in enumerate(steps):
            line = self.canvas.create_text(x1 + 15, y1 + 70 + i*50, text=step, fill="#ffffff", font=("Helvetica", 10), anchor="nw", width=320)
            lines.append(line)
            
        # Draw Fact badge rectangle on the bottom of the card
        f_bg = self.canvas.create_rectangle(x1 + 15, y2 - 90, x2 - 15, y2 - 15, fill="#1a1a1a", outline=color, width=1)
        f_text = self.canvas.create_text(x1 + 175, y2 - 52, text=fact, fill=color, font=("Helvetica", 10, "bold"), justify=tk.CENTER, width=300)
        
        self.card_lines.extend([bg, t, f_bg, f_text] + lines)

    def _draw_sa_progress_card(self, current_temp):
        x1 = 10
        y1 = 80
        x2 = 360
        y2 = self.canvas_height - 10
        
        self._clear_card_lines()
        
        color = "#FFD700"
        bg = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#121212", outline=color, width=2)
        self.card_lines.append(bg)
        
        t = self.canvas.create_text(x1 + 15, y1 + 25, text="SIMULATED ANNEALING METRIC", fill=color, font=("Helvetica", 11, "bold"), anchor="w")
        self.card_lines.append(t)
        
        rate_val = getattr(self, 'sa_cooling_rate', 0.995)
        actual_evals = tsp_lib.get_tsp_comparison_count()
        steps = [
            f"• Current Temp: {current_temp:.4f}",
            f"• Cooling Rate: α = {rate_val:.4f}",
            f"• Evaluated: {actual_evals:,} swaps",
            "• Probabilistic acceptance enabled"
        ]
        for i, step in enumerate(steps):
            line = self.canvas.create_text(x1 + 15, y1 + 55 + i*22, text=step, fill="#ffffff", font=("Helvetica", 10), anchor="nw")
            self.card_lines.append(line)
            
        gx1 = x1 + 15
        gy1 = y1 + 145
        gx2 = x2 - 15
        gy2 = y2 - 15
        
        gbg = self.canvas.create_rectangle(gx1, gy1, gx2, gy2, fill="#0c0c0c", outline="#333333", width=1)
        self.card_lines.append(gbg)
        
        lbl_t = self.canvas.create_text(gx1 + 5, gy1 + 5, text="Temp", fill="#888888", font=("Helvetica", 8), anchor="nw")
        lbl_s = self.canvas.create_text(gx2 - 5, gy2 - 5, text="Time →", fill="#888888", font=("Helvetica", 8), anchor="se")
        self.card_lines.append(lbl_t)
        self.card_lines.append(lbl_s)
        
        history = self.sa_temp_history
        if len(history) > 100:
            indices = [int(i * (len(history) - 1) / 99) for i in range(100)]
            points = [history[idx] for idx in indices]
        else:
            points = history
            
        num_pts = len(points)
        if num_pts >= 2:
            coords = []
            for idx, temp in enumerate(points):
                px = gx1 + 5 + (idx / (num_pts - 1)) * (gx2 - gx1 - 10)
                ratio = temp / self.sa_initial_temp
                if ratio > 1.0: ratio = 1.0
                if ratio < 0.0: ratio = 0.0
                py = gy2 - 5 - ratio * (gy2 - gy1 - 20)
                coords.append((px, py))
                
            for idx in range(num_pts - 1):
                lx1, ly1 = coords[idx]
                lx2, ly2 = coords[idx+1]
                gl = self.canvas.create_line(lx1, ly1, lx2, ly2, fill="#FF6F61", width=2)
                self.card_lines.append(gl)

    def _draw_clear_all(self):
        """Wipe all algorithm-drawn lines and stage overlays from the canvas."""
        for line in self.path_lines:
            self.canvas.delete(line)
        self.path_lines = []
        self._clear_stage_lines()
        self._clear_card_lines()

    def _show_distance_badge(self, label, dist, color):
        """Draw/update a persistent distance badge in the top-right corner of the canvas."""
        self._clear_distance_badge()
        x = self.canvas_width - 10
        y = 10
        comp_count = tsp_lib.get_tsp_comparison_count()
        # Background rectangle with more height for the comparison count
        bg = self.canvas.create_rectangle(
            x - 240, y, x, y + 72,
            fill="#1e1e1e", outline=color, width=2
        )
        title = self.canvas.create_text(
            x - 120, y + 14,
            text=label,
            fill=color, font=("Helvetica", 11, "bold"), anchor="center"
        )
        value = self.canvas.create_text(
            x - 120, y + 36,
            text=f"Distance: {dist:.2f}",
            fill="#ffffff", font=("Helvetica", 13, "bold"), anchor="center"
        )
        comp = self.canvas.create_text(
            x - 120, y + 56,
            text=f"Comparisons: {comp_count:,}",
            fill="#ffc66d", font=("Courier", 10, "bold"), anchor="center"
        )
        self.dist_badge = [bg, title, value, comp]

    def _clear_distance_badge(self):
        if hasattr(self, 'dist_badge') and self.dist_badge:
            for item in self.dist_badge:
                self.canvas.delete(item)
            self.dist_badge = None

    def _on_tsp_cb(self, event_type, path_ptr, path_len, current_dist):
        try:
            # event_type 3 = Done/cleanup signal from C — ALWAYS let it through,
            # even when aborted, so that _finish_run() is called and the UI unlocks.
            if event_type == 3:
                comp_count = tsp_lib.get_tsp_comparison_count()
                if self.abort_requested:
                    self._draw_clear_all()
                    self.last_path = None
                    self.info_label.config(
                        text=f"ABORTED! Evaluated {comp_count:,} comparisons.",
                        fg="#ff5252"
                    )
                else:
                    if self.current_algo != "Lower Bound":
                        self.info_label.config(
                            text=f"DONE! Final Dist: {self.best_dist:.2f} | Comparisons: {comp_count:,}",
                            fg="#a9b7c6"
                        )
                        if self.best_dist != float('inf') and path_ptr and path_len == self.num_elements:
                            self._draw_algo_path(path_ptr, path_len, color="#ffc66d", width=2)
                            self._show_distance_badge(f"Final ({self.current_algo})", self.best_dist, "#ffc66d")
                            self.last_path = [path_ptr[idx] for idx in range(path_len)]
                        
                        if self.current_algo in self.algo_result_labels:
                            self.algo_result_labels[self.current_algo].config(
                                text=f"Last run: {self.best_dist:.1f}\n({comp_count:,} comps)"
                            )
                        self._clear_stage_lines()
                        self._clear_card_lines()
                
                self._finish_run()
                return 0

            # For all other events, bail immediately if user requested abort
            if self.abort_requested:
                self._clear_stage_lines()
                return 1
                
            if event_type == 1:  # Evaluating a candidate path
                self.eval_count += 1

                # CRITICAL: Process pending UI events every 100 iterations.
                # Without this, the Tkinter event loop never runs while C is executing,
                # so button clicks (including Abort) can never be processed.
                if self.eval_count % 100 == 0:
                    self.update()
                    if self.abort_requested:
                        self._clear_stage_lines()
                        return 1

                speed = self.speed_slider.get()

                # Throttle DRAWING independently of event processing above
                if speed >= 1000:
                    # Max speed: draw only every 2000 frames
                    if self.eval_count % 2000 != 0:
                        return 0
                elif speed >= 200:
                    # Fast: draw every 50 frames
                    if self.eval_count % 50 != 0:
                        return 0

                self._draw_algo_path(path_ptr, path_len, color="#666666", width=1, dash=(2,2))
                self.info_label.config(text=f"[Evaluating] Dist: {current_dist:.2f} | Paths Checked: {self.eval_count}")
                self.update()
                self.my_sleep()
                
            elif event_type == 2:  # New best / final path
                self.best_dist = current_dist
                self._clear_stage_lines()  # wipe intermediate Christofides layers
                self._draw_algo_path(path_ptr, path_len, color="#4CAF50", width=2)
                self._show_distance_badge("Best so far", current_dist, "#4CAF50")
                self.info_label.config(text=f"[NEW BEST!] Dist: {current_dist:.2f} | Paths: {self.eval_count}")
                if path_ptr and path_len == self.num_elements:
                    self.last_path = [path_ptr[idx] for idx in range(path_len)]
                self.update()
                
                if self.speed_slider.get() < 500:
                    self._interruptible_pause(500)
                    

            elif event_type == 4:  # Christofides Stage 1: MST
                print(f"[DEBUG UI] Received MST event. path_len={path_len}")
                self._clear_stage_lines()

                # Compute degree of every node from the MST edge list
                degrees = {}
                for i in range(0, path_len, 2):
                    u = path_ptr[i]
                    v = path_ptr[i+1]
                    degrees[u] = degrees.get(u, 0) + 1
                    degrees[v] = degrees.get(v, 0) + 1
                
                num_odd = sum(1 for d in degrees.values() if d % 2 != 0)
                
                for i in range(0, path_len, 2):
                    u = path_ptr[i]
                    v = path_ptr[i+1]
                    x1, y1 = self.c_array[u].x, self.c_array[u].y
                    x2, y2 = self.c_array[v].x, self.c_array[v].y
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#03A9F4", width=2)
                    self.stage_lines.append(line)
                    
                    for node in (u, v):
                        if degrees[node] % 2 != 0:
                            x, y = self.c_array[node].x, self.c_array[node].y
                            r = 5
                            dot = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#FF5722", outline="")
                            self.stage_lines.append(dot)
                            
                self._draw_explanation_card(
                    "CHRISTOFIDES STEP 1/3: Minimum Spanning Tree (MST)",
                    [
                        f"• Connected all {self.num_elements} stations cleanly without cycles.",
                        f"• Total MST Distance: {current_dist:.2f}",
                        f"• Identified {num_odd} stations with an odd number of connections (highlighted in orange)."
                    ],
                    "MST Bound:\nWeight(MST) < Optimal TSP tour\n(since removing any edge from the\noptimal tour yields a spanning tree)",
                    "#03A9F4"
                )
                
                self.info_label.config(
                    text=f"[Christofides 1/3] MST formed (Dist: {current_dist:.2f}). {num_odd} odd stations found (orange).",
                    fg="#03A9F4"
                )
                self.update()
                
                # Pop up a gorgeous shorter button on the side, above the explanation
                if not hasattr(self, 'continue_var'):
                    self.continue_var = tk.BooleanVar(value=False)
                self.continue_var.set(False)
                
                btn = tk.Button(
                    self.canvas, 
                    text="Step 2: Eulerian Methodology ➔",
                    command=lambda: self.continue_var.set(True),
                    font=("Helvetica", 11, "bold"),
                    fg="#FF5722",
                    highlightbackground="#1e1e1e"
                )
                btn_window = self.canvas.create_window(185, 40, window=btn)
                self.stage_lines.append(btn_window)
                self.active_step_btn = btn
                
                self.canvas.wait_variable(self.continue_var)
                    
                if self.active_step_btn:
                    try:
                        self.active_step_btn.destroy()
                    except:
                        pass
                    self.active_step_btn = None
                try:
                    self.canvas.delete(btn_window)
                except:
                    pass
                if self.abort_requested:
                    self._clear_stage_lines()
                    return 1

            elif event_type == 5:  # Christofides Stage 2: MWPM
                num_pairs = path_len // 2
                print(f"[DEBUG UI] Received MWPM event. path_len={path_len}, num_pairs={num_pairs}")
                for i in range(0, path_len - 1, 2):
                    n1 = path_ptr[i]
                    n2 = path_ptr[i+1]
                    x1, y1 = self.c_array[n1].x, self.c_array[n1].y
                    x2, y2 = self.c_array[n2].x, self.c_array[n2].y
                    r = 7 if self.num_elements <= 30 else 4
                    dot  = self.canvas.create_oval(x1-r, y1-r, x1+r, y1+r, fill="#FF5722", outline="")
                    dot2 = self.canvas.create_oval(x2-r, y2-r, x2+r, y2+r, fill="#FF5722", outline="")
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#FF5722", width=2, dash=(4, 3))
                    self.stage_lines.extend([dot, dot2, line])
                    
                # Draw beautiful overlay card at the bottom of the canvas
                self._draw_explanation_card(
                    "CHRISTOFIDES STEP 2/3: Minimum Weight Perfect Matching (MWPM)",
                    [
                        f"• Paired orange stations using perfect matching ({num_pairs} pairs).",
                        f"• Total Matching Distance: {current_dist:.2f}",
                        "• Added matching edges (orange dashed lines) to MST.",
                        "• Every station now has an EVEN degree. Eulerian tour ready!"
                    ],
                    "MWPM Bound:\nWeight(MWPM) ≤ 0.5 × Optimal TSP\n(hence, MST + MWPM yields a total\ntour cost ≤ 1.5 × Optimal TSP!)",
                    "#FF5722"
                )
                
                self.info_label.config(
                    text=f"[Christofides 2/3] Odd stations matched (Dist: {current_dist:.2f}). Eulerian circuit ready.",
                    fg="#FF5722"
                )
                self.update()
                
                # Pop up a gorgeous shorter button on the side, above the explanation
                if not hasattr(self, 'continue_var'):
                    self.continue_var = tk.BooleanVar(value=False)
                self.continue_var.set(False)
                
                btn = tk.Button(
                    self.canvas, 
                    text="Step 3: Shortcut to Hamiltonian Path ➔",
                    command=lambda: self.continue_var.set(True),
                    font=("Helvetica", 11, "bold"),
                    fg="#4CAF50",
                    highlightbackground="#1e1e1e"
                )
                btn_window = self.canvas.create_window(185, 40, window=btn)
                self.stage_lines.append(btn_window)
                self.active_step_btn = btn
                
                self.canvas.wait_variable(self.continue_var)
                    
                if self.active_step_btn:
                    try:
                        self.active_step_btn.destroy()
                    except:
                        pass
                    self.active_step_btn = None
                try:
                    self.canvas.delete(btn_window)
                except:
                    pass
                if self.abort_requested:
                    self._clear_stage_lines()
                    return 1

            elif event_type == 6:  # Greedy Edge-Insertion intermediate edges
                self._clear_stage_lines()
                for i in range(0, path_len - 1, 2):
                    n1 = path_ptr[i]
                    n2 = path_ptr[i+1]
                    x1, y1 = self.c_array[n1].x, self.c_array[n1].y
                    x2, y2 = self.c_array[n2].x, self.c_array[n2].y
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#E91E63", width=2)
                    self.stage_lines.append(line)
                
                num_edges = path_len // 2
                self.info_label.config(
                    text=f"[Greedy Edge Selection] Selected {num_edges}/{self.num_elements} edges | Total Dist: {current_dist:.2f}",
                    fg="#E91E63"
                )
                self.update()
                self.my_sleep()
                if self.abort_requested:
                    self._clear_stage_lines()
                    return 1
                
            elif event_type == 7:  # Lower Bound: Evaluating 1-Tree for a vertex
                self._clear_stage_lines()
                anchor = path_ptr[0]
                
                # Draw anchor with glowing pink aura
                ax, ay = self.c_array[anchor].x, self.c_array[anchor].y
                r_halo = 12
                halo = self.canvas.create_oval(ax-r_halo, ay-r_halo, ax+r_halo, ay+r_halo, outline="#FF4081", width=2)
                self.stage_lines.append(halo)
                
                # Draw the two cheapest edges incident to the anchor in solid pink
                for i in range(0, 4, 2):
                    n1 = path_ptr[i]
                    n2 = path_ptr[i+1]
                    x1, y1 = self.c_array[n1].x, self.c_array[n1].y
                    x2, y2 = self.c_array[n2].x, self.c_array[n2].y
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#FF4081", width=2.5)
                    self.stage_lines.append(line)
                
                # Draw MST edges on remaining nodes in delicate dashed pink
                for i in range(4, path_len - 1, 2):
                    n1 = path_ptr[i]
                    n2 = path_ptr[i+1]
                    x1, y1 = self.c_array[n1].x, self.c_array[n1].y
                    x2, y2 = self.c_array[n2].x, self.c_array[n2].y
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#ff8da1", width=1.5, dash=(3, 2))
                    self.stage_lines.append(line)
                    
                # Update text details
                stn_name = self.c_array[anchor].name.decode()
                self._draw_explanation_card(
                    f"EVALUATING 1-TREE FOR {stn_name}",
                    [
                        f"1. Remove node {stn_name} temporarily.",
                        f"2. Compute MST on remaining {self.num_elements - 1} vertices.",
                        f"3. Connect {stn_name} with 2 cheapest incident edges.",
                        f"Current 1-Tree Weight: {current_dist:.2f}"
                    ],
                    "Calculating lower\nbound baseline...",
                    "#FF4081"
                )
                self.info_label.config(
                    text=f"[Lower Bound Search] Evaluating node {anchor+1}/{self.num_elements} ({stn_name}) | 1-Tree Cost: {current_dist:.2f}",
                    fg="#FF4081"
                )
                self.update()
                self.my_sleep()
                if self.abort_requested:
                    self._clear_stage_lines()
                    return 1

            elif event_type == 10:  # EVENT_2OPT_SWAP
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
                if path_len >= 3:
                    node_idx = path_ptr[0]
                    # Draw a gorgeous glowing aura around the node being relocated!
                    nx, ny = self.c_array[node_idx].x, self.c_array[node_idx].y
                    r_halo = 12
                    halo = self.canvas.create_oval(nx-r_halo, ny-r_halo, nx+r_halo, ny+r_halo, outline="#FF4081", width=3)
                    self.stage_lines.append(halo)
                    
                    # Draw predecessor and successor candidate/broken connections
                    pred = path_ptr[1]
                    succ = path_ptr[2]
                    px, py = self.c_array[pred].x, self.c_array[pred].y
                    sx, sy = self.c_array[succ].x, self.c_array[succ].y
                    l1 = self.canvas.create_line(px, py, nx, ny, fill="#FF4081", width=1.5, dash=(2, 2))
                    l2 = self.canvas.create_line(nx, ny, sx, sy, fill="#FF4081", width=1.5, dash=(2, 2))
                    self.stage_lines.append(l1)
                    self.stage_lines.append(l2)
                    
                self.info_label.config(text=f"[1-Opt Evaluating] Relocating node: {node_idx+1} | Checked: {self.eval_count}")
                self.update()
                self.my_sleep()

            elif event_type == 15:  # EVENT_SA_EVALUATING (current_dist is the temperature T)
                self.eval_count += 1
                
                # Get the default return value (just return 0, no longer need to pass cooling rate back!)
                ret_val = 0

                # Record temperature history on every callback for 100% complete graph
                self.sa_temp_history.append(current_dist)
                if self.sa_initial_temp is None:
                    self.sa_initial_temp = current_dist if current_dist > 0 else 1.0

                import time

                # CRITICAL: Process pending UI events every 200 iterations for SA to prevent lockup
                if self.eval_count % 200 == 0:
                    self.update()
                    if self.abort_requested:
                        self._clear_stage_lines()
                        return 1
                
                # Throttle GUI redrawing using time-based (FPS) logic at max speed to guarantee 0 lag
                speed = self.speed_slider.get()
                now = time.time()
                should_draw = False
                
                if speed < 1000:
                    draw_throttle = 15 if speed >= 500 else (3 if speed >= 100 else 1)
                    if self.eval_count % draw_throttle == 0:
                        should_draw = True
                else:
                    # Time-based throttle at max speed (~30 FPS)
                    if now - getattr(self, 'sa_last_draw', 0) > 0.033:
                        should_draw = True
                
                if should_draw:
                    # Render custom SA progress card and temperature graph
                    self._draw_sa_progress_card(current_dist)

                    # Render candidate edges currently being evaluated
                    self._clear_stage_lines()
                    for k in range(0, path_len - 1, 2):
                        n1, n2 = path_ptr[k], path_ptr[k+1]
                        x1, y1 = self.c_array[n1].x, self.c_array[n1].y
                        x2, y2 = self.c_array[n2].x, self.c_array[n2].y
                        line = self.canvas.create_line(x1, y1, x2, y2, fill="#555555", width=1.5, dash=(2, 2))
                        self.stage_lines.append(line)
                        
                    actual_evals = tsp_lib.get_tsp_comparison_count()
                    self.info_label.config(text=f"[SA Evaluating] Current Temp: {current_dist:.4f} | Checked: {actual_evals:,} swaps")
                    self.update()
                    
                    # CRITICAL YIELD: Yield CPU so macOS WindowServer can composite and draw the frame!
                    time.sleep(0.005) 
                    self.my_sleep()
                    self.sa_last_draw = time.time()
                    
                return ret_val

            elif event_type == 14:  # EVENT_SA_SWAP
                self.best_dist = current_dist
                self._clear_stage_lines()
                self._draw_algo_path(path_ptr, path_len, color="#2ecc71", width=2)
                self._show_distance_badge("SA Tour", current_dist, "#2ecc71")
                actual_evals = tsp_lib.get_tsp_comparison_count()
                self.info_label.config(text=f"[SA Accepted Move!] Dist: {current_dist:.2f} | Checked: {actual_evals:,} swaps")
                self.update()
                if self.speed_slider.get() < 500:
                    self._interruptible_pause(100)

            elif event_type == 8:  # Lower Bound: Final Max 1-Tree Confirmed
                self._clear_stage_lines()
                self.lbl_lb_result.config(text=f"{current_dist:.2f}")
                
                anchor = path_ptr[0]
                
                # Draw final anchor with glowing gold aura
                ax, ay = self.c_array[anchor].x, self.c_array[anchor].y
                r_halo = 12
                halo = self.canvas.create_oval(ax-r_halo, ay-r_halo, ax+r_halo, ay+r_halo, outline="#FFD700", width=3)
                self.stage_lines.append(halo)
                
                # Draw the two cheapest edges incident to the anchor in solid gold
                for i in range(0, 4, 2):
                    n1 = path_ptr[i]
                    n2 = path_ptr[i+1]
                    x1, y1 = self.c_array[n1].x, self.c_array[n1].y
                    x2, y2 = self.c_array[n2].x, self.c_array[n2].y
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#FFD700", width=3.5)
                    self.stage_lines.append(line)
                    
                # Draw final MST edges on remaining nodes in solid gold/amber
                for i in range(4, path_len - 1, 2):
                    n1 = path_ptr[i]
                    n2 = path_ptr[i+1]
                    x1, y1 = self.c_array[n1].x, self.c_array[n1].y
                    x2, y2 = self.c_array[n2].x, self.c_array[n2].y
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#FFD700", width=2)
                    self.stage_lines.append(line)
                    
                stn_name = self.c_array[anchor].name.decode()
                self._draw_explanation_card(
                    "MAX 1-TREE LOWER BOUND FOUND",
                    [
                        f"• Anchor Node: {stn_name}",
                        f"• Mathematical Best Lower Bound: {current_dist:.2f}",
                        "• Crucial: No valid TSP tour can EVER be",
                        f"  shorter than this value ({current_dist:.2f})!",
                        "• Gives us a perfect heuristic gap comparison."
                    ],
                    f"Optimal Route ≥\n{current_dist:.2f} km",
                    "#FFD700"
                )
                self.info_label.config(
                    text=f"Max 1-Tree Lower Bound locked: {current_dist:.2f} (Anchor: {stn_name})",
                    fg="#FFD700"
                )
                self.update()
                
            return 0
        except Exception as e:
            print(f"Exception in TSP callback: {e}")
            import traceback
            traceback.print_exc()
            try:
                self._clear_stage_lines()
            except:
                pass
            return 1

    def abort_process(self):
        if self.is_running:
            self.abort_requested = True
            if hasattr(self, 'continue_var'):
                self.continue_var.set(True)
            self._clear_distance_badge()
            self.info_label.config(text="ABORTING C ENGINE...", fg="#ff5252")

    def _prepare_run(self):
        if self.is_running: return False
        
        import inspect
        caller = inspect.currentframe().f_back.f_code.co_name
        if caller == "start_brute_force" and self.num_elements > 11:
            self.info_label.config(text=f"Cannot run Brute Force on {self.num_elements} nodes! It would take literal centuries.", fg="#ff5252")
            return False

        algo_map = {
            "start_nearest_neighbor": "Nearest Neighbor",
            "start_greedy": "Greedy",
            "start_christofides": "Christofides",
            "start_brute_force": "Brute Force",
            "start_lower_bound": "Lower Bound",
            "start_1opt": "1-Opt Refinement",
            "start_2opt": "2-Opt Refinement",
            "start_simulated_annealing": "Simulated Annealing"
        }
        self.current_algo = algo_map.get(caller, "Algorithm")

        # Clear canvas BEFORE setting is_running=True.
        # (reset_user_route bails early if is_running, so we clear directly here.)
        self._draw_clear_all()
        self._clear_distance_badge()
        for i in range(self.num_elements):
            self.canvas.itemconfig(f"node_{i}", fill="#ffc66d")  # reset node colors
        self.user_path = []
        self.btn_check.config(state=tk.DISABLED)

        self.is_running = True
        self.abort_requested = False
        
        self.btn_nn.config(state=tk.DISABLED)
        self.btn_greedy.config(state=tk.DISABLED)
        self.btn_christofides.config(state=tk.DISABLED)
        self.btn_brute.config(state=tk.DISABLED)
        self.btn_lower_bound.config(state=tk.DISABLED)
        self.btn_1opt.config(state=tk.DISABLED)
        self.btn_2opt.config(state=tk.DISABLED)
        self.btn_sa.config(state=tk.DISABLED)
        self.btn_regen.config(state=tk.DISABLED)
        self.btn_random_route.config(state=tk.DISABLED)
        self.nodes_spin.config(state=tk.DISABLED)
        self.eval_count = 0
        self.best_dist = float('inf')
        return True

    def _finish_run(self):
        if self.abort_requested:
            actual_evals = tsp_lib.get_tsp_comparison_count()
            self.info_label.config(text=f"ABORTED by user! Evaluated {actual_evals:,} comparisons.", fg="#ff5252")
        self.btn_nn.config(state=tk.NORMAL)
        self.btn_greedy.config(state=tk.NORMAL)
        self.btn_christofides.config(state=tk.NORMAL)
        self.btn_brute.config(state=tk.NORMAL)
        self.btn_lower_bound.config(state=tk.NORMAL)
        self.btn_1opt.config(state=tk.NORMAL)
        self.btn_2opt.config(state=tk.NORMAL)
        self.btn_sa.config(state=tk.NORMAL)
        self.btn_regen.config(state=tk.NORMAL)
        self.btn_random_route.config(state=tk.NORMAL)
        self.nodes_spin.config(state=tk.NORMAL)
        self.is_running = False

    def start_nearest_neighbor(self):
        if not self._prepare_run(): return
        self.info_label.config(text="Starting Nearest-Neighbor Algorithm...", fg="#a9b7c6")
        self.update()
        tsp_lib.tsp_nearest_neighbor(self.c_array, self.num_elements, self.c_callback)

    def start_greedy(self):
        if not self._prepare_run(): return
        self.info_label.config(text="Starting Greedy (Edge-Insertion) Algorithm...", fg="#a9b7c6")
        self.update()
        tsp_lib.tsp_greedy(self.c_array, self.num_elements, self.c_callback)

    def start_christofides(self):
        if not self._prepare_run(): return
        self.info_label.config(text="Starting Christofides Algorithm...", fg="#a9b7c6")
        self.update()
        tsp_lib.tsp_christofides(self.c_array, self.num_elements, self.c_callback)

    def start_brute_force(self):
        if not self._prepare_run(): return
        self.info_label.config(text=f"Starting Unpruned Brute Force (O(N!))...", fg="#a9b7c6")
        self.update()
        tsp_lib.tsp_brute_force(self.c_array, self.num_elements, self.c_callback)

    def start_lower_bound(self):
        if not self._prepare_run(): return
        self.info_label.config(text="Starting Max 1-Tree Lower Bound computation...", fg="#a9b7c6")
        self.update()
        tsp_lib.tsp_max_1_tree(self.c_array, self.num_elements, self.c_callback)

    def start_1opt(self):
        if not hasattr(self, 'last_path') or not self.last_path or len(self.last_path) != self.num_elements:
            self.info_label.config(text="Run Nearest-Neighbor, Greedy, or Christofides first to construct an initial tour!", fg="#ff5252")
            return
        
        # Calculate initial path distance
        init_dist = 0.0
        for idx in range(self.num_elements):
            u = self.last_path[idx]
            v = self.last_path[(idx + 1) % self.num_elements]
            dx = self.c_array[u].x - self.c_array[v].x
            dy = self.c_array[u].y - self.c_array[v].y
            init_dist += (dx*dx + dy*dy)**0.5

        if not self._prepare_run(): return
        self.best_dist = init_dist

        # Draw the initial path before starting optimization
        PathArrType = ctypes.c_int * self.num_elements
        path_arr = PathArrType(*self.last_path)
        self._draw_algo_path(path_arr, self.num_elements, color="#4CAF50", width=2)
        self._show_distance_badge("Initial Tour", init_dist, "#4CAF50")

        self.info_label.config(text="Starting 1-Opt Node Relocation Local Search...", fg="#a9b7c6")
        self.update()
        
        # Call C library
        tsp_lib.tsp_1opt(self.c_array, self.num_elements, path_arr, self.c_callback)

    def start_2opt(self):
        if not hasattr(self, 'last_path') or not self.last_path or len(self.last_path) != self.num_elements:
            self.info_label.config(text="Run Nearest-Neighbor, Greedy, or Christofides first to construct an initial tour!", fg="#ff5252")
            return
        
        # Calculate initial path distance
        init_dist = 0.0
        for idx in range(self.num_elements):
            u = self.last_path[idx]
            v = self.last_path[(idx + 1) % self.num_elements]
            dx = self.c_array[u].x - self.c_array[v].x
            dy = self.c_array[u].y - self.c_array[v].y
            init_dist += (dx*dx + dy*dy)**0.5

        if not self._prepare_run(): return
        self.best_dist = init_dist

        # Draw the initial path before starting optimization
        PathArrType = ctypes.c_int * self.num_elements
        path_arr = PathArrType(*self.last_path)
        self._draw_algo_path(path_arr, self.num_elements, color="#4CAF50", width=2)
        self._show_distance_badge("Initial Tour", init_dist, "#4CAF50")

        self.info_label.config(text="Starting 2-Opt Edge-Uncrossing Local Search...", fg="#a9b7c6")
        self.update()
        
        # Call C library
        tsp_lib.tsp_2opt(self.c_array, self.num_elements, path_arr, self.c_callback)

    def start_simulated_annealing(self):
        if not hasattr(self, 'last_path') or not self.last_path or len(self.last_path) != self.num_elements:
            self.info_label.config(text="Run Nearest-Neighbor, Greedy, or Christofides first to construct an initial tour!", fg="#ff5252")
            return
        
        # Calculate initial path distance
        init_dist = 0.0
        for idx in range(self.num_elements):
            u = self.last_path[idx]
            v = self.last_path[(idx + 1) % self.num_elements]
            dx = self.c_array[u].x - self.c_array[v].x
            dy = self.c_array[u].y - self.c_array[v].y
            init_dist += (dx*dx + dy*dy)**0.5

        import tkinter.simpledialog as simpledialog
        rate = simpledialog.askfloat(
            "Simulated Annealing Config",
            "Enter Cooling Rate (α) between 0.800 and 0.999:\n(e.g. 0.995 is slow/precise, 0.900 is fast)",
            initialvalue=0.925, minvalue=0.800, maxvalue=0.999, parent=self.winfo_toplevel()
        )
        if rate is None:
            return
            
        init_ratio = simpledialog.askfloat(
            "Simulated Annealing Config",
            "Enter Initial Temp Ratio (0.001 to 0.050):\n(Higher = scrambles the route more; Lower = gentle refinement)",
            initialvalue=0.010, minvalue=0.001, maxvalue=0.050, parent=self.winfo_toplevel()
        )
        if init_ratio is None:
            return

        self.sa_cooling_rate = rate
        self.sa_init_ratio = init_ratio

        if not self._prepare_run(): return
        self.best_dist = init_dist

        # Draw the initial path before starting optimization
        PathArrType = ctypes.c_int * self.num_elements
        path_arr = PathArrType(*self.last_path)
        self._draw_algo_path(path_arr, self.num_elements, color="#4CAF50", width=2)
        self._show_distance_badge("Initial Tour", init_dist, "#4CAF50")

        self.sa_temp_history = []
        self.sa_initial_temp = None
        self.sa_last_draw = 0

        self.info_label.config(text="Starting Simulated Annealing Metaheuristic...", fg="#a9b7c6")
        self.update()
        
        # Call C library
        tsp_lib.tsp_simulated_annealing(self.c_array, self.num_elements, path_arr, self.c_callback, self.sa_init_ratio, self.sa_cooling_rate)


class SortVisualizer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#2b2b2b")
        
        self.canvas = tk.Canvas(self, width=1350, height=450, bg="#3c3f41", highlightthickness=0)
        self.canvas.pack(pady=20)
        
        self.info_label = tk.Label(self, text="Ready to sort", font=("Helvetica", 16), bg="#2b2b2b", fg="#a9b7c6")
        self.info_label.pack()
        
        self.btn_frame = tk.Frame(self, bg="#2b2b2b")
        self.btn_frame.pack(pady=20)
        
        self.btn_bubble = tk.Button(self.btn_frame, text="Visualize Bubble Sort", command=self.start_bubble_sort, font=("Helvetica", 12))
        self.btn_bubble.pack(side=tk.LEFT, padx=10)
        
        self.btn_quick = tk.Button(self.btn_frame, text="Visualize Quick Sort", command=self.start_quick_sort, font=("Helvetica", 12))
        self.btn_quick.pack(side=tk.LEFT, padx=10)
        
        self.btn_abort = tk.Button(self.btn_frame, text="ABORT", command=self.abort_process, font=("Helvetica", 12, "bold"), fg="red")
        self.btn_abort.pack(side=tk.LEFT, padx=20)
        
        self.speed_slider = tk.Scale(self.btn_frame, from_=1, to=1000, orient=tk.HORIZONTAL, label="Actions/Sec (Speed)", length=200, bg="#2b2b2b", fg="white", highlightthickness=0)
        self.speed_slider.set(10)
        self.speed_slider.pack(side=tk.LEFT, padx=20)
        
        self.c_array = None
        self.num_elements = 7
        self.rects = []
        self.texts = []
        self.pointers = {}
        
        self.is_running = False
        self.abort_requested = False
        
        self.c_callback = SORT_CALLBACK_TYPE(self._on_c_callback)
        self.reset_data()

    def my_sleep(self):
        actions_per_sec = self.speed_slider.get()
        if actions_per_sec >= 1000:
            self.update()
            return
        
        delay_ms = int(1000 / actions_per_sec)
        if delay_ms <= 0: delay_ms = 1
        var = tk.IntVar()
        self.after(delay_ms, var.set, 1)
        self.wait_variable(var)

    def reset_data(self):
        py_data = [
            (b"Thomas Bus", 70),
            (b"Fanta Bus", 20),
            (b"Omri Bus", 80),
            (b"Annoyed Driver Bus", 30),
            (b"Sleepy Bus", 90),
            (b"Party Bus", 10),
            (b"Late Bus", 50)
        ]
        
        ArrayType = BusLine * self.num_elements
        self.c_array = ArrayType()
        for i, (name, dist) in enumerate(py_data):
            self.c_array[i].name = name
            self.c_array[i].distance = dist
            self.c_array[i].duration = 0
            self.c_array[i].frequency = 0
            
        self.draw_array()
        
    def draw_array(self):
        self.canvas.delete("all")
        self.rects = []
        self.texts = []
        self.pointers = {}
        
        start_x = 50
        y = 120
        box_width = 160
        box_height = 100
        spacing = 20
        
        for i in range(self.num_elements):
            item = self.c_array[i]
            x1 = start_x + i * (box_width + spacing)
            y1 = y
            x2 = x1 + box_width
            y2 = y + box_height
            
            addr = hex(0x1000 + i*0x40)
            self.canvas.create_text((x1+x2)/2, y1-20, text=addr, font=("Courier", 12, "bold"), fill="#ffc66d")
            
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#546e7a", outline="#a9b7c6", width=2)
            
            name_str = item.name.decode('utf-8', errors='ignore')
            text = self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=f"\"{name_str}\"\nDist: {item.distance}", font=("Helvetica", 12, "bold"), fill="#ffffff", justify=tk.CENTER, width=box_width-10)
            
            self.rects.append(rect)
            self.texts.append(text)
            
    def update_pointers(self, ptr_dict):
        for p in self.pointers.values():
            self.canvas.delete(p)
        self.pointers = {}
        
        start_x = 50
        box_width = 160
        spacing = 20
        y_pos = 280
        
        from collections import defaultdict
        grouped = defaultdict(list)
        for name, idx in ptr_dict.items():
            if idx is not None and 0 <= idx < self.num_elements:
                addr = hex(0x1000 + idx*0x40)
                grouped[idx].append(f"{name}\n({addr})")
                
        for idx, names in grouped.items():
            x = start_x + idx * (box_width + spacing) + box_width/2
            lbl = "⬆\n" + "\n".join(names)
            t = self.canvas.create_text(x, y_pos, text=lbl, font=("Courier", 12, "bold"), fill="#ff6b6b", justify=tk.CENTER)
            self.pointers[f"group_{idx}"] = t
            
        self.update()

    def highlight(self, indices, color="#81c784"):
        for i in indices:
            if 0 <= i < self.num_elements:
                self.canvas.itemconfig(self.rects[i], fill=color)
        self.update()

    def unhighlight(self):
        for r in self.rects:
            self.canvas.itemconfig(r, fill="#546e7a")
        self.update()

    def _on_c_callback(self, event_type, p1, p2, p3, p4):
        if self.abort_requested:
            return 1
            
        self.draw_array()
        
        if event_type == 1:
            ptrs = {}
            if p1 >= 0: ptrs["cur_p"] = p1
            if p2 >= 0: ptrs["next_p/low"] = p2
            if p3 >= 0: ptrs["pivot"] = p3
            
            self.update_pointers(ptrs)
            self.highlight([p1, p2] if p3 < 0 else [p1, p3])
            
            name1 = self.c_array[p1].name.decode('utf-8', errors='ignore')
            if p2 >= 0 and p3 < 0: # Bubble
                name2 = self.c_array[p2].name.decode('utf-8', errors='ignore')
                self.info_label.config(text=f"[Native C Engine] Compare ( \"{name1}\" > \"{name2}\" )?")
            elif p3 >= 0: # Quick Sort
                name2 = self.c_array[p3].name.decode('utf-8', errors='ignore')
                dist1 = self.c_array[p1].distance
                dist2 = self.c_array[p3].distance
                self.info_label.config(text=f"[Native C Engine] Compare {name1}({dist1}) < Pivot {name2}({dist2})?")
                
            self.my_sleep()
            self.unhighlight()
            
        elif event_type == 2:
            ptrs = {}
            if p1 >= 0: ptrs["swap1"] = p1
            if p2 >= 0: ptrs["swap2"] = p2
            if p3 >= 0: ptrs["pivot"] = p3
            
            self.update_pointers(ptrs)
            
            name1 = self.c_array[p1].name.decode('utf-8', errors='ignore')
            name2 = self.c_array[p2].name.decode('utf-8', errors='ignore')
            self.info_label.config(text=f"[Native C Engine] YES! Swapping [ {name1} ] and [ {name2} ]")
            self.highlight([p1, p2], "#ffb74d")
            
            self.my_sleep()
            self.unhighlight()
            
        elif event_type == 3:
            self.update_pointers({})
            self.info_label.config(text="Native C Sort Complete! Memory is fully sorted.")
            self._finish_run()
            
        return 0

    def abort_process(self):
        if self.is_running:
            self.abort_requested = True
            if hasattr(self, 'continue_var'):
                self.continue_var.set(True)
            self.info_label.config(text="ABORTING C ENGINE...")

    def _prepare_run(self):
        if self.is_running: return False
        self.is_running = True
        self.abort_requested = False
        self.reset_data()
        self.btn_bubble.config(state=tk.DISABLED)
        self.btn_quick.config(state=tk.DISABLED)
        return True
        
    def _finish_run(self):
        if self.abort_requested:
            self.info_label.config(text="ABORTED by user!")
        self.btn_bubble.config(state=tk.NORMAL)
        self.btn_quick.config(state=tk.NORMAL)
        self.is_running = False

    def start_bubble_sort(self):
        if not self._prepare_run(): return
        start_ptr = ctypes.pointer(self.c_array[0])
        end_ptr = ctypes.pointer(self.c_array[self.num_elements - 1])
        viz_lib.visualize_bubble_sort_c(start_ptr, end_ptr, self.c_callback)
        self._finish_run()

    def start_quick_sort(self):
        if not self._prepare_run(): return
        start_ptr = ctypes.pointer(self.c_array[0])
        end_ptr = ctypes.pointer(self.c_array[self.num_elements - 1])
        DISTANCE = 0
        viz_lib.visualize_quick_sort_c(start_ptr, end_ptr, DISTANCE, self.c_callback)
        self._finish_run()


class IsraelRoadTSPVisualizer(tk.Frame):
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
        self.edit_mode = False
        self.connect_node_start = None
        
        # Load the background map image with 2x subsampling
        try:
            self.bg_photo = tk.PhotoImage(file=os.path.join(lib_dir, "ramat_efal_map.png")).subsample(2, 2)
        except Exception as e:
            print(f"Error loading map background: {e}")
            self.bg_photo = None

        import json
        config_path = os.path.join(lib_dir, "ramat_efal_config.json")
        self.nodes = {}
        self.node_names = {}
        self.graph = {}
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.nodes = {int(k): tuple(v) for k, v in data.get("nodes", {}).items()}
                self.node_names = {int(k): v for k, v in data.get("node_names", {}).items()}
                edges = data.get("edges", [])
                
                max_node = max(list(self.nodes.keys()) + [0])
                self.graph = {i: [] for i in range(max_node + 1)}
                for i in self.nodes:
                    if i not in self.graph:
                        self.graph[i] = []
                for u, v in edges:
                    p1 = self.nodes.get(u)
                    p2 = self.nodes.get(v)
                    if p1 and p2:
                        w = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
                        self.graph[u].append((v, w))
                        self.graph[v].append((u, w))
            except Exception as e:
                print(f"Error loading config: {e}")

        self._build_ui()
        self._draw_base_map()

    def _build_ui(self):
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

        # --- TAB 1: TSP ROUTING (TWO-COLUMN COMPACT LAYOUT) ---
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
        
        tk.Button(btn_frame, text="Entry", command=lambda: self._add_preset(0), font=("Helvetica", 9), width=10).grid(row=0, column=0, padx=1, pady=1)
        tk.Button(btn_frame, text="Samoha", command=lambda: self._add_preset(7), font=("Helvetica", 9), width=10).grid(row=0, column=1, padx=1, pady=1)
        tk.Button(btn_frame, text="Kelman", command=lambda: self._add_preset(10), font=("Helvetica", 9), width=10).grid(row=0, column=2, padx=1, pady=1)
        
        tk.Button(btn_frame, text="Carrefour", command=lambda: self._add_preset(27), font=("Helvetica", 9), width=10).grid(row=1, column=0, padx=1, pady=1)
        tk.Button(btn_frame, text="Harpaz", command=lambda: self._add_preset(52), font=("Helvetica", 9), width=10).grid(row=1, column=1, padx=1, pady=1)
        tk.Button(btn_frame, text="My house", command=lambda: self._add_preset(34), font=("Helvetica", 9), width=10).grid(row=1, column=2, padx=1, pady=1)
        
        tk.Button(btn_frame, text="Berlo", command=lambda: self._add_preset(21), font=("Helvetica", 9), width=10).grid(row=2, column=0, padx=1, pady=1)
        tk.Button(btn_frame, text="Shula", command=lambda: self._add_preset(58), font=("Helvetica", 9), width=10).grid(row=2, column=1, padx=1, pady=1)
        tk.Button(btn_frame, text="MeatBar", command=lambda: self._add_preset(4), font=("Helvetica", 9), width=10).grid(row=2, column=2, padx=1, pady=1)
        
        tk.Button(btn_frame, text="Ohad", command=lambda: self._add_preset(57), font=("Helvetica", 9), width=10).grid(row=3, column=0, padx=1, pady=1)
        tk.Button(btn_frame, text="Zofim", command=lambda: self._add_preset(48), font=("Helvetica", 9), width=10).grid(row=3, column=1, padx=1, pady=1)
        tk.Button(btn_frame, text="Laser", command=lambda: self._add_preset(44), font=("Helvetica", 9), width=10).grid(row=3, column=2, padx=1, pady=1)
        
        tk.Button(btn_frame, text="Katz", command=lambda: self._add_preset(47), font=("Helvetica", 9), width=10).grid(row=4, column=0, padx=1, pady=1)
        tk.Button(btn_frame, text="Bialik", command=lambda: self._add_preset(8), font=("Helvetica", 9), width=10).grid(row=4, column=1, padx=1, pady=1)
        tk.Button(btn_frame, text="Helmaan", command=lambda: self._add_preset(55), font=("Helvetica", 9), width=10).grid(row=4, column=2, padx=1, pady=1)
        
        tk.Button(btn_frame, text="Leyhman", command=lambda: self._add_preset(25), font=("Helvetica", 9), width=10).grid(row=5, column=0, padx=1, pady=1)
        tk.Button(btn_frame, text="Pincher", command=lambda: self._add_preset(35), font=("Helvetica", 9), width=10).grid(row=5, column=1, padx=1, pady=1)
        
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
        self.tour_text.pack(fill=tk.BOTH, expand=True)

        # --- TAB 2: GRAPH EDITOR ---
        ef = tk.LabelFrame(tab_editor, text="🗺️ Interactive Alignment Tools", font=("Helvetica", 11, "bold"),
                           bg="#1e1e2e", fg="#54a0ff", padx=8, pady=4)
        ef.pack(fill=tk.BOTH, expand=True, pady=(4, 8))
        
        self.btn_edit_mode = tk.Button(ef, text="Edit Mode: Pin Houses", command=self._toggle_edit_mode,
                                       font=("Helvetica", 11, "bold"), width=32, bg="#54a0ff", pady=8)
        self.btn_edit_mode.pack(pady=(10, 20))
        
        help_text = "Instructions for Graph Editor:\n\n1. Toggle Edit Mode on.\n2. Drag yellow dots to position them on roads.\n3. Double-click empty space to Add Node.\n4. Right-click a dot to Delete Node.\n5. Shift + Click dot A, then Shift + Click dot B to connect or disconnect them.\n6. Click Save below to permanently update code!"
        tk.Label(ef, text=help_text, font=("Helvetica", 10), bg="#1e1e2e", fg="#a9b7c6",
                 justify=tk.LEFT, wraplength=340).pack(fill=tk.X, pady=10, padx=10)
                 
        tk.Button(ef, text="🗑️ Clear Entire Graph (Build from Scratch)", command=self._clear_entire_graph,
                  font=("Helvetica", 11, "bold"), width=32, bg="#e74c3c", fg="white", pady=8).pack(pady=(10, 5))
                  
        tk.Button(ef, text="💾 Save Graph Coordinates Permanently", command=self._save_graph_to_file,
                  font=("Helvetica", 11, "bold"), width=32, bg="#2ecc71", fg="black", pady=8).pack(pady=(20, 10))

    def _on_canvas_click(self, event):
        if self.is_running or getattr(self, 'edit_mode', False): return
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
            self._clear_metrics()
            self._draw_base_map()
            self.info_lbl.config(text=f"Pinned location: {self.node_names[best_node]}!")
        else:
            self.info_lbl.config(text="Please click closer to a visible street or junction!")

    def _add_preset(self, node_id):
        if self.is_running: return
        if node_id not in self.nodes:
            self.info_lbl.config(text="Preset location not available in the current graph.")
            return
        if node_id in self.pinned_nodes:
            self.info_lbl.config(text="Location already pinned!")
            return
        self.pinned_nodes.append(node_id)
        self._clear_metrics()
        self._draw_base_map()
        self.info_lbl.config(text=f"Added Preset: {self.node_names.get(node_id, f'Node {node_id}')}!")

    def _clear_entire_graph(self):
        import tkinter.messagebox as messagebox
        if messagebox.askyesno("Clear Graph", "Are you sure you want to delete ALL nodes and edges to build from scratch?"):
            self.nodes = {}
            self.node_names = {}
            self.graph = {}
            self.pinned_nodes = []
            self.current_tour = None
            self._clear_metrics()
            self._draw_base_map()
            self.info_lbl.config(text="Graph completely cleared. Toggle Edit Mode to add nodes.")

    def _clear_metrics(self):
        self.lbl_nn.config(text="")
        self.lbl_gr.config(text="")
        self.lbl_2opt.config(text="")
        self.lbl_primary.config(text="—")
        self.lbl_secondary.config(text="")
        self.tour_text.config(state=tk.NORMAL)
        self.tour_text.delete("1.0", tk.END)
        self.tour_text.config(state=tk.DISABLED)

    def _clear_pins(self):
        if self.is_running: return
        self.pinned_nodes = []
        self.current_tour = None
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        self._clear_stage_lines()
        self._clear_path_lines()
        self._clear_metrics()
        self._draw_base_map()
        self.info_lbl.config(text="All pins cleared. Click the map to add homes!")

    def get_shortest_path(self, start, end):
        if start == end:
            return [start], 0.0
        dist = {i: float('inf') for i in self.nodes.keys()}
        prev = {i: None for i in self.nodes.keys()}
        dist[start] = 0.0
        Q = list(self.nodes.keys())
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
                    self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#54a0ff", width=1.5, dash=(2, 2))

        if getattr(self, "edit_mode", False):
            for node_id, pos in self.nodes.items():
                color = "#f1c40f"
                if getattr(self, "connect_node_start", None) == node_id:
                    color = "#2ecc71"
                self.canvas.create_oval(pos[0]-4, pos[1]-4, pos[0]+4, pos[1]+4,
                                        fill=color, outline="#ffffff", tags="edit_dot")
                self.canvas.create_text(pos[0], pos[1]-10, text=str(node_id), fill=color, tags="edit_lbl")
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
            line = self.canvas.create_line(*coords, fill=color, width=3.5, smooth=False, tags="tour_line")
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
            self.tour_text.insert(tk.END, f"{i+1:2}. {self.node_names[nid]}\n")
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
                line = self.canvas.create_line(*coords, fill="#4CAF50", width=3, smooth=False)
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
        self.edit_mode = False
        self.connect_node_start = None

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
                line = self.canvas.create_line(*coords, fill="#E91E63", width=3, smooth=False)
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
        self.edit_mode = False
        self.connect_node_start = None

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
        self.is_running = False
    def _toggle_edit_mode(self):
        self.edit_mode = not getattr(self, "edit_mode", False)
        if self.edit_mode:
            self.btn_edit_mode.config(text="Edit Mode: Adjust Graph Dots", fg="black", bg="#f1c40f")
            self.info_lbl.config(text="DRAG dots. DOUBLE-CLICK empty space to add. RIGHT-CLICK to delete. SHIFT-CLICK to connect.")
        else:
            self.btn_edit_mode.config(text="Edit Mode: Pin Houses", fg="black", bg="#54a0ff")
            self.connect_node_start = None
            self.info_lbl.config(text="Click on the map to place pins representing your friends' houses!")
        self._draw_base_map()

    def _get_node_at(self, x, y, radius=15):
        best_node = None
        best_dist = float('inf')
        for node_id, pos in self.nodes.items():
            d = ((pos[0]-x)**2 + (pos[1]-y)**2)**0.5
            if d < best_dist and d < radius:
                best_dist = d
                best_node = node_id
        return best_node

    def _on_canvas_drag(self, event):
        if not getattr(self, "edit_mode", False) or self.is_running: return
        x = max(0, min(self.MAP_W, event.x))
        y = max(0, min(self.MAP_H, event.y))
        if not hasattr(self, "drag_node"):
            self.drag_node = self._get_node_at(x, y)
        if getattr(self, "drag_node", None) is not None:
            self.nodes[self.drag_node] = (x, y)
            self._draw_base_map()

    def _on_canvas_release(self, event):
        if hasattr(self, "drag_node"):
            delattr(self, "drag_node")
            self._rebuild_graph_weights()

    def _rebuild_graph_weights(self):
        for u in self.graph:
            new_edges = []
            for v, _ in self.graph[u]:
                p1 = self.nodes[u]
                p2 = self.nodes[v]
                w = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
                new_edges.append((v, w))
            self.graph[u] = new_edges

    def _on_canvas_double_click(self, event):
        if not getattr(self, "edit_mode", False) or self.is_running: return
        new_id = max(self.nodes.keys()) + 1 if self.nodes else 0
        self.nodes[new_id] = (event.x, event.y)
        self.node_names[new_id] = f"New Node {new_id}"
        self.graph[new_id] = []
        self._draw_base_map()

    def _on_canvas_right_click(self, event):
        if not getattr(self, "edit_mode", False) or self.is_running: return
        node = self._get_node_at(event.x, event.y)
        if node is not None:
            del self.nodes[node]
            if node in self.node_names: del self.node_names[node]
            if node in self.pinned_nodes: self.pinned_nodes.remove(node)
            del self.graph[node]
            for u in self.graph:
                self.graph[u] = [(v, w) for v, w in self.graph[u] if v != node]
            self._draw_base_map()

    def _on_canvas_shift_click(self, event):
        if not getattr(self, "edit_mode", False) or self.is_running: return
        node = self._get_node_at(event.x, event.y)
        if node is None: return
        if getattr(self, "connect_node_start", None) is None:
            self.connect_node_start = node
            self._draw_base_map()
        else:
            u = self.connect_node_start
            v = node
            if u != v:
                has_edge = any(edge_v == v for edge_v, _ in self.graph[u])
                if has_edge:
                    self.graph[u] = [(n, w) for n, w in self.graph[u] if n != v]
                    self.graph[v] = [(n, w) for n, w in self.graph[v] if n != u]
                else:
                    p1 = self.nodes[u]
                    p2 = self.nodes[v]
                    w = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
                    self.graph[u].append((v, w))
                    self.graph[v].append((u, w))
            self.connect_node_start = None
            self._draw_base_map()

    def _save_graph_to_file(self):
        import os, json
        lib_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(lib_dir, "ramat_efal_config.json")
        
        edges = set()
        for u in self.graph:
            for v, _ in self.graph[u]:
                if u < v: edges.add((u, v))
                
        data = {
            "nodes": {str(k): list(v) for k, v in self.nodes.items()},
            "node_names": {str(k): v for k, v in self.node_names.items()},
            "edges": list(edges)
        }
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            self.info_lbl.config(text="Graph coordinates permanently saved to ramat_efal_config.json!")
        except Exception as e:
            self.info_lbl.config(text=f"Error saving config: {e}")

class MainApp(tk.Tk):
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

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
