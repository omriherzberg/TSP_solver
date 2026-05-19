# TSP Visualization Event Types (matching C constants.h)
EVENT_EVALUATING = 1        # Path/Edge is being evaluated/considered
EVENT_PATH_CONFIRMED = 2    # Exact/greedy path confirmed
EVENT_DONE = 3              # Done/cleanup signal to unlock UI
EVENT_MST_CONFIRMED = 4     # MST edges computed (Christofides Step 1)
EVENT_MWPM_CONFIRMED = 5     # MWPM edges computed (Christofides Step 2)
EVENT_GREEDY_EDGES = 6      # Greedy Edge-Insertion intermediate state
EVENT_1TREE_EVALUATING = 7  # 1-Tree evaluating state
EVENT_1TREE_CONFIRMED = 8   # Final Max 1-Tree locked in
EVENT_MWPM_DELEGATE = 9     # exact MWPM computation delegation request
EVENT_2OPT_SWAP = 10        # 2-opt edge uncrossing performed
EVENT_1OPT_SWAP = 11        # 1-opt node relocation performed
EVENT_2OPT_EVALUATING = 12  # evaluating a 2-opt swap
EVENT_1OPT_EVALUATING = 13  # evaluating a 1-opt insertion

# GUI Sizing Constants
CANVAS_WIDTH = 1350
CANVAS_HEIGHT = 450

# Visual Styling and Colors (Harmonious Sleek Dark Mode Palette)
COLOR_BACKGROUND_DARK = "#2b2b2b"
COLOR_CANVAS_BG = "#3c3f41"
COLOR_NODE_DEFAULT = "#ffc66d"
COLOR_NODE_EVALUATING = "#a9b7c6"

# Heuristic Solver Visual Edge Colors
COLOR_EDGE_EVALUATING = "#a9b7c6"
COLOR_EDGE_CONFIRMED = "#ffc66d"
COLOR_EDGE_MST = "#81c784"
COLOR_EDGE_MWPM = "#03A9F4"
COLOR_EDGE_GREEDY = "#E91E63"
COLOR_EDGE_1TREE_EVAL = "#FF4081"
COLOR_EDGE_1TREE_EVAL_DASH = "#ff8da1"
COLOR_EDGE_1TREE_CONFIRMED = "#FFD700"
