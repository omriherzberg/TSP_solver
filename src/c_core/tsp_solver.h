#ifndef TSP_SOLVER_H
#define TSP_SOLVER_H

#include "constants.h"

typedef struct BusStation {
    char name[NAME_LEN];
    double x;
    double y;
} BusStation;

// Callback type for Python UI.
// event_type: 1 = Evaluating/Considering, 2 = Edge/Path Confirmed, 3 = Done
// path_len=2 means a single edge (u,v); path_len=N means a full Hamiltonian path
// RETURNS: 1 if user requested abort, 0 to continue
typedef int (*TspVizCallback)(int event_type, int* path_indices, int path_len, double current_dist);

// Computes the exact shortest path using O(N!) Brute Force
void tsp_brute_force(BusStation* stations, int num_stations, TspVizCallback cb);

// Computes an approximate shortest path using the Christofides algorithm
void tsp_christofides(BusStation* stations, int num_stations, TspVizCallback cb);

// Real Greedy: sort ALL edges by length, greedily add shortest that doesn't
// violate degree<=2 or create a premature cycle (Union-Find).
void tsp_greedy(BusStation* stations, int num_stations, TspVizCallback cb);

// Nearest Neighbor: from node 0, always go to the closest unvisited node.
void tsp_nearest_neighbor(BusStation* stations, int num_stations, TspVizCallback cb);

// Random Path: just generates a random permutation of nodes.
void tsp_random(BusStation* stations, int num_stations, TspVizCallback cb);

// Computes the total path cost
double get_path_cost(BusStation* stations, int num_stations, int* path);

// Computes the maximum 1-tree lower bound by evaluating 1-trees centered at each node.
void tsp_max_1_tree(BusStation* stations, int num_stations, TspVizCallback cb);

// Local Search Optimizations
// These functions take an existing path and optimize it in-place.
// They return the final optimized cost.
double tsp_1opt(BusStation* stations, int num_stations, int* path, TspVizCallback cb);
double tsp_2opt(BusStation* stations, int num_stations, int* path, TspVizCallback cb);
double tsp_simulated_annealing(BusStation* stations, int num_stations, int* path, TspVizCallback cb, double initial_temp_ratio, double cooling_rate);

// Expose comparison count stats for the UI
long long get_tsp_comparison_count(void);
void reset_tsp_comparison_count(void);
void add_tsp_comparison_count(long long count);

#endif // TSP_SOLVER_H
