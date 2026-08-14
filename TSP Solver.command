#!/bin/bash
# Get the absolute path of the directory containing this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Ensure libraries are compiled
echo "Checking compilation..."
python3 compile.py

# Launch the UI
echo "Launching Visualizer..."
python3 src/py_ui/visualize_ui.py
