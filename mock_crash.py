import visualize_ui
import tkinter as tk

app = visualize_ui.MainApp()
tsp_tab = app.tsp_tab

# Generate map
tsp_tab.generate_map()

# Run Christofides
try:
    tsp_tab.start_christofides()
except Exception as e:
    import traceback
    traceback.print_exc()
