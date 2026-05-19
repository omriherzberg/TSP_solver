"""
Diagnostic: trace every callback event for all 3 algorithms,
simulating abort after N callbacks, and checking whether event_type=3
(Done) is still received so _finish_run() would be called.
"""
import ctypes, os, random, math

class BusStation(ctypes.Structure):
    _fields_ = [("name", ctypes.c_char * 21), ("x", ctypes.c_double), ("y", ctypes.c_double)]

TSP_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_double)

lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build', 'libtsp.dylib'))
lib.tsp_brute_force.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, TSP_CB]; lib.tsp_brute_force.restype = None
lib.tsp_christofides.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, TSP_CB]; lib.tsp_christofides.restype = None
lib.tsp_greedy.argtypes = [ctypes.POINTER(BusStation), ctypes.c_int, TSP_CB]; lib.tsp_greedy.restype = None

def make_stations(n, seed=42):
    random.seed(seed)
    A = BusStation * n
    arr = A()
    for i in range(n):
        arr[i].name = f"S{i}".encode()
        arr[i].x = random.uniform(0, 100)
        arr[i].y = random.uniform(0, 100)
    return arr

def run_with_abort_after(algo_func, stations, n, abort_after_n_callbacks):
    """Run algo, abort after abort_after_n_callbacks calls, report if Done (event 3) arrives."""
    state = {"calls": 0, "aborted": False, "got_done": False, "events": []}

    def cb(event_type, path_ptr, path_len, dist):
        state["calls"] += 1
        state["events"].append(event_type)

        if event_type == 3:
            state["got_done"] = True
            return 0  # always accept Done

        if state["aborted"]:
            return 1  # keep telling C to abort

        if state["calls"] >= abort_after_n_callbacks:
            state["aborted"] = True
            return 1  # first abort signal

        return 0

    c_cb = TSP_CB(cb)
    algo_func(stations, n, c_cb)

    return state

SEPARATOR = "=" * 60

print(f"\n{SEPARATOR}")
print("DIAGNOSTIC: Abort Signal Flow Test")
print(SEPARATOR)

# ---- Test 1: Greedy abort ----
print("\n[TEST] Greedy — abort after 3 callbacks (N=15 nodes)")
st = make_stations(15)
res = run_with_abort_after(lib.tsp_greedy, st, 15, 3)
print(f"  Total callbacks received : {res['calls']}")
print(f"  Events received          : {res['events']}")
print(f"  abort_requested was set  : {res['aborted']}")
print(f"  event_type=3 received?   : {res['got_done']}")
if res["got_done"]:
    print("  RESULT: ✅ PASS — Done signal received after abort")
else:
    print("  RESULT: ❌ FAIL — Done signal NEVER received! UI would freeze.")

# ---- Test 2: Christofides abort during MST pause (first callback) ----
print("\n[TEST] Christofides — abort on very first callback (event 4, N=20 nodes)")
st = make_stations(20)
res = run_with_abort_after(lib.tsp_christofides, st, 20, 1)
print(f"  Total callbacks received : {res['calls']}")
print(f"  Events received          : {res['events']}")
print(f"  abort_requested was set  : {res['aborted']}")
print(f"  event_type=3 received?   : {res['got_done']}")
if res["got_done"]:
    print("  RESULT: ✅ PASS — Done signal received after abort")
else:
    print("  RESULT: ❌ FAIL — Done signal NEVER received! UI would freeze.")

# ---- Test 3: Christofides abort during MWPM pause (second callback) ----
print("\n[TEST] Christofides — abort on second callback (event 5, N=20 nodes)")
st = make_stations(20)
res = run_with_abort_after(lib.tsp_christofides, st, 20, 2)
print(f"  Total callbacks received : {res['calls']}")
print(f"  Events received          : {res['events']}")
print(f"  abort_requested was set  : {res['aborted']}")
print(f"  event_type=3 received?   : {res['got_done']}")
if res["got_done"]:
    print("  RESULT: ✅ PASS")
else:
    print("  RESULT: ❌ FAIL — UI would freeze.")

# ---- Test 4: Brute force abort ----
print("\n[TEST] Brute Force — abort after 5 callbacks (N=8 nodes)")
st = make_stations(8)
res = run_with_abort_after(lib.tsp_brute_force, st, 8, 5)
print(f"  Total callbacks received : {res['calls']}")
print(f"  Events received          : {res['events']}")
print(f"  abort_requested was set  : {res['aborted']}")
print(f"  event_type=3 received?   : {res['got_done']}")
if res["got_done"]:
    print("  RESULT: ✅ PASS")
else:
    print("  RESULT: ❌ FAIL — UI would freeze.")

# ---- Test 5: No abort — normal completion, all algorithms ----
print("\n[TEST] Normal run (no abort) — check all 3 algorithms send Done (N=6)")
st = make_stations(6)
for name, fn in [("Greedy", lib.tsp_greedy), ("Christofides", lib.tsp_christofides), ("BruteForce", lib.tsp_brute_force)]:
    res = run_with_abort_after(fn, st, 6, 9999)
    ok = "✅" if res["got_done"] else "❌"
    print(f"  {ok} {name}: events={res['events']}, got_done={res['got_done']}")

print(f"\n{SEPARATOR}\n")
