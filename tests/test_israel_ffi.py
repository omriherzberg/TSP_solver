import ctypes
import os

lib_dir = os.path.dirname(os.path.abspath(__file__))
israel_lib = ctypes.CDLL(os.path.join(lib_dir, '..', 'build', 'libisrael.dylib'))

CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_double)

israel_lib.israel_init.argtypes = []
israel_lib.israel_init.restype = None
israel_lib.israel_num_cities.argtypes = []
israel_lib.israel_num_cities.restype = ctypes.c_int
israel_lib.israel_tsp_nearest_neighbor.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), CALLBACK_TYPE]
israel_lib.israel_tsp_nearest_neighbor.restype = ctypes.c_double
israel_lib.israel_tsp_greedy.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int), CALLBACK_TYPE]
israel_lib.israel_tsp_greedy.restype = ctypes.c_double
israel_lib.israel_tsp_2opt.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int), CALLBACK_TYPE]
israel_lib.israel_tsp_2opt.restype = ctypes.c_double
israel_lib.israel_tsp_christofides.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int), CALLBACK_TYPE]
israel_lib.israel_tsp_christofides.restype = ctypes.c_double

israel_lib.israel_init()

N = israel_lib.israel_num_cities()
print(f"Num cities: {N}")

def dummy_cb(event_type, path_ptr, path_len, current_dist):
    return 0

c_dummy_cb = CALLBACK_TYPE(dummy_cb)

# Nearest neighbor
TourArray = ctypes.c_int * N
tour = TourArray()
cost = israel_lib.israel_tsp_nearest_neighbor(0, 0, tour, c_dummy_cb)
print(f"NN: cost = {cost:.2f}, tour = {list(tour)[:5]}...")

# Greedy
tour = TourArray()
cost = israel_lib.israel_tsp_greedy(0, tour, c_dummy_cb)
print(f"Greedy: cost = {cost:.2f}, tour = {list(tour)[:5]}...")

# Christofides
tour = TourArray()
cost = israel_lib.israel_tsp_christofides(0, tour, c_dummy_cb)
print(f"Christofides: cost = {cost:.2f}, tour = {list(tour)[:5]}...")

