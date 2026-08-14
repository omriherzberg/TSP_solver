# 🏆 Competition Submission

# TSP + Sorting Visualization (C + Python Integration)
---

### Student Details
* **Student Name:** Omri Herzberg
* **Course:** C/C++
* **University:** HUJI
* **Date:** May 2026

---

## Project Overview
An advanced hybrid application integrating **highly optimized C backend algorithms** with a **rich Tkinter-based Python GUI** via `ctypes`. The project visualizes fundamental algorithms in both **Travelling Salesperson Problem (TSP)** heuristics and **in-memory Array Sorting**, featuring interactive manipulation and live step-by-step state visualization.

---

## Key Features

### 1. Euclidean TSP Visualizer
* **Constructive Heuristics:** Nearest Neighbor, Greedy Edge-Insertion, and the 1.5-approximation **Christofides Algorithm** (with detailed MST & MWPM staging, step-by-step node-by-node visualization).
* **Refinement Heuristics:** 1-Opt (node relocation) and 2-Opt (edge uncrossing), both with color-coded live feedback — **Green** = initial tour, **Purple** flash = swap made, **Blue** = final improved tour.
* **Simulated Annealing:** Configurable cooling rate and initial temperature ratio, with a live temperature-history chart.
* **Lower Bound Computation:** Calculates Held-Karp style 1-Tree bounds with anchor-vertex selection.
* **Geometric Presets:** Circle, Clusters, and Grid node arrangements to highlight algorithmic differences.
* **Responsive Control Panel:** Decoupled asynchronous C-to-Python callback loop preventing Tkinter freezing during high-throughput evaluation.

### 2. Ramat Efal Friend's Router (Road Graph TSP)
* **Real Map Background:** Operates on a real PNG map of Ramat Efal with a pre-loaded road graph.
* **Step-by-Step Algorithm Visualization:** Watch Nearest Neighbor and Greedy build roads edge-by-edge. Christofides visually shows **Stage 1 (MST, green)** and **Stage 2 (Odd Vertex Matching, orange dashed)** before drawing the final tour.
* **Performance Bar Chart:** The Route Travel Cost panel displays a live bar chart comparing all algorithms that have been run. 2-Opt savings are shown as a **purple stripe** on top of the originating algorithm's bar.
* **Named Presets:** Quick-add buttons for locations like Shula, Harpaz, Carrefour, My House, etc. The optimal path sequence shows real names, not node indices.
* **Interactive Graph Editor:** A dedicated tab to double-click/drag/shift-click to modify the road network and save it to `assets/ramat_efal_config.json`.

### 3. Array Sorting Visualizer
* **C-to-Python Rendering:** Visualizes Bubble Sort and Quick Sort executed in-place on C-memory structures, rendering pivots, swaps, and sorted sub-arrays in real time using native callback tracking.

---

## Directory Structure
```text
ex_2_plus/
├── src/
│   ├── c_core/                  # Core optimized C logic: TSP solvers, Efal solver, sorting
│   └── py_ui/                   # Tkinter visualizer frontend & ctypes bridge
├── assets/                      # Map image & road graph configuration (ramat_efal_config.json)
├── tests/                       # Integration tests (Pytest) — 28 tests, all passing
├── build/                       # Compiled dynamic libraries (auto-generated, git-ignored)
├── compile.py                   # Cross-platform library compiler (macOS/Linux/Windows)
└── README.md                    # This file
```

---

## Setup & How to Run

### Prerequisites
* Python 3.11+
* GCC or Clang (any modern C compiler on your PATH)

### Step 1 — Install Dependencies
Install the required Python packages (currently just pytest for testing):
```bash
pip install -r requirements.txt
```

### Step 2 — Run the Application

**Option A: macOS Users (Quick Launch)**
Simply double-click the `TSP Solver.command` file in Finder! This script automatically compiles all the C libraries in the background and launches the graphical interface instantly. 

**Option B: Linux & Windows Users (Terminal)**
Dynamic C libraries are machine-specific and **must be compiled before running**. Use the included cross-platform build script:
```bash
python3 compile.py
```
This detects your OS and outputs:
* `build/libbuslines.<ext>`
* `build/libtsp.<ext>`
* `build/libefaltsp.<ext>`
* `build/libvisualize.<ext>`

Where `<ext>` is `dylib` (macOS), `so` (Linux), or `dll` (Windows).

Once compiled, launch the UI via terminal:
```bash
python3 src/py_ui/visualize_ui.py
```

### Run the CLI Script (Bus Lines Sorting)
```bash
python3 src/py_ui/main.py
```

### Run Integration Tests
```bash
pytest tests/
```
All 28 tests should pass on a clean compile.