import os
import sys
import subprocess
import platform

def compile_libraries():
    sys_name = platform.system()
    
    # Determine output extension
    if sys_name == "Windows":
        ext = "dll"
    elif sys_name == "Darwin":
        ext = "dylib"
    else:
        ext = "so"
        
    print(f"Detected OS: {sys_name}")
    print(f"Building dynamic libraries with extension: .{ext}\n")
    
    # Target files
    root = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(root, "build")
    src_dir = os.path.join(root, "src", "c_core")
    
    os.makedirs(build_dir, exist_ok=True)
    
    compilation_units = [
        {
            "out": f"libbuslines.{ext}",
            "src": ["sort_bus_lines.c"]
        },
        {
            "out": f"libtsp.{ext}",
            "src": ["tsp_solver.c"]
        },
        {
            "out": f"libefaltsp.{ext}",
            "src": ["efal_tsp_solver.c"]
        },
        {
            "out": f"libvisualize.{ext}",
            "src": ["visualize_lib.c", "visualize_bubble_sort.c", "visualize_quick_sort.c", "sort_bus_lines.c"]
        }
    ]
    
    compiler = "gcc"
    if sys_name == "Windows":
        # Check for gcc or clang on Windows
        try:
            subprocess.run(["gcc", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            try:
                subprocess.run(["clang", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                compiler = "clang"
            except FileNotFoundError:
                print("Error: No C compiler (gcc or clang) found on your path! Please install gcc/MinGW or clang.")
                sys.exit(1)
                
    for unit in compilation_units:
        out_path = os.path.join(build_dir, unit["out"])
        src_paths = [os.path.join(src_dir, f) for f in unit["src"]]
        
        # Build command
        cmd = [compiler, "-shared", "-fPIC", "-o", out_path] + src_paths
        
        print(f"Compiling {unit['out']}...")
        print("Command:", " ".join(cmd))
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Successfully built: {unit['out']}\n")
            else:
                print(f"Failed to build: {unit['out']}")
                print("Error:\n", result.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error executing build command: {e}")
            sys.exit(1)
            
    print("All dynamic libraries compiled successfully!")

if __name__ == "__main__":
    compile_libraries()
