# TSP + Sorting Visualization and Expermintation (C + Python Integration)

# SUBMITTING FOR THE COMPETETION
---

### Student Details
* **Student Name:** [Omri Herzberg]
* **Course:** [C/C++]
* **University:** [HUJI]
* **Date:** May 2026

---

## Project Overview
This project is an advanced, hybrid application integrating **highly optimized C backend algorithms** with a **rich Tkinter-based Python GUI** via `ctypes`. The project visualizes fundamental algorithms in both **Travelling Salesperson Problem (TSP)** heuristics and **in-memory Array Sorting**, featuring interactive manipulation and live step-by-step state visualization.

---

## Key Features

### 1. Euclidean TSP Visualizer
* **Constructive Heuristics:** Nearest Neighbor, Greedy Edge-Insertion, and the 1.5-approximation **Christofides Algorithm** (with detailed MST & MWPM staging).
* **Refinement Heuristics:** 1-Opt, 2-Opt, and Simulated Annealing (with custom temperature constraints).
* **Lower Bound Computation:** Calculates Held-Karp style 1-Tree bounds with anchor-vertex selection.
* **Responsive Control Panel:** Decoupled asynchronous callback loop preventing Tkinter window freezing during high-compute algorithm loops.

### 2. Ramat Efal Friend's Router (Custom Topology Editor)
* **Step-by-Step Algorithm Visualization:** Watch Nearest Neighbor, Greedy, and Christofides build their routes along real streets. Christofides shows the MST (green) and Matching (orange dashed) stages before the final tour.
* **Performance Bar Chart:** Route Travel Cost panel displays a live bar chart comparing all algorithms that have been run, with 2-Opt savings shown as a purple stripe on top of its parent algorithm's bar.
* **Interactive Graph Editing:** Double-click to place named nodes, click-and-drag to adjust, and `Shift + Click` to dynamically draw connections.
* **Decoupled Configuration:** Read/write operations fully detached from the Python code and saved natively to a standalone `assets/ramat_efal_config.json` file.
* **Quick Presets:** Custom 3-column quick-select layout bound to your designated interjunction coordinates.

### 3. Array Sorting Visualizer
* **C-to-Python Rendering:** Visualizes Bubble Sort and Quick Sort executed in-place on C-memory structures, rendering pivots, swaps, and sorted sub-arrays in real time using native callback tracking.

---

## Directory Structure
```text
ex_2_plus/
├── src/
│   ├── c_core/                  # Core optimized C logic, sorting & TSP solvers
│   └── py_ui/                   # Tkinter visualizer frontend & ctypes bridge
├── assets/                      # Node configurations & map graphic assets
├── tests/                       # Integration test files (Pytest compatible)
├── build/                       # Compiled dynamic libraries (.so / .dylib / .dll)
├── scripts/                     # Developer utility scripts
├── compile.py                   # Cross-platform library compiler
└── README.md                    # Project documentation & setup instructions
```

---

## Setup & How to Run

### Prerequisite
Ensure Python 3.11+ is installed on your machine.

### Compile Shared Libraries
Since dynamic C libraries are machine-dependent, you must compile the shared libraries on your machine prior to running the code. We have included an automated, cross-platform build script:
```bash
python3 compile.py
```
This script dynamically detects your OS (macOS, Linux, Windows) and compiles:
* `build/libbuslines.<ext>`
* `build/libtsp.<ext>`
* `build/libefaltsp.<ext>`
* `build/libvisualize.<ext>`

### Run the Application
Start the main visualizer interface from the root directory:
```bash
python3 src/py_ui/visualize_ui.py
```

### Run the CLI Processing Script (Bus Lines Sorting)
```bash
python3 src/py_ui/main.py
```

### Run Integration Tests
Run the Pytest suite to validate logic correctness and FFI boundaries:
```bash
pytest tests/
```