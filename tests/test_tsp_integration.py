import ctypes
import os
import pytest
import math
import random
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'py_ui'))
from constants import *

# 1. Map the C struct identically
class BusStation(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * 21),
        ("x", ctypes.c_double),
        ("y", ctypes.c_double)
    ]

# Callback type
# int event_type, int* path_indices, int path_len, double current_dist
# Returns 1 for abort, 0 for continue
CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_double)

# Load library
import platform
sys_name = platform.system()
ext = "dll" if sys_name == "Windows" else ("dylib" if sys_name == "Darwin" else "so")

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build', f'libtsp.{ext}')
tsp_lib = ctypes.CDLL(lib_path)

tsp_lib.tsp_brute_force.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, CALLBACK_TYPE]
tsp_lib.tsp_brute_force.restype = None

tsp_lib.tsp_christofides.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, CALLBACK_TYPE]
tsp_lib.tsp_christofides.restype = None

tsp_lib.tsp_greedy.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, CALLBACK_TYPE]
tsp_lib.tsp_greedy.restype = None

tsp_lib.tsp_nearest_neighbor.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, CALLBACK_TYPE]
tsp_lib.tsp_nearest_neighbor.restype = None

tsp_lib.tsp_max_1_tree.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, CALLBACK_TYPE]
tsp_lib.tsp_max_1_tree.restype = None

tsp_lib.tsp_1opt.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, ctypes.POINTER(ctypes.c_int), CALLBACK_TYPE]
tsp_lib.tsp_1opt.restype = ctypes.c_double

tsp_lib.tsp_2opt.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, ctypes.POINTER(ctypes.c_int), CALLBACK_TYPE]
tsp_lib.tsp_2opt.restype = ctypes.c_double

tsp_lib.tsp_simulated_annealing.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, ctypes.POINTER(ctypes.c_int), CALLBACK_TYPE]
tsp_lib.tsp_simulated_annealing.restype = ctypes.c_double

def run_tsp_algo(algo_func, python_stations):
    n = len(python_stations)
    if n == 0:
        return [], 0.0
        
    ArrayType = BusStation * n
    c_array = ArrayType()
    for i, st in enumerate(python_stations):
        c_array[i].name = st["name"].encode('utf-8')
        c_array[i].x = st["x"]
        c_array[i].y = st["y"]
        
    final_path = []
    final_cost = [float('inf')]
    
    def cb(event_type, path_ptr, path_len, current_dist):
        if event_type == EVENT_PATH_CONFIRMED: # New Best Path Found
            if path_ptr and path_len == n:
                final_cost[0] = current_dist
                final_path.clear()
                for i in range(path_len):
                    final_path.append(path_ptr[i])
        elif event_type == EVENT_MWPM_DELEGATE:
            num_odds = path_len
            odds = [path_ptr[i] for i in range(num_odds)]
            import networkx as nx
            G = nx.Graph()
            for i in range(num_odds):
                for j in range(i + 1, num_odds):
                    n1, n2 = odds[i], odds[j]
                    dx = c_array[n1].x - c_array[n2].x
                    dy = c_array[n1].y - c_array[n2].y
                    dist = (dx*dx + dy*dy)**0.5
                    G.add_edge(i, j, weight=-dist)
            matching_pairs = nx.algorithms.matching.max_weight_matching(G, maxcardinality=True)
            partner_map = {}
            for u, v in matching_pairs:
                partner_map[u] = v
                partner_map[v] = u
            for i in range(num_odds):
                path_ptr[num_odds + i] = partner_map.get(i, -1)
        return 0
                    
    c_cb = CALLBACK_TYPE(cb)
    algo_func(c_array, n, c_cb)
    return final_path, final_cost[0]

# =====================================================================
# INTEGRATION TESTS
# =====================================================================

def get_square_stations():
    # A perfect 10x10 square. The optimal path is the perimeter = 40.0
    return [
        {"name": "A", "x": 0.0, "y": 0.0},
        {"name": "B", "x": 0.0, "y": 10.0},
        {"name": "C", "x": 10.0, "y": 10.0},
        {"name": "D", "x": 10.0, "y": 0.0}
    ]

def test_brute_force_optimal_square():
    stations = get_square_stations()
    path, cost = run_tsp_algo(tsp_lib.tsp_brute_force, stations)
    assert math.isclose(cost, 40.0), f"Brute force failed optimal calculation. Got {cost}"
    assert len(path) == 4
    assert len(set(path)) == 4 # Ensure all unique vertices visited

def test_christofides_square_validity():
    stations = get_square_stations()
    path, cost = run_tsp_algo(tsp_lib.tsp_christofides, stations)
    # Christofides guarantees a path length within 1.5 * optimal
    assert cost <= 40.0 * 1.5
    assert len(path) == 4
    assert len(set(path)) == 4

def test_greedy_square_validity():
    stations = get_square_stations()
    path, cost = run_tsp_algo(tsp_lib.tsp_greedy, stations)
    # Greedy on a perfect square starting from 0 should find optimal, but we just check it's valid
    assert cost >= 40.0
    assert len(path) == 4
    assert len(set(path)) == 4

def test_complex_random_graph():
    """
    Tests all 3 algorithms on an 8-node random map to ensure:
    1. Brute Force doesn't crash on slightly larger graphs.
    2. Christofides honors the 1.5x mathematical boundary.
    3. Greedy finds a valid Hamiltonian cycle.
    """
    random.seed(42)
    stations = []
    for i in range(8):
        stations.append({
            "name": f"Station {i}", 
            "x": random.uniform(0, 100), 
            "y": random.uniform(0, 100)
        })
        
    bf_path, bf_cost = run_tsp_algo(tsp_lib.tsp_brute_force, stations)
    ch_path, ch_cost = run_tsp_algo(tsp_lib.tsp_christofides, stations)
    gr_path, gr_cost = run_tsp_algo(tsp_lib.tsp_greedy, stations)
    
    assert bf_cost > 0, "Brute force cost should be > 0"
    assert len(set(bf_path)) == 8, "Brute force path must be a hamiltonian cycle"
    
    # Christofides theoretical maximum limit: 1.5 * Optimal
    assert ch_cost <= 1.501 * bf_cost, f"Christofides violated mathematical bound! BF: {bf_cost}, Christofides: {ch_cost}"
    assert len(set(ch_path)) == 8, "Christofides failed to visit all nodes"
    
    # Greedy bounds can be anything, just check validity
    assert gr_cost > 0
    assert len(set(gr_path)) == 8, "Greedy failed to visit all nodes"
    
    nn_path, nn_cost = run_tsp_algo(tsp_lib.tsp_nearest_neighbor, stations)
    assert nn_cost > 0
    assert len(set(nn_path)) == 8, "Nearest Neighbor failed to visit all nodes"

def test_single_node_handling():
    stations = [{"name": "Lonely Bus", "x": 50.0, "y": 50.0}]
    
    bf_path, bf_cost = run_tsp_algo(tsp_lib.tsp_brute_force, stations)
    assert len(bf_path) == 0
    
    ch_path, ch_cost = run_tsp_algo(tsp_lib.tsp_christofides, stations)
    assert len(ch_path) == 0

    gr_path, gr_cost = run_tsp_algo(tsp_lib.tsp_greedy, stations)
    assert len(gr_path) == 0

    nn_path, nn_cost = run_tsp_algo(tsp_lib.tsp_nearest_neighbor, stations)
    assert len(nn_path) == 0

def test_lower_bound_correctness():
    # Generate random points for a small graph
    random.seed(42)
    stations = []
    for i in range(8):
        stations.append({
            "name": f"Station {i}",
            "x": random.uniform(0, 100),
            "y": random.uniform(0, 100)
        })
        
    bf_path, bf_cost = run_tsp_algo(tsp_lib.tsp_brute_force, stations)
    
    # Run the Max 1-Tree Lower Bound solver
    # Event 8 callback gives the final maximum cost
    lb_cost_wrapper = [0.0]
    
    def viz_cb(event_type, path_ptr, path_len, current_dist):
        if event_type == EVENT_1TREE_CONFIRMED:
            lb_cost_wrapper[0] = current_dist
        return 0
        
    c_cb = CALLBACK_TYPE(viz_cb)
    
    # Serialize stations
    CStationArray = BusStation * len(stations)
    c_stations = CStationArray()
    for i, s in enumerate(stations):
        c_stations[i].name = s["name"].encode('utf-8')
        c_stations[i].x = s["x"]
        c_stations[i].y = s["y"]
        
    tsp_lib.tsp_max_1_tree(c_stations, len(stations), c_cb)
    
    lb_cost = lb_cost_wrapper[0]
    
    assert lb_cost > 0, "Lower bound cost should be positive"
    assert lb_cost <= bf_cost + 1e-5, f"Lower bound {lb_cost} exceeded the exact optimal tour cost {bf_cost}! Math violation!"
    print(f"[TEST SUCCESS] 1-Tree Lower Bound: {lb_cost:.4f} <= Exact Optimal Cost: {bf_cost:.4f}")

def test_local_search_optimizations():
    # A known crossing square to test 2-opt
    stations = [
        {"name": "A", "x": 0.0, "y": 0.0},
        {"name": "C", "x": 10.0, "y": 10.0},
        {"name": "B", "x": 10.0, "y": 0.0},
        {"name": "D", "x": 0.0, "y": 10.0}
    ]
    # Path with a crossing: A -> C -> B -> D -> A
    # Cost: sqrt(200) + 10 + sqrt(200) + 10 = ~48.28
    
    n = len(stations)
    CStationArray = BusStation * n
    c_stations = CStationArray()
    for i, s in enumerate(stations):
        c_stations[i].name = s["name"].encode('utf-8')
        c_stations[i].x = s["x"]
        c_stations[i].y = s["y"]
        
    path_array = (ctypes.c_int * n)(0, 1, 2, 3)
    
    def cb(event_type, path_ptr, path_len, current_dist):
        return 0
    c_cb = CALLBACK_TYPE(cb)
    
    optimized_cost_2opt = tsp_lib.tsp_2opt(c_stations, n, path_array, c_cb)
    # The optimal uncrossed square path: A -> B -> C -> D -> A
    # Cost: 10 + 10 + 10 + 10 = 40.0
    assert optimized_cost_2opt < 48.0
    assert math.isclose(optimized_cost_2opt, 40.0, rel_tol=1e-5), f"2-opt failed to uncross. Cost: {optimized_cost_2opt}"
    
    # Test 1-opt
    # An example where 1-opt can easily fix a misaligned node
    stations_1opt = [
        {"name": "P1", "x": 0.0, "y": 0.0},
        {"name": "P2", "x": 2.0, "y": 0.0},
        {"name": "P3", "x": 4.0, "y": 0.0},
        {"name": "P5", "x": 8.0, "y": 0.0},
        {"name": "P4", "x": 6.0, "y": 0.0}
    ]
    n_1opt = len(stations_1opt)
    CStationArray_1opt = BusStation * n_1opt
    c_stations_1opt = CStationArray_1opt()
    for i, s in enumerate(stations_1opt):
        c_stations_1opt[i].name = s["name"].encode('utf-8')
        c_stations_1opt[i].x = s["x"]
        c_stations_1opt[i].y = s["y"]
        
    path_array_1opt = (ctypes.c_int * n_1opt)(0, 1, 2, 3, 4)
    # The path is 0->1->2->3(P5)->4(P4)->0
    # Cost: 2 + 2 + 4 + 2 + 6 = 16
    # Optimal is 0->1->2->4(P4)->3(P5)->0
    # Cost: 2 + 2 + 2 + 2 + 8 = 16 (actually, same cost because it's a line returning to start, 
    # but let's just make sure 1-opt runs without crashing and possibly improves or stays same)
    
    optimized_cost_1opt = tsp_lib.tsp_1opt(c_stations_1opt, n_1opt, path_array_1opt, c_cb)
    assert optimized_cost_1opt <= 16.0
    print(f"[TEST SUCCESS] Local Search passed. 2-opt cost: {optimized_cost_2opt}, 1-opt cost: {optimized_cost_1opt}")

def test_simulated_annealing_square():
    # A known crossing square to test Simulated Annealing
    stations = [
        {"name": "A", "x": 0.0, "y": 0.0},
        {"name": "C", "x": 10.0, "y": 10.0},
        {"name": "B", "x": 10.0, "y": 0.0},
        {"name": "D", "x": 0.0, "y": 10.0}
    ]
    n = len(stations)
    CStationArray = BusStation * n
    c_stations = CStationArray()
    for i, s in enumerate(stations):
        c_stations[i].name = s["name"].encode('utf-8')
        c_stations[i].x = s["x"]
        c_stations[i].y = s["y"]
        
    path_array = (ctypes.c_int * n)(0, 1, 2, 3)
    
    def cb(event_type, path_ptr, path_len, current_dist):
        return 0
    c_cb = CALLBACK_TYPE(cb)
    
    sa_cost = tsp_lib.tsp_simulated_annealing(c_stations, n, path_array, c_cb)
    # The optimal uncrossed square path: A -> B -> C -> D -> A = 40.0
    assert sa_cost <= 40.0 + 1e-5, f"Simulated annealing failed to reach optimal square. Got {sa_cost}"

