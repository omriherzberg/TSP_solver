#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <float.h>
#include "tsp_solver.h"

#define DIST(i, j) dist_matrix[(i) * num_stations + (j)]

// ---------------------------------------------------------
// 1. NEAREST NEIGHBOR ALGORITHM
// ---------------------------------------------------------
void efal_nearest_neighbor(double* dist_matrix, int num_stations, int* out_path, double* out_cost, TspVizCallback cb) {
    if (num_stations <= 0) return;
    if (num_stations == 1) {
        out_path[0] = 0;
        *out_cost = 0;
        return;
    }

    int* visited = calloc(num_stations, sizeof(int));
    double total_cost = 0;
    
    int current_node = 0;
    out_path[0] = 0;
    visited[0] = 1;

    for (int step = 1; step < num_stations; step++) {
        double min_dist = DBL_MAX;
        int next_node = -1;

        for (int i = 0; i < num_stations; i++) {
            if (!visited[i]) {
                double d = DIST(current_node, i);
                if (d < min_dist) {
                    min_dist = d;
                    next_node = i;
                }
            }
        }

        if (next_node != -1) {
            out_path[step] = next_node;
            visited[next_node] = 1;
            total_cost += min_dist;
            
            if (cb) {
                int edge[2] = {current_node, next_node};
                if (cb(2, edge, 2, total_cost) == 1) { free(visited); return; }
            }
            
            current_node = next_node;
        }
    }
    
    // Complete cycle
    total_cost += DIST(current_node, out_path[0]);
    *out_cost = total_cost;

    free(visited);
}

// ---------------------------------------------------------
// 2. GREEDY (EDGE INSERTION) ALGORITHM
// ---------------------------------------------------------
typedef struct {
    int u;
    int v;
    double weight;
} Edge;

static int compare_edges(const void* a, const void* b) {
    double wa = ((Edge*)a)->weight;
    double wb = ((Edge*)b)->weight;
    if (wa < wb) return -1;
    if (wa > wb) return 1;
    return 0;
}

static int find_set(int i, int* parent) {
    if (parent[i] == i) return i;
    return parent[i] = find_set(parent[i], parent);
}

static void union_sets(int i, int j, int* parent) {
    int root_i = find_set(i, parent);
    int root_j = find_set(j, parent);
    if (root_i != root_j) parent[root_i] = root_j;
}

void efal_greedy(double* dist_matrix, int num_stations, int* out_path, double* out_cost, TspVizCallback cb) {
    if (num_stations <= 0) return;
    if (num_stations == 1) {
        out_path[0] = 0;
        *out_cost = 0;
        return;
    }

    int num_edges = num_stations * (num_stations - 1) / 2;
    Edge* edges = malloc(num_edges * sizeof(Edge));
    int edge_idx = 0;
    for (int i = 0; i < num_stations; i++) {
        for (int j = i + 1; j < num_stations; j++) {
            edges[edge_idx].u = i;
            edges[edge_idx].v = j;
            edges[edge_idx].weight = DIST(i, j);
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

    for (int i = 0; i < num_edges && selected_count < num_stations; i++) {
        int u = edges[i].u;
        int v = edges[i].v;
        double w = edges[i].weight;

        if (degrees[u] >= 2 || degrees[v] >= 2) continue;

        int root_u = find_set(u, parent);
        int root_v = find_set(v, parent);
        if (root_u == root_v && selected_count < num_stations - 1) continue;

        union_sets(u, v, parent);
        degrees[u]++;
        degrees[v]++;

        if (neighbor1[u] == -1) neighbor1[u] = v; else neighbor2[u] = v;
        if (neighbor1[v] == -1) neighbor1[v] = u; else neighbor2[v] = u;

        selected_count++;
        total_cost += w;
        
        if (cb) {
            int edge[2] = {u, v};
            if (cb(2, edge, 2, total_cost) == 1) {
                free(neighbor1); free(neighbor2); free(degrees); free(parent); free(edges);
                return;
            }
        }
    }

    if (selected_count == num_stations) {
        int curr = 0;
        int prev = -1;
        for (int step = 0; step < num_stations; step++) {
            out_path[step] = curr;
            int next = -1;
            if (neighbor1[curr] != prev) next = neighbor1[curr];
            else next = neighbor2[curr];
            prev = curr;
            curr = next;
        }
        *out_cost = total_cost;
    }

    free(neighbor1);
    free(neighbor2);
    free(degrees);
    free(parent);
    free(edges);
}

// ---------------------------------------------------------
// 3. BRUTE FORCE EXACT SOLVER
// ---------------------------------------------------------
int efal_bf_recursive(double* dist_matrix, int num_stations, int* current_path, int depth, int* visited, double current_cost, int* best_path, double* min_cost, TspVizCallback cb) {
    if (depth == num_stations) {
        double total_cost = current_cost + DIST(current_path[num_stations-1], current_path[0]);
        if (total_cost < *min_cost) {
            *min_cost = total_cost;
            for(int i = 0; i < num_stations; i++) best_path[i] = current_path[i];
        }
        return 0;
    }

    for (int i = 1; i < num_stations; i++) {
        if (!visited[i]) {
            visited[i] = 1;
            current_path[depth] = i;
            double cost_added = DIST(current_path[depth-1], i);
            if (cb) {
                if (cb(1, current_path, depth + 1, current_cost + cost_added) == 1) return 1;
            }
            if (efal_bf_recursive(dist_matrix, num_stations, current_path, depth + 1, visited, current_cost + cost_added, best_path, min_cost, cb) == 1) return 1;
            visited[i] = 0;
        }
    }
    return 0;
}

void efal_brute_force(double* dist_matrix, int num_stations, int* out_path, double* out_cost, TspVizCallback cb) {
    if (num_stations <= 0) return;
    if (num_stations == 1) {
        out_path[0] = 0;
        *out_cost = 0;
        return;
    }

    int* current_path = malloc(sizeof(int) * num_stations);
    int* visited = calloc(num_stations, sizeof(int));
    
    current_path[0] = 0;
    visited[0] = 1;
    double min_cost = DBL_MAX;
    
    efal_bf_recursive(dist_matrix, num_stations, current_path, 1, visited, 0.0, out_path, &min_cost, cb);
    
    *out_cost = min_cost;
    
    free(current_path);
    free(visited);
}

// ---------------------------------------------------------
// 4. CHRISTOFIDES ALGORITHM
// ---------------------------------------------------------
static int* efal_prim_mst(double* dist_matrix, int n, int* degrees) {
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
            if (!in_mst[v] && key[v] < min) {
                min = key[v];
                u = v;
            }
        }
        in_mst[u] = 1;
        
        for (int v = 0; v < n; v++) {
            double d = dist_matrix[u * n + v];
            if (d > 0 && !in_mst[v] && d < key[v]) {
                parent[v] = u;
                key[v] = d;
            }
        }
    }
    
    for (int i = 1; i < n; i++) {
        degrees[i]++;
        degrees[parent[i]]++;
    }
    
    free(key);
    free(in_mst);
    return parent;
}

static int* efal_get_odd_vertices(int* degrees, int n, int* num_odds) {
    int* odds = malloc(n * sizeof(int));
    *num_odds = 0;
    for (int i = 0; i < n; i++) {
        if (degrees[i] % 2 != 0) odds[(*num_odds)++] = i;
    }
    return odds;
}

static int* efal_get_mwpm(int* odds, int num_odds, double* dist_matrix, int n) {
    int* matching = malloc(num_odds * sizeof(int));
    int* matched = calloc(num_odds, sizeof(int));
    for (int i = 0; i < num_odds; i++) matching[i] = -1;
    
    for (int i = 0; i < num_odds; i++) {
        if (matched[i]) continue;
        int best_j = -1;
        double min_dist = DBL_MAX;
        
        for (int j = i + 1; j < num_odds; j++) {
            if (!matched[j]) {
                double d = dist_matrix[odds[i] * n + odds[j]];
                if (d < min_dist) {
                    min_dist = d;
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

typedef struct EfalEdgeNode {
    int to;
    int used;
    struct EfalEdgeNode* next;
} EfalEdgeNode;

static void efal_add_edge(EfalEdgeNode** adj, int u, int v) {
    EfalEdgeNode* node1 = malloc(sizeof(EfalEdgeNode));
    node1->to = v; node1->used = 0; node1->next = adj[u]; adj[u] = node1;
    
    EfalEdgeNode* node2 = malloc(sizeof(EfalEdgeNode));
    node2->to = u; node2->used = 0; node2->next = adj[v]; adj[v] = node2;
}

static void efal_eulerian_tour(EfalEdgeNode** adj, int u, int* tour, int* tour_idx) {
    EfalEdgeNode* edge = adj[u];
    while (edge != NULL) {
        if (!edge->used) {
            edge->used = 1;
            EfalEdgeNode* rev = adj[edge->to];
            while (rev != NULL) {
                if (rev->to == u && !rev->used) {
                    rev->used = 1;
                    break;
                }
                rev = rev->next;
            }
            efal_eulerian_tour(adj, edge->to, tour, tour_idx);
        }
        edge = edge->next;
    }
    tour[(*tour_idx)++] = u;
}

void efal_christofides(double* dist_matrix, int num_stations, int* out_path, double* out_cost, TspVizCallback cb) {
    if (num_stations <= 1) {
        if (num_stations == 1) {
            out_path[0] = 0;
            *out_cost = 0;
        }
        return;
    }

    int* degrees = calloc(num_stations, sizeof(int));
    int* parent = efal_prim_mst(dist_matrix, num_stations, degrees);
    
    if (cb) {
        int* mst_edges = malloc(2 * num_stations * sizeof(int));
        int edge_idx = 0;
        double mst_cost = 0;
        for (int i = 1; i < num_stations; i++) {
            mst_edges[edge_idx++] = parent[i];
            mst_edges[edge_idx++] = i;
            mst_cost += dist_matrix[parent[i] * num_stations + i];
        }
        if (cb(4, mst_edges, edge_idx, mst_cost) == 1) {
            free(mst_edges); free(parent); free(degrees); return;
        }
        free(mst_edges);
    }
    
    int num_odds = 0;
    int* odds = efal_get_odd_vertices(degrees, num_stations, &num_odds);
    
    int* matching = efal_get_mwpm(odds, num_odds, dist_matrix, num_stations);
    
    if (cb) {
        int* matching_edges = malloc(num_odds * sizeof(int));
        int edge_idx = 0;
        double matching_cost = 0;
        int* matched_vis = calloc(num_odds, sizeof(int));
        for (int i = 0; i < num_odds; i++) {
            if (!matched_vis[i]) {
                matching_edges[edge_idx++] = odds[i];
                matching_edges[edge_idx++] = odds[matching[i]];
                matching_cost += dist_matrix[odds[i] * num_stations + odds[matching[i]]];
                matched_vis[i] = 1;
                matched_vis[matching[i]] = 1;
            }
        }
        free(matched_vis);
        if (cb(5, matching_edges, edge_idx, matching_cost) == 1) {
            free(matching_edges); free(matching); free(odds); free(parent); free(degrees); return;
        }
        free(matching_edges);
    }
    
    EfalEdgeNode** adj = calloc(num_stations, sizeof(EfalEdgeNode*));
    for (int i = 1; i < num_stations; i++) efal_add_edge(adj, i, parent[i]);
    
    int* matched_visited = calloc(num_odds, sizeof(int));
    for (int i = 0; i < num_odds; i++) {
        if (!matched_visited[i]) {
            int u = odds[i];
            int v = odds[matching[i]];
            efal_add_edge(adj, u, v);
            matched_visited[i] = 1;
            matched_visited[matching[i]] = 1;
        }
    }
    free(matched_visited);
    
    int max_tour_len = 2 * num_stations;
    int* tour = malloc(max_tour_len * sizeof(int));
    int tour_idx = 0;
    efal_eulerian_tour(adj, 0, tour, &tour_idx);
    
    int* visited = calloc(num_stations, sizeof(int));
    int idx = 0;
    for (int i = tour_idx - 1; i >= 0; i--) {
        int u = tour[i];
        if (!visited[u]) {
            visited[u] = 1;
            out_path[idx++] = u;
        }
    }
    free(visited);
    
    double total_cost = 0;
    for (int i = 0; i < num_stations - 1; i++) total_cost += dist_matrix[out_path[i] * num_stations + out_path[i+1]];
    total_cost += dist_matrix[out_path[num_stations-1] * num_stations + out_path[0]];
    *out_cost = total_cost;

    for (int i = 0; i < num_stations; i++) {
        EfalEdgeNode* edge = adj[i];
        while (edge != NULL) {
            EfalEdgeNode* tmp = edge;
            edge = edge->next;
            free(tmp);
        }
    }
    free(adj);
    free(tour);
    free(matching);
    free(odds);
    free(parent);
    free(degrees);
}
