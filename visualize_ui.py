import ctypes
import tkinter as tk
import os

# 1. Map the C struct identically to your original code
class BusLine(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * 21),
        ("distance", ctypes.c_int),
        ("duration", ctypes.c_int),
        ("frequency", ctypes.c_int)
    ]

# 2. Define the Python callback function type
# It takes: event_type(1=Compare, 2=Swap, 3=Done), and 4 pointer indices
CALLBACK_TYPE = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)

# 3. Load the new shared library
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libvisualize.dylib')
viz_lib = ctypes.CDLL(lib_path)

viz_lib.visualize_bubble_sort_c.argtypes = [ctypes.POINTER(BusLine), ctypes.POINTER(BusLine), CALLBACK_TYPE]
viz_lib.visualize_bubble_sort_c.restype = None

viz_lib.visualize_quick_sort_c.argtypes = [ctypes.POINTER(BusLine), ctypes.POINTER(BusLine), ctypes.c_int, CALLBACK_TYPE]
viz_lib.visualize_quick_sort_c.restype = None

class SortVisualizer:
    def __init__(self, master):
        self.master = master
        self.master.title("C-Integrated Memory Visualization UI")
        self.master.geometry("1400x700")
        self.master.configure(bg="#2b2b2b")
        
        self.title = tk.Label(master, text="C Pointer Memory Visualizer (Native C Integrated!)", font=("Helvetica", 24, "bold"), bg="#2b2b2b", fg="#ffffff")
        self.title.pack(pady=10)
        
        self.canvas = tk.Canvas(master, width=1350, height=450, bg="#3c3f41", highlightthickness=0)
        self.canvas.pack(pady=20)
        
        self.info_label = tk.Label(master, text="Ready to sort", font=("Helvetica", 16), bg="#2b2b2b", fg="#a9b7c6")
        self.info_label.pack()
        
        self.btn_frame = tk.Frame(master, bg="#2b2b2b")
        self.btn_frame.pack(pady=20)
        
        self.btn_bubble = tk.Button(self.btn_frame, text="Visualize Bubble Sort (by Name)", command=self.start_bubble_sort, font=("Helvetica", 12), bg="#4CAF50", fg="black")
        self.btn_bubble.pack(side=tk.LEFT, padx=10)
        
        self.btn_quick = tk.Button(self.btn_frame, text="Visualize Quick Sort (by Distance)", command=self.start_quick_sort, font=("Helvetica", 12), bg="#2196F3", fg="black")
        self.btn_quick.pack(side=tk.LEFT, padx=10)
        
        self.c_array = None
        self.num_elements = 7
        self.rects = []
        self.texts = []
        self.pointers = {}
        self.is_sorting = False
        
        # Keep a reference to the python callback to prevent garbage collection by ctypes
        self.c_callback = CALLBACK_TYPE(self._on_c_callback)
        
        self.reset_data()

    def my_sleep(self, ms):
        """Thread-safe sleep that yields to Tkinter to process UI redraws."""
        var = tk.IntVar()
        self.master.after(ms, var.set, 1)
        self.master.wait_variable(var)

    def reset_data(self):
        # Initial python data
        py_data = [
            (b"Thomas Bus", 70),
            (b"Fanta Bus", 20),
            (b"Omri Bus", 80),
            (b"Annoyed Driver Bus", 30),
            (b"Sleepy Bus", 90),
            (b"Party Bus", 10),
            (b"Late Bus", 50)
        ]
        
        # Load the data directly into a continuous C-memory buffer
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
            
            # Read directly from C struct memory
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
            
        self.master.update()

    def highlight(self, indices, color="#81c784"):
        for i in indices:
            if 0 <= i < self.num_elements:
                self.canvas.itemconfig(self.rects[i], fill=color)
        self.master.update()

    def unhighlight(self):
        for r in self.rects:
            self.canvas.itemconfig(r, fill="#546e7a")
        self.master.update()

    # ------------------ C-CALLBACK DRIVEN UI ------------------ #
    def _on_c_callback(self, event_type, p1, p2, p3, p4):
        """This function is invoked DIRECTLY by the C code during sorting!"""
        
        # Redraw array in case C just swapped elements in the prior step
        self.draw_array()
        
        if event_type == 1:
            # Comparing Event
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
                
            self.my_sleep(1200)
            self.unhighlight()
            
        elif event_type == 2:
            # Swap About To Happen Event
            ptrs = {}
            if p1 >= 0: ptrs["swap1"] = p1
            if p2 >= 0: ptrs["swap2"] = p2
            if p3 >= 0: ptrs["pivot"] = p3
            
            self.update_pointers(ptrs)
            
            name1 = self.c_array[p1].name.decode('utf-8', errors='ignore')
            name2 = self.c_array[p2].name.decode('utf-8', errors='ignore')
            self.info_label.config(text=f"[Native C Engine] YES! Swapping [ {name1} ] and [ {name2} ]")
            self.highlight([p1, p2], "#ffb74d")
            self.my_sleep(1200)
            self.unhighlight()
            # As soon as this returns, C will physically swap them in memory!
            
        elif event_type == 3:
            # Done Event
            self.update_pointers({})
            self.info_label.config(text="Native C Sort Complete! Memory is fully sorted.")
            self.btn_bubble.config(state=tk.NORMAL)
            self.btn_quick.config(state=tk.NORMAL)
            self.is_sorting = False

    def start_bubble_sort(self):
        if self.is_sorting: return
        self.is_sorting = True
        self.reset_data()
        self.btn_bubble.config(state=tk.DISABLED)
        self.btn_quick.config(state=tk.DISABLED)
        
        # Hook up python memory pointers directly to C!
        start_ptr = ctypes.pointer(self.c_array[0])
        end_ptr = ctypes.pointer(self.c_array[self.num_elements - 1])
        
        # Execute C code synchronously (it will yield to python via callbacks)
        viz_lib.visualize_bubble_sort_c(start_ptr, end_ptr, self.c_callback)

    def start_quick_sort(self):
        if self.is_sorting: return
        self.is_sorting = True
        self.reset_data()
        self.btn_bubble.config(state=tk.DISABLED)
        self.btn_quick.config(state=tk.DISABLED)
        
        start_ptr = ctypes.pointer(self.c_array[0])
        end_ptr = ctypes.pointer(self.c_array[self.num_elements - 1])
        
        DISTANCE = 0 # SortType.DISTANCE from C enum
        viz_lib.visualize_quick_sort_c(start_ptr, end_ptr, DISTANCE, self.c_callback)

if __name__ == "__main__":
    root = tk.Tk()
    app = SortVisualizer(root)
    root.mainloop()
