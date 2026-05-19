import ctypes
import os



# 1. Define the Python equivalent of the C struct
class BusLine(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * 21),
        ("distance", ctypes.c_int),
        ("duration", ctypes.c_int),
        ("frequency", ctypes.c_int)
    ]

DISTANCE = 0
DURATION = 1
FREQUENCY = 2

# 2. Load the library
lib_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'build', 'libbuslines.dylib'))
try:
    bus_lib = ctypes.CDLL(lib_path)
except OSError:
    print(f"Error: Could not load {lib_path}")
    exit(1)

# 3. Set up C function signatures
bus_lib.bus_bubble_sort.argtypes = [ctypes.POINTER(BusLine), ctypes.POINTER(BusLine)]
bus_lib.bus_bubble_sort.restype = None

bus_lib.bus_quick_sort.argtypes = [ctypes.POINTER(BusLine), ctypes.POINTER(BusLine), ctypes.c_int]
bus_lib.bus_quick_sort.restype = None

def process_buses(inputs, sort_type):
    """
    Takes string inputs, converts them to C structs, and uses the shared library to sort them.
    """
    num_buses = len(inputs)
    if num_buses == 0:
        return

    # Create the contiguous C array in memory
    BusArrayType = BusLine * num_buses
    bus_array = BusArrayType()

    # Parse Python strings and pack them into the C structs
    for i, line in enumerate(inputs):
        parts = line.split(',')
        if len(parts) != 4:
            raise ValueError("Invalid number of fields")
        name, dist, dur, freq = parts
        
        # Security Fix: Ensure string fits into char[21] with room for null terminator
        if len(name) > 20:
            raise ValueError(f"Bus name '{name}' exceeds 20 characters")
        import re
        if not re.match(r'^[a-z0-9]*$', name):
            raise ValueError("Bus name must contain only lowercase letters and digits")
            
        dist = int(dist)
        dur = int(dur)
        freq = int(freq)
        
        if not (0 <= dist <= 1000):
            raise ValueError("Distance must be between 0 and 1000")
        if not (10 <= dur <= 100):
            raise ValueError("Duration must be between 10 and 100")
        if not (1 <= freq <= 50):
            raise ValueError("Frequency must be between 1 and 50")
            
        bus_array[i].name = name.encode('utf-8')
        bus_array[i].distance = dist
        bus_array[i].duration = dur
        bus_array[i].frequency = freq

    # Grab pointers to the first and last element of the array
    start_ptr = ctypes.pointer(bus_array[0])
    end_ptr = ctypes.pointer(bus_array[num_buses - 1])
    
    # Call the actual C code inside the shared library!
    if sort_type == "by_name":
        bus_lib.bus_bubble_sort(start_ptr, end_ptr)
    else:
        enum_val = DISTANCE
        if sort_type == "by_duration":
            enum_val = DURATION
        elif sort_type == "by_frequency":
            enum_val = FREQUENCY
            
        bus_lib.bus_quick_sort(start_ptr, end_ptr, enum_val)

    # The array was sorted in-place by C. Now we unpack the C structs and print them in Python.
    for i in range(num_buses):
        bus = bus_array[i]
        print(f"{bus.name.decode('utf-8')},{bus.distance},{bus.duration},{bus.frequency}")

if __name__ == "__main__":
    print("--- Using C Shared Library via Python ctypes ---\n")
    
    test_inputs = [
        "busa,500,20,5",
        "busc,100,10,2",
        "busb,200,15,3"
    ]
    
    print("Results after C Quick Sort (by_distance):")
    try:
        process_buses(test_inputs, "by_distance")
    except ValueError as e:
        print(f"Invalid Input! Error processing bus data: {e}")
