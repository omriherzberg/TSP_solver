#include "tsp_solver.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <float.h>

long long tsp_comparison_count = 0;

long long get_tsp_comparison_count(void) {
    return tsp_comparison_count;
}

void reset_tsp_comparison_count(void) {
    tsp_comparison_count = 0;
}

double get_dist(BusStation a, BusStation b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return sqrt(dx*dx + dy*dy);
}

// ---------------------------------------------------------
// 1. BRUTE FORCE EXACT SOLVER
// ---------------------------------------------------------
int tsp_bf_recursive(BusStation* stations, int num_stations, int* current_path, int depth, int* visited, double current_cost, int* best_path, double* min_cost, TspVizCallback cb) {
    if (depth == num_stations) {
        // Complete the cycle by returning to the start (index 0)
        double total_cost = current_cost + get_dist(stations[current_path[num_stations-1]], stations[current_path[0]]);
        
        // Notify UI that a full path is being evaluated
        if (cb && cb(1, current_path, num_stations, total_cost)) return 1;

        tsp_comparison_count++;
        if (total_cost < *min_cost) {
            *min_cost = total_cost;
            for(int i = 0; i < num_stations; i++) best_path[i] = current_path[i];
            
            // Notify UI of a new global best
            if (cb && cb(2, best_path, num_stations, total_cost)) return 1;
        }
        return 0;
    }

    for (int i = 1; i < num_stations; i++) {
        if (!visited[i]) {
            visited[i] = 1;
            current_path[depth] = i;
            double cost_added = get_dist(stations[current_path[depth-1]], stations[i]);
            
            // Intentional pure brute-force: Explore every single branch without any pruning
            if (tsp_bf_recursive(stations, num_stations, current_path, depth + 1, visited, current_cost + cost_added, best_path, min_cost, cb)) return 1;
            
            visited[i] = 0;
        }
    }
    return 0;
}

void tsp_brute_force(BusStation* stations, int num_stations, TspVizCallback cb) {
    reset_tsp_comparison_count();
    if (num_stations <= 1) {
        if (cb) cb(3, NULL, 0, 0);
        return;
    }

    int* current_path = malloc(sizeof(int) * num_stations);
    int* best_path = malloc(sizeof(int) * num_stations);
    int* visited = calloc(num_stations, sizeof(int));
    
    current_path[0] = 0;
    visited[0] = 1;
    double min_cost = DBL_MAX;
    
    tsp_bf_recursive(stations, num_stations, current_path, 1, visited, 0.0, best_path, &min_cost, cb);
    
    // Send Done signal
    if (cb) cb(3, best_path, num_stations, min_cost);
    
    free(current_path);
    free(best_path);
    free(visited);
}

// ---------------------------------------------------------
// 2. CHRISTOFIDES ALGORITHM
// ---------------------------------------------------------

double** create_dist_matrix(BusStation* stations, int n) {
    double** mat = malloc(n * sizeof(double*));
    for (int i = 0; i < n; i++) {
        mat[i] = malloc(n * sizeof(double));
        for (int j = 0; j < n; j++) {
            mat[i][j] = get_dist(stations[i], stations[j]);
        }
    }
    return mat;
}

// Returns parent array representing the Minimum Spanning Tree (MST)
int* prim_mst(double** dist, int n, int* degrees) {
    int* parent = malloc(n * sizeof(int));
    double* key = malloc(n * sizeof(double));
    int* in_mst = calloc(n, sizeof(int));
    
    for (int i = 0; i < n; i++) {
        key[i] = DBL_MAX;
        degrees[i] = 0;
    }
    
    key[0] = 0;
    parent[0] = -1;
    
    for (int count = 0; count < n - 1; count++) {
        double min = DBL_MAX;
        int u = -1;
        for (int v = 0; v < n; v++) {
            tsp_comparison_count++;
            if (!in_mst[v] && key[v] < min) {
                min = key[v];
                u = v;
            }
        }
        
        in_mst[u] = 1;
        
        for (int v = 0; v < n; v++) {
            tsp_comparison_count++;
            if (dist[u][v] > 0 && !in_mst[v] && dist[u][v] < key[v]) {
                parent[v] = u;
                key[v] = dist[u][v];
            }
        }
    }
    
    // Calculate degree of each vertex in the MST
    for (int i = 1; i < n; i++) {
        degrees[i]++;
        degrees[parent[i]]++;
    }
    
    free(key);
    free(in_mst);
    return parent;
}

// Extracts vertices with an odd degree
int* get_odd_vertices(int* degrees, int n, int* num_odds) {
    int* odds = malloc(n * sizeof(int));
    *num_odds = 0;
    for (int i = 0; i < n; i++) {
        if (degrees[i] % 2 != 0) {
            odds[(*num_odds)++] = i;
        }
    }
    return odds;
}

// Greedy Minimum Weight Perfect Matching Approximation
// Exact MWPM is O(N^3) (Edmonds' Blossom) or exponential (brute-force).
// To support N=1000 without freezing, we use a fast greedy matching.
int* get_mwpm(int* odds, int num_odds, double** dist) {
    int* matching = malloc(num_odds * sizeof(int));
    int* matched = calloc(num_odds, sizeof(int));
    
    for (int i = 0; i < num_odds; i++) matching[i] = -1;
    
    for (int i = 0; i < num_odds; i++) {
        if (matched[i]) continue;
        
        int best_j = -1;
        double min_dist = DBL_MAX;
        
        for (int j = i + 1; j < num_odds; j++) {
            if (!matched[j]) {
                tsp_comparison_count++;
                if (dist[odds[i]][odds[j]] < min_dist) {
                    min_dist = dist[odds[i]][odds[j]];
                    best_j = j;
                }
            }
        }
        
        if (best_j != -1) {
            matching[i] = best_j;
            matching[best_j] = i;
            matched[i] = 1;
            matched[best_j] = 1;
        }
    }
    
    free(matched);
    return matching;
}

// Build Eulerian Multigraph
typedef struct EdgeNode {
    int to;
    int used;
    struct EdgeNode* next;
} EdgeNode;

void add_edge(EdgeNode** adj, int u, int v) {
    EdgeNode* node1 = malloc(sizeof(EdgeNode));
    node1->to = v; node1->used = 0; node1->next = adj[u]; adj[u] = node1;
    
    EdgeNode* node2 = malloc(sizeof(EdgeNode));
    node2->to = u; node2->used = 0; node2->next = adj[v]; adj[v] = node2;
}

EdgeNode** build_multigraph(int n, int* parent, int* odds, int num_odds, int* matching) {
    EdgeNode** adj = calloc(n, sizeof(EdgeNode*));
    
    // Add MST edges
    for (int i = 1; i < n; i++) {
        add_edge(adj, i, parent[i]);
    }
    
    // Add Matching edges
    int* matched_visited = calloc(num_odds, sizeof(int));
    for (int i = 0; i < num_odds; i++) {
        if (!matched_visited[i]) {
            int u = odds[i];
            int v = odds[matching[i]];
            add_edge(adj, u, v);
            matched_visited[i] = 1;
            matched_visited[matching[i]] = 1;
        }
    }
    free(matched_visited);
    return adj;
}

// Hierholzer's Algorithm
void eulerian_tour(EdgeNode** adj, int u, int* tour, int* tour_idx) {
    EdgeNode* edge = adj[u];
    while (edge != NULL) {
        if (!edge->used) {
            edge->used = 1;
            EdgeNode* rev = adj[edge->to];
            while (rev != NULL) {
                if (rev->to == u && !rev->used) {
                    rev->used = 1;
                    break;
                }
                rev = rev->next;
            }
            eulerian_tour(adj, edge->to, tour, tour_idx);
        }
        edge = edge->next;
    }
    tour[(*tour_idx)++] = u;
}

int* get_hamiltonian(int* tour, int tour_len, int n) {
    int* path = malloc(n * sizeof(int));
    int* visited = calloc(n, sizeof(int));
    int idx = 0;
    
    for (int i = tour_len - 1; i >= 0; i--) {
        int u = tour[i];
        if (!visited[u]) {
            visited[u] = 1;
            path[idx++] = u;
        }
    }
    free(visited);
    return path;
}

void tsp_christofides(BusStation* stations, int num_stations, TspVizCallback cb) {
    reset_tsp_comparison_count();
    if (num_stations <= 1) {
        if (cb) cb(3, NULL, 0, 0);
        return;
    }

    double** dist = create_dist_matrix(stations, num_stations);
    int* degrees = calloc(num_stations, sizeof(int));
    int* parent = NULL;
    int* odds = NULL;
    int* matching = NULL;
    EdgeNode** adj = NULL;
    int* tour = NULL;
    int* path = NULL;
    
    // 1. MST
    parent = prim_mst(dist, num_stations, degrees);
    if (cb) {
        int* mst_edges = malloc(2 * (num_stations - 1) * sizeof(int));
        int idx = 0;
        double mst_cost = 0.0;
        for (int i = 1; i < num_stations; i++) {
            mst_edges[idx++] = i;
            mst_edges[idx++] = parent[i];
            mst_cost += dist[i][parent[i]];
        }
        if (cb(4, mst_edges, idx, mst_cost)) { free(mst_edges); goto cleanup_all; }
        free(mst_edges);
    }
    
    // 2. Odd vertices
    int num_odds = 0;
    odds = get_odd_vertices(degrees, num_stations, &num_odds);
    
    // 3. MWPM
    matching = get_mwpm(odds, num_odds, dist);
    if (cb) {
        int* mwpm_edges = malloc(num_odds * sizeof(int));
        int idx = 0;
        int* matched_visited = calloc(num_odds, sizeof(int));
        double mwpm_cost = 0.0;
        for (int i = 0; i < num_odds; i++) {
            if (!matched_visited[i]) {
                mwpm_edges[idx++] = odds[i];
                mwpm_edges[idx++] = odds[matching[i]];
                mwpm_cost += dist[odds[i]][odds[matching[i]]];
                matched_visited[i] = 1;
                matched_visited[matching[i]] = 1;
            }
        }
        if (cb(5, mwpm_edges, idx, mwpm_cost)) { free(mwpm_edges); free(matched_visited); goto cleanup_all; }
        free(mwpm_edges);
        free(matched_visited);
    }
    
    // 4. Multigraph
    adj = build_multigraph(num_stations, parent, odds, num_odds, matching);
    
    // 5. Eulerian Tour
    int max_tour_len = 2 * num_stations; // Upper bound
    tour = malloc(max_tour_len * sizeof(int));
    int tour_idx = 0;
    eulerian_tour(adj, 0, tour, &tour_idx);
    
    // 6. Hamiltonian Cycle
    path = get_hamiltonian(tour, tour_idx, num_stations);
    
    // Calculate cost
    double total_cost = 0;
    for (int i = 0; i < num_stations - 1; i++) {
        total_cost += dist[path[i]][path[i+1]];
    }
    total_cost += dist[path[num_stations-1]][path[0]];
    
    if (cb) cb(2, path, num_stations, total_cost);

cleanup_all:
    // Always fire Done — even on early abort — so Python can unlock the UI.
    if (cb) cb(3, NULL, 0, 0);
    if (adj) {
        for (int i = 0; i < num_stations; i++) {
            EdgeNode* edge = adj[i];
            while (edge != NULL) {
                EdgeNode* tmp = edge;
                edge = edge->next;
                free(tmp);
            }
        }
        free(adj);
    }
    if (path) free(path);
    if (tour) free(tour);
    if (matching) free(matching);
    if (odds) free(odds);
    if (parent) free(parent);
    if (degrees) free(degrees);
    if (dist) {
        for (int i = 0; i < num_stations; i++) free(dist[i]);
        free(dist);
    }
}

// ---------------------------------------------------------
// 3. NEAREST NEIGHBOR ALGORITHM (formerly called Greedy)
// ---------------------------------------------------------
void tsp_nearest_neighbor(BusStation* stations, int num_stations, TspVizCallback cb) {
    reset_tsp_comparison_count();
    if (num_stations <= 1) {
        if (cb) cb(3, NULL, 0, 0);
        return;
    }

    int* path = malloc(sizeof(int) * num_stations);
    int* visited = calloc(num_stations, sizeof(int));
    double total_cost = 0;
    int aborted = 0;

    int current_node = 0;
    path[0] = 0;
    visited[0] = 1;

    for (int step = 1; step < num_stations && !aborted; step++) {
        double min_dist = DBL_MAX;
        int next_node = -1;

        for (int i = 0; i < num_stations && !aborted; i++) {
            if (!visited[i]) {
                double dist = get_dist(stations[current_node], stations[i]);
                
                path[step] = i;
                if (cb && cb(1, path, step + 1, total_cost + dist)) { aborted = 1; break; }

                tsp_comparison_count++;
                if (dist < min_dist) {
                    min_dist = dist;
                    next_node = i;
                }
            }
        }

        if (!aborted && next_node != -1) {
            path[step] = next_node;
            visited[next_node] = 1;
            total_cost += min_dist;
            current_node = next_node;
            
            if (cb && cb(2, path, step + 1, total_cost)) aborted = 1;
        }
    }

    if (!aborted) {
        // Complete cycle
        total_cost += get_dist(stations[current_node], stations[0]);
        if (cb) cb(2, path, num_stations, total_cost);
    }
    
    // Always send Done — even after abort — so Python can unlock the UI.
    if (cb) cb(3, NULL, 0, 0);

    free(path);
    free(visited);
}

// ---------------------------------------------------------
// 4. REAL GREEDY ALGORITHM (Edge Insertion)
// ---------------------------------------------------------
typedef struct Edge {
    int u;
    int v;
    double weight;
} Edge;

static int compare_edges(const void* a, const void* b) {
    tsp_comparison_count++;
    double wa = ((Edge*)a)->weight;
    double wb = ((Edge*)b)->weight;
    if (wa < wb) return -1;
    if (wa > wb) return 1;
    return 0;
}

static int find_set(int i, int* parent) {
    if (parent[i] == i)
        return i;
    return parent[i] = find_set(parent[i], parent);
}

static void union_sets(int i, int j, int* parent) {
    int root_i = find_set(i, parent);
    int root_j = find_set(j, parent);
    if (root_i != root_j) {
        parent[root_i] = root_j;
    }
}

void tsp_greedy(BusStation* stations, int num_stations, TspVizCallback cb) {
    reset_tsp_comparison_count();
    if (num_stations <= 1) {
        if (cb) cb(3, NULL, 0, 0);
        return;
    }

    int num_edges = num_stations * (num_stations - 1) / 2;
    Edge* edges = malloc(num_edges * sizeof(Edge));
    int edge_idx = 0;
    for (int i = 0; i < num_stations; i++) {
        for (int j = i + 1; j < num_stations; j++) {
            edges[edge_idx].u = i;
            edges[edge_idx].v = j;
            edges[edge_idx].weight = get_dist(stations[i], stations[j]);
            edge_idx++;
        }
    }

    qsort(edges, num_edges, sizeof(Edge), compare_edges);

    int* parent = malloc(num_stations * sizeof(int));
    for (int i = 0; i < num_stations; i++) parent[i] = i;

    int* degrees = calloc(num_stations, sizeof(int));
    
    int* neighbor1 = malloc(num_stations * sizeof(int));
    int* neighbor2 = malloc(num_stations * sizeof(int));
    for(int i = 0; i < num_stations; i++) {
        neighbor1[i] = -1;
        neighbor2[i] = -1;
    }

    int selected_count = 0;
    double total_cost = 0;
    int aborted = 0;

    // Packed pairs for visualization (event 6)
    int* viz_edges = malloc(2 * num_stations * sizeof(int));

    for (int i = 0; i < num_edges && selected_count < num_stations && !aborted; i++) {
        int u = edges[i].u;
        int v = edges[i].v;
        double w = edges[i].weight;

        // Rule 1: No vertex should have degree >= 2
        if (degrees[u] >= 2 || degrees[v] >= 2) continue;

        // Rule 2: No premature cycle (cycle of length < num_stations)
        int root_u = find_set(u, parent);
        int root_v = find_set(v, parent);
        if (root_u == root_v && selected_count < num_stations - 1) continue;

        // Accept the edge!
        union_sets(u, v, parent);
        degrees[u]++;
        degrees[v]++;

        if (neighbor1[u] == -1) neighbor1[u] = v;
        else neighbor2[u] = v;

        if (neighbor1[v] == -1) neighbor1[v] = u;
        else neighbor2[v] = u;

        viz_edges[2 * selected_count] = u;
        viz_edges[2 * selected_count + 1] = v;
        selected_count++;
        total_cost += w;

        // Emit current selected edges for visualization
        if (cb && cb(6, viz_edges, 2 * selected_count, total_cost)) {
            aborted = 1;
            break;
        }
    }

    if (!aborted && selected_count == num_stations) {
        // Reconstruct full cycle path starting at node 0
        int* final_path = malloc(num_stations * sizeof(int));
        int curr = 0;
        int prev = -1;
        for (int step = 0; step < num_stations; step++) {
            final_path[step] = curr;
            int next = -1;
            if (neighbor1[curr] != prev) next = neighbor1[curr];
            else next = neighbor2[curr];
            prev = curr;
            curr = next;
        }

        if (cb) cb(2, final_path, num_stations, total_cost);
        free(final_path);
    }

    if (cb) cb(3, NULL, 0, 0);

    free(viz_edges);
    free(neighbor1);
    free(neighbor2);
    free(degrees);
    free(parent);
    free(edges);
}

// Calculates the MST on V \ {excluded} using Prim's.
int mst_excluding(double** dist, int n, int excluded, int* parent, double* mst_weight) {
    if (n <= 1) return 1;
    double* key = malloc(n * sizeof(double));
    int* in_mst = calloc(n, sizeof(int));
    
    for (int i = 0; i < n; i++) {
        key[i] = DBL_MAX;
        parent[i] = -1;
    }
    
    int start_node = (excluded == 0) ? 1 : 0;
    key[start_node] = 0;
    
    for (int count = 0; count < n - 1; count++) {
        double min = DBL_MAX;
        int u = -1;
        for (int v = 0; v < n; v++) {
            if (v == excluded) continue;
            tsp_comparison_count++;
            if (!in_mst[v] && key[v] < min) {
                min = key[v];
                u = v;
            }
        }
        
        if (u == -1) break;
        
        in_mst[u] = 1;
        
        for (int v = 0; v < n; v++) {
            if (v == excluded) continue;
            tsp_comparison_count++;
            if (dist[u][v] > 0 && !in_mst[v] && dist[u][v] < key[v]) {
                parent[v] = u;
                key[v] = dist[u][v];
            }
        }
    }
    
    double total = 0.0;
    for (int i = 0; i < n; i++) {
        if (i == excluded || i == start_node) continue;
        if (parent[i] == -1) {
            free(key);
            free(in_mst);
            return 1;
        }
        total += dist[i][parent[i]];
    }
    
    *mst_weight = total;
    free(key);
    free(in_mst);
    return 0;
}

// Finds the two cheapest edges incident to the excluded vertex
int find_two_cheapest_edges(double** dist, int n, int excluded, int* cheapest1, int* cheapest2, double* edge_cost) {
    double min1 = DBL_MAX;
    double min2 = DBL_MAX;
    int idx1 = -1;
    int idx2 = -1;
    
    for (int j = 0; j < n; j++) {
        if (j == excluded) continue;
        double d = dist[excluded][j];
        if (d <= 0) continue;
        
        tsp_comparison_count++;
        if (d < min1) {
            min2 = min1;
            idx2 = idx1;
            min1 = d;
            idx1 = j;
        } else if (d < min2) {
            min2 = d;
            idx2 = j;
        }
    }
    
    if (idx1 == -1 || idx2 == -1) {
        return 1;
    }
    
    *cheapest1 = idx1;
    *cheapest2 = idx2;
    *edge_cost = min1 + min2;
    return 0;
}

// Computes the maximum 1-tree lower bound by evaluating 1-trees centered at each node.
void tsp_max_1_tree(BusStation* stations, int num_stations, TspVizCallback cb) {
    if (num_stations < 3) return;
    
    reset_tsp_comparison_count();
    
    double** dist = malloc(num_stations * sizeof(double*));
    for (int i = 0; i < num_stations; i++) {
        dist[i] = malloc(num_stations * sizeof(double));
        for (int j = 0; j < num_stations; j++) {
            double dx = stations[i].x - stations[j].x;
            double dy = stations[i].y - stations[j].y;
            dist[i][j] = sqrt(dx*dx + dy*dy);
        }
    }
    
    int* best_edges = malloc(2 * num_stations * sizeof(int));
    double max_lower_bound = -1.0;
    
    int* temp_parent = malloc(num_stations * sizeof(int));
    int* current_edges = malloc(2 * num_stations * sizeof(int));
    
    for (int v = 0; v < num_stations; v++) {
        double mst_weight = 0.0;
        if (mst_excluding(dist, num_stations, v, temp_parent, &mst_weight) != 0) {
            continue;
        }
        
        int cheapest1 = -1, cheapest2 = -1;
        double edge_cost = 0.0;
        if (find_two_cheapest_edges(dist, num_stations, v, &cheapest1, &cheapest2, &edge_cost) != 0) {
            continue;
        }
        
        double current_1_tree_cost = mst_weight + edge_cost;
        
        int idx = 0;
        current_edges[idx++] = v;
        current_edges[idx++] = cheapest1;
        current_edges[idx++] = v;
        current_edges[idx++] = cheapest2;
        
        int start_node = (v == 0) ? 1 : 0;
        for (int i = 0; i < num_stations; i++) {
            if (i == v || i == start_node) continue;
            current_edges[idx++] = i;
            current_edges[idx++] = temp_parent[i];
        }
        
        if (cb && cb(7, current_edges, idx, current_1_tree_cost)) {
            goto cleanup;
        }
        
        if (current_1_tree_cost > max_lower_bound) {
            max_lower_bound = current_1_tree_cost;
            memcpy(best_edges, current_edges, 2 * num_stations * sizeof(int));
        }
    }
    
    if (max_lower_bound > 0 && cb) {
        cb(8, best_edges, 2 * num_stations, max_lower_bound);
    }
    
cleanup:
    free(temp_parent);
    free(current_edges);
    free(best_edges);
    for (int i = 0; i < num_stations; i++) {
        free(dist[i]);
    }
    free(dist);
}


