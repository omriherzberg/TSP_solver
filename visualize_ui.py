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
        
        # --- Algorithm Buttons with result labels ---
        self.algo_frame = tk.Frame(self, bg="#2b2b2b")
        self.algo_frame.pack(pady=5)

        # Nearest Neighbor column
        nn_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        nn_col.pack(side=tk.LEFT, padx=5)
        self.btn_nn = tk.Button(nn_col, text="1. Nearest-Neighbor", command=self.start_nearest_neighbor, font=("Helvetica", 11), width=16)
        self.btn_nn.pack()
        self.lbl_nn_comp = tk.Label(nn_col, text="O(N²)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_nn_comp.pack()
        self.lbl_nn_result = tk.Label(nn_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#4CAF50")
        self.lbl_nn_result.pack()

        # Greedy column
        greedy_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        greedy_col.pack(side=tk.LEFT, padx=5)
        self.btn_greedy = tk.Button(greedy_col, text="2. Greedy (Edge)", command=self.start_greedy, font=("Helvetica", 11), width=16)
        self.btn_greedy.pack()
        self.lbl_greedy_comp = tk.Label(greedy_col, text="O(N² log N)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_greedy_comp.pack()
        self.lbl_greedy_result = tk.Label(greedy_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#E91E63")
        self.lbl_greedy_result.pack()

        # Christofides column
        ch_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        ch_col.pack(side=tk.LEFT, padx=5)
        self.btn_christofides = tk.Button(ch_col, text="3. Christofides", command=self.start_christofides, font=("Helvetica", 11), width=16)
        self.btn_christofides.pack()
        self.lbl_ch_comp = tk.Label(ch_col, text="O(N³)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_ch_comp.pack()
        self.lbl_ch_result = tk.Label(ch_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#03A9F4")
        self.lbl_ch_result.pack()

        # Brute Force column
        bf_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        bf_col.pack(side=tk.LEFT, padx=5)
        self.btn_brute = tk.Button(bf_col, text="4. Brute-Force", command=self.start_brute_force, font=("Helvetica", 11), width=16)
        self.btn_brute.pack()
        self.lbl_bf_comp = tk.Label(bf_col, text="O(N!)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_bf_comp.pack()
        self.lbl_bf_result = tk.Label(bf_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#ffc66d")
        self.lbl_bf_result.pack()

        # Lower Bound column
        lb_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        lb_col.pack(side=tk.LEFT, padx=5)
        self.btn_lower_bound = tk.Button(lb_col, text="5. Lower Bound", command=self.start_lower_bound, font=("Helvetica", 11), width=16)
        self.btn_lower_bound.pack()
        self.lbl_lb_comp = tk.Label(lb_col, text="O(N³)", font=("Helvetica", 9, "italic"), bg="#2b2b2b", fg="#888888")
        self.lbl_lb_comp.pack()
        self.lbl_lb_result = tk.Label(lb_col, text="", font=("Courier", 10), bg="#2b2b2b", fg="#FFD700")
        self.lbl_lb_result.pack()

        # Abort + Speed
        ctrl_col = tk.Frame(self.algo_frame, bg="#2b2b2b")
        ctrl_col.pack(side=tk.LEFT, padx=15)
        self.btn_abort = tk.Button(ctrl_col, text="ABORT", command=self.abort_process, font=("Helvetica", 12, "bold"), fg="red")
        self.btn_abort.pack()
        self.speed_slider = tk.Scale(ctrl_col, from_=1, to=1000, orient=tk.HORIZONTAL, label="Actions/Sec", length=140, bg="#2b2b2b", fg="white", highlightthickness=0)
        self.speed_slider.set(10)
        self.speed_slider.pack()
        
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
        }
        
        self.user_path = []
        self.path_lines = []
        self.stage_lines = []
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
        self.user_path = []
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

    def _draw_explanation_card(self, title, steps, fact, color):
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
        
        self.stage_lines.extend([bg, t, f_bg, f_text] + lines)

    def _draw_clear_all(self):
        """Wipe all algorithm-drawn lines and stage overlays from the canvas."""
        for line in self.path_lines:
            self.canvas.delete(line)
        self.path_lines = []
        self._clear_stage_lines()

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
                    self.info_label.config(
                        text=f"ABORTED! Evaluated {self.eval_count} paths | {comp_count:,} comparisons.",
                        fg="#ff5252"
                    )
                else:
                    self.info_label.config(
                        text=f"DONE! Final Dist: {self.best_dist:.2f} | Comparisons: {comp_count:,}",
                        fg="#a9b7c6"
                    )
                    if self.best_dist != float('inf') and path_ptr and path_len == self.num_elements:
                        self._draw_algo_path(path_ptr, path_len, color="#ffc66d", width=2)
                        self._show_distance_badge(f"Final ({self.current_algo})", self.best_dist, "#ffc66d")
                    # Update the per-algo button label
                    if self.current_algo in self.algo_result_labels:
                        self.algo_result_labels[self.current_algo].config(
                            text=f"Last run: {self.best_dist:.1f}\n({comp_count:,} comps)"
                        )
                self._clear_stage_lines()
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
                self.update()
                
                if self.speed_slider.get() < 500:
                    self._interruptible_pause(500)
                    

            elif event_type == 4:  # Christofides Stage 1: MST
                print(f"[DEBUG UI] Received MST event. path_len={path_len}")
                self._clear_stage_lines()

                # Compute degree of every node from the MST edge list
                degrees = {}
                edges = []
                for i in range(0, path_len - 1, 2):
                    n1 = path_ptr[i]
                    n2 = path_ptr[i+1]
                    edges.append((n1, n2))
                    degrees[n1] = degrees.get(n1, 0) + 1
                    degrees[n2] = degrees.get(n2, 0) + 1

                # Draw MST edges in blue
                for n1, n2 in edges:
                    x1, y1 = self.c_array[n1].x, self.c_array[n1].y
                    x2, y2 = self.c_array[n2].x, self.c_array[n2].y
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#03A9F4", width=2)
                    self.stage_lines.append(line)

                # Annotate each node with its MST degree (small number badge)
                if self.num_elements <= 80:  # only annotate when not too dense
                    for i in range(self.num_elements):
                        deg = degrees.get(i, 0)
                        x, y = self.c_array[i].x, self.c_array[i].y
                        color = "#FF5722" if deg % 2 != 0 else "#a9b7c6"  # orange=odd, grey=even
                        t = self.canvas.create_text(
                            x + 12, y + 12, text=str(deg),
                            fill=color, font=("Helvetica", 9, "bold")
                        )
                        self.stage_lines.append(t)

                num_odd = sum(1 for d in degrees.values() if d % 2 != 0)
                self._draw_explanation_card(
                    "CHRISTOFIDES STEP 1/3: Minimum Spanning Tree (MST)",
                    [
                        f"• Connected all {self.num_elements} stations using Prim's algorithm.",
                        f"• Total MST Distance: {current_dist:.2f}",
                        f"• Found {num_odd} stations with ODD degrees (highlighted in orange)."
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
                self.continue_clicked = False
                btn = tk.Button(
                    self.canvas, 
                    text="Step 2: Eulerian Methodology ➔",
                    command=lambda: setattr(self, 'continue_clicked', True),
                    font=("Helvetica", 11, "bold"),
                    fg="#FF5722",
                    highlightbackground="#1e1e1e"
                )
                btn_window = self.canvas.create_window(185, 40, window=btn)
                self.stage_lines.append(btn_window)
                self.active_step_btn = btn
                
                import time
                while not getattr(self, 'continue_clicked', False) and not self.abort_requested:
                    self.update()
                    time.sleep(0.02)
                    
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
                    print(f"[DEBUG UI] MWPM Edge {i//2}: {n1} ({self.c_array[n1].name.decode()}) - {n2} ({self.c_array[n2].name.decode()})")
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
                self.continue_clicked = False
                btn = tk.Button(
                    self.canvas, 
                    text="Step 3: Shortcut to Hamiltonian Path ➔",
                    command=lambda: setattr(self, 'continue_clicked', True),
                    font=("Helvetica", 11, "bold"),
                    fg="#4CAF50",
                    highlightbackground="#1e1e1e"
                )
                btn_window = self.canvas.create_window(185, 40, window=btn)
                self.stage_lines.append(btn_window)
                self.active_step_btn = btn
                
                import time
                while not getattr(self, 'continue_clicked', False) and not self.abort_requested:
                    self.update()
                    time.sleep(0.02)
                    
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
            "start_lower_bound": "Lower Bound"
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
        self.btn_regen.config(state=tk.DISABLED)
        self.nodes_spin.config(state=tk.DISABLED)
        self.eval_count = 0
        self.best_dist = float('inf')
        return True

    def _finish_run(self):
        if self.abort_requested:
            self.info_label.config(text=f"ABORTED by user! Evaluated {self.eval_count} paths.", fg="#ff5252")
        self.btn_nn.config(state=tk.NORMAL)
        self.btn_greedy.config(state=tk.NORMAL)
        self.btn_christofides.config(state=tk.NORMAL)
        self.btn_brute.config(state=tk.NORMAL)
        self.btn_lower_bound.config(state=tk.NORMAL)
        self.btn_regen.config(state=tk.NORMAL)
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
        self.sort_tab = SortVisualizer(self.notebook)
        
        self.notebook.add(self.tsp_tab, text="Mode 1: Traveling Salesperson Visualizer")
        self.notebook.add(self.sort_tab, text="Mode 2: Array Sorting Visualizer")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
