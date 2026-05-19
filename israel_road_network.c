
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_ISRAEL_VERTICES 34
#define NUM_ISRAEL_CITIES 22
#define INF 1e9

double road_dist[NUM_ISRAEL_VERTICES][NUM_ISRAEL_VERTICES];
double road_time[NUM_ISRAEL_VERTICES][NUM_ISRAEL_VERTICES];

void init_israel_road_network() {
    for (int i = 0; i < NUM_ISRAEL_VERTICES; i++) {
        for (int j = 0; j < NUM_ISRAEL_VERTICES; j++) {
            if (i == j) {
                road_dist[i][j] = 0.0;
                road_time[i][j] = 0.0;
            } else {
                road_dist[i][j] = INF;
                road_time[i][j] = INF;
            }
        }
    }
    
    road_dist[11][2] = 35.0; road_dist[2][11] = 35.0;
    road_time[11][2] = 30.0; road_time[2][11] = 30.0;
    road_dist[2][7] = 45.0; road_dist[7][2] = 45.0;
    road_time[2][7] = 40.0; road_time[7][2] = 40.0;
    road_dist[7][19] = 30.0; road_dist[19][7] = 30.0;
    road_time[7][19] = 25.0; road_time[19][7] = 25.0;
    road_dist[19][9] = 30.0; road_dist[9][19] = 30.0;
    road_time[19][9] = 20.0; road_time[9][19] = 20.0;
    road_dist[19][18] = 10.0; road_dist[18][19] = 10.0;
    road_time[19][18] = 15.0; road_time[18][19] = 15.0;
    road_dist[11][18] = 45.0; road_dist[18][11] = 45.0;
    road_time[11][18] = 50.0; road_time[18][11] = 50.0;
    road_dist[28][5] = 15.0; road_dist[5][28] = 15.0;
    road_time[28][5] = 15.0; road_time[5][28] = 15.0;
    road_dist[2][28] = 50.0; road_dist[28][2] = 50.0;
    road_time[2][28] = 45.0; road_time[28][2] = 45.0;
    road_dist[19][5] = 25.0; road_dist[5][19] = 25.0;
    road_time[19][5] = 25.0; road_time[5][19] = 25.0;
    road_dist[28][19] = 35.0; road_dist[19][28] = 35.0;
    road_time[28][19] = 30.0; road_time[19][28] = 30.0;
    road_dist[5][20] = 40.0; road_dist[20][5] = 40.0;
    road_time[5][20] = 45.0; road_time[20][5] = 45.0;
    road_dist[20][9] = 45.0; road_dist[9][20] = 45.0;
    road_time[20][9] = 50.0; road_time[9][20] = 50.0;
    road_dist[19][20] = 25.0; road_dist[20][19] = 25.0;
    road_time[19][20] = 30.0; road_time[20][19] = 30.0;
    road_dist[6][15] = 15.0; road_dist[15][6] = 15.0;
    road_time[6][15] = 20.0; road_time[15][6] = 20.0;
    road_dist[6][28] = 20.0; road_dist[28][6] = 20.0;
    road_time[6][28] = 20.0; road_time[28][6] = 20.0;
    road_dist[2][10] = 60.0; road_dist[10][2] = 60.0;
    road_time[2][10] = 45.0; road_time[10][2] = 45.0;
    road_dist[10][22] = 25.0; road_dist[22][10] = 25.0;
    road_time[10][22] = 20.0; road_time[22][10] = 20.0;
    road_dist[22][0] = 10.0; road_dist[0][22] = 10.0;
    road_time[22][0] = 15.0; road_time[0][22] = 15.0;
    road_dist[32][25] = 15.0; road_dist[25][32] = 15.0;
    road_time[32][25] = 10.0; road_time[25][32] = 10.0;
    road_dist[25][31] = 25.0; road_dist[31][25] = 25.0;
    road_time[25][31] = 20.0; road_time[31][25] = 20.0;
    road_dist[31][15] = 15.0; road_dist[15][31] = 15.0;
    road_time[31][15] = 15.0; road_time[15][31] = 15.0;
    road_dist[15][28] = 30.0; road_dist[28][15] = 30.0;
    road_time[15][28] = 25.0; road_time[28][15] = 25.0;
    road_dist[15][29] = 25.0; road_dist[29][15] = 25.0;
    road_time[15][29] = 25.0; road_time[29][15] = 25.0;
    road_dist[2][32] = 40.0; road_dist[32][2] = 40.0;
    road_time[2][32] = 30.0; road_time[32][2] = 30.0;
    road_dist[32][10] = 20.0; road_dist[10][32] = 20.0;
    road_time[32][10] = 15.0; road_time[10][32] = 15.0;
    road_dist[0][23] = 40.0; road_dist[23][0] = 40.0;
    road_time[0][23] = 35.0; road_time[23][0] = 35.0;
    road_dist[23][1] = 30.0; road_dist[1][23] = 30.0;
    road_time[23][1] = 30.0; road_time[1][23] = 30.0;
    road_dist[12][23] = 15.0; road_dist[23][12] = 15.0;
    road_time[12][23] = 15.0; road_time[23][12] = 15.0;
    road_dist[13][23] = 15.0; road_dist[23][13] = 15.0;
    road_time[13][23] = 15.0; road_time[23][13] = 15.0;
    road_dist[12][0] = 35.0; road_dist[0][12] = 35.0;
    road_time[12][0] = 35.0; road_time[0][12] = 35.0;
    road_dist[24][0] = 20.0; road_dist[0][24] = 20.0;
    road_time[24][0] = 20.0; road_time[0][24] = 20.0;
    road_dist[0][8] = 40.0; road_dist[8][0] = 40.0;
    road_time[0][8] = 35.0; road_time[8][0] = 35.0;
    road_dist[8][16] = 20.0; road_dist[16][8] = 20.0;
    road_time[8][16] = 20.0; road_time[16][8] = 20.0;
    road_dist[16][21] = 30.0; road_dist[21][16] = 30.0;
    road_time[16][21] = 25.0; road_time[21][16] = 25.0;
    road_dist[21][3] = 35.0; road_dist[3][21] = 35.0;
    road_time[21][3] = 30.0; road_time[3][21] = 30.0;
    road_dist[16][17] = 25.0; road_dist[17][16] = 25.0;
    road_time[16][17] = 25.0; road_time[17][16] = 25.0;
    road_dist[17][30] = 20.0; road_dist[30][17] = 20.0;
    road_time[17][30] = 15.0; road_time[30][17] = 15.0;
    road_dist[24][30] = 35.0; road_dist[30][24] = 35.0;
    road_time[24][30] = 25.0; road_time[30][24] = 25.0;
    road_dist[30][26] = 40.0; road_dist[26][30] = 40.0;
    road_time[30][26] = 25.0; road_time[26][30] = 25.0;
    road_dist[26][3] = 25.0; road_dist[3][26] = 25.0;
    road_time[26][3] = 20.0; road_time[3][26] = 20.0;
    road_dist[3][14] = 45.0; road_dist[14][3] = 45.0;
    road_time[3][14] = 40.0; road_time[14][3] = 40.0;
    road_dist[14][33] = 25.0; road_dist[33][14] = 25.0;
    road_time[14][33] = 25.0; road_time[33][14] = 25.0;
    road_dist[8][30] = 20.0; road_dist[30][8] = 20.0;
    road_time[8][30] = 20.0; road_time[30][8] = 20.0;
    road_dist[10][24] = 30.0; road_dist[24][10] = 30.0;
    road_time[10][24] = 25.0; road_time[24][10] = 25.0;
    road_dist[25][24] = 45.0; road_dist[24][25] = 45.0;
    road_time[25][24] = 30.0; road_time[24][25] = 30.0;
    road_dist[5][29] = 40.0; road_dist[29][5] = 40.0;
    road_time[5][29] = 35.0; road_time[29][5] = 35.0;
    road_dist[29][33] = 130.0; road_dist[33][29] = 130.0;
    road_time[29][33] = 110.0; road_time[33][29] = 110.0;
    road_dist[33][27] = 40.0; road_dist[27][33] = 40.0;
    road_time[33][27] = 30.0; road_time[27][33] = 30.0;
    road_dist[3][27] = 110.0; road_dist[27][3] = 110.0;
    road_time[3][27] = 80.0; road_time[27][3] = 80.0;
    road_dist[27][4] = 120.0; road_dist[4][27] = 120.0;
    road_time[27][4] = 90.0; road_time[4][27] = 90.0;
}


void run_dijkstra(int source, int use_time_metric, double* shortest_paths, int* prev_nodes) {
    int visited[NUM_ISRAEL_VERTICES];
    for (int i = 0; i < NUM_ISRAEL_VERTICES; i++) {
        shortest_paths[i] = INF;
        prev_nodes[i] = -1;
        visited[i] = 0;
    }
    
    shortest_paths[source] = 0.0;
    
    for (int count = 0; count < NUM_ISRAEL_VERTICES - 1; count++) {
        double min_dist = INF;
        int min_index = -1;
        
        for (int v = 0; v < NUM_ISRAEL_VERTICES; v++) {
            if (!visited[v] && shortest_paths[v] <= min_dist) {
                min_dist = shortest_paths[v];
                min_index = v;
            }
        }
        
        if (min_index == -1) break;
        visited[min_index] = 1;
        
        for (int v = 0; v < NUM_ISRAEL_VERTICES; v++) {
            double weight = use_time_metric ? road_time[min_index][v] : road_dist[min_index][v];
            if (!visited[v] && weight < INF && shortest_paths[min_index] != INF &&
                shortest_paths[min_index] + weight < shortest_paths[v]) {
                shortest_paths[v] = shortest_paths[min_index] + weight;
                prev_nodes[v] = min_index;
            }
        }
    }
}

// Global matrices for precomputed APSP
double apsp_dist[NUM_ISRAEL_CITIES][NUM_ISRAEL_CITIES];
double apsp_time[NUM_ISRAEL_CITIES][NUM_ISRAEL_CITIES];
int apsp_prev_dist[NUM_ISRAEL_CITIES][NUM_ISRAEL_VERTICES];
int apsp_prev_time[NUM_ISRAEL_CITIES][NUM_ISRAEL_VERTICES];

void precompute_all_pairs_shortest_paths() {
    init_israel_road_network();
    for (int i = 0; i < NUM_ISRAEL_CITIES; i++) {
        double shortest_paths_dist[NUM_ISRAEL_VERTICES];
        int prev_nodes_dist[NUM_ISRAEL_VERTICES];
        run_dijkstra(i, 0, shortest_paths_dist, prev_nodes_dist);
        for (int j = 0; j < NUM_ISRAEL_CITIES; j++) {
            apsp_dist[i][j] = shortest_paths_dist[j];
        }
        for (int v = 0; v < NUM_ISRAEL_VERTICES; v++) {
            apsp_prev_dist[i][v] = prev_nodes_dist[v];
        }
        
        double shortest_paths_time[NUM_ISRAEL_VERTICES];
        int prev_nodes_time[NUM_ISRAEL_VERTICES];
        run_dijkstra(i, 1, shortest_paths_time, prev_nodes_time);
        for (int j = 0; j < NUM_ISRAEL_CITIES; j++) {
            apsp_time[i][j] = shortest_paths_time[j];
        }
        for (int v = 0; v < NUM_ISRAEL_VERTICES; v++) {
            apsp_prev_time[i][v] = prev_nodes_time[v];
        }
    }
}

// ==========================================
// City coordinate table (canvas x,y for a 700x600 Israel map)
// ==========================================
static double city_x[34] = {
    320, 370, 265, 345, 340,   /* 0  Tel Aviv, 1  Jerusalem, 2  Haifa, 3  Beer Sheva, 4  Eilat */
    430, 355, 330, 260, 425,   /* 5  Tiberias, 6  Nazareth, 7  Karmiel, 8  Ashdod, 9  Kiryat Shmona */
    280, 230, 340, 315, 415,   /* 10 Netanya, 11 Nahariya, 12 Modiin, 13 Beit Shemesh, 14 Arad */
    365, 240, 280, 385, 400,   /* 15 Afula, 16 Ashkelon, 17 Kiryat Gat, 18 Safed, 19 Rosh Pinna */
    455, 220,                  /* 20 Katzrin, 21 Netivot */
    300, 345, 295, 290,        /* 22 Galilot, 23 Latrun, 24 Kesem, 25 Iron */
    340, 375, 370, 445,        /* 26 Beit Kama, 27 Arava, 28 Golani, 29 Beit Shean */
    280, 330, 270, 430         /* 30 Sorek, 31 Megiddo, 32 Hadera, 33 Neve Zohar */
};

static double city_y[34] = {
    290, 310, 165, 410, 570,   /* Tel Aviv, Jerusalem, Haifa, Beer Sheva, Eilat */
    195, 195, 160, 330, 105,   /* Tiberias, Nazareth, Karmiel, Ashdod, Kiryat Shmona */
    250, 135, 305, 325, 425,   /* Netanya, Nahariya, Modiin, Beit Shemesh, Arad */
    195, 360, 385, 145, 150,   /* Afula, Ashkelon, Kiryat Gat, Safed, Rosh Pinna */
    190, 400,                  /* Katzrin, Netivot */
    280, 308, 260, 185,        /* Galilot, Latrun, Kesem, Iron */
    400, 500, 195, 215,        /* Beit Kama, Arava, Golani, Beit Shean */
    350, 195, 228, 455         /* Sorek, Megiddo, Hadera, Neve Zohar */
};

static const char* city_names[34] = {
    "Tel Aviv", "Jerusalem", "Haifa", "Beer Sheva", "Eilat",
    "Tiberias", "Nazareth", "Karmiel", "Ashdod", "Kiryat Shmona",
    "Netanya", "Nahariya", "Modiin", "Beit Shemesh", "Arad",
    "Afula", "Ashkelon", "Kiryat Gat", "Safed", "Rosh Pinna",
    "Katzrin", "Netivot",
    "Galilot Junc", "Latrun Junc", "Kesem Junc", "Iron Junc",
    "Beit Kama Junc", "Arava Junc", "Golani Junc", "Beit Shean Junc",
    "Sorek Junc", "Megiddo Junc", "Hadera Junc", "Neve Zohar Junc"
};

// ==========================================
// Road graph edge list (for drawing background network)
// ==========================================
typedef struct { int u; int v; } RoadEdge;

static RoadEdge road_edges[] = {
    {11,2},{2,7},{7,19},{19,9},{19,18},{11,18},{28,5},{2,28},{19,5},{28,19},
    {5,20},{20,9},{19,20},{6,15},{6,28},{2,10},{10,22},{22,0},{32,25},{25,31},
    {31,15},{15,28},{15,29},{2,32},{32,10},{0,23},{23,1},{12,23},{13,23},{12,0},
    {24,0},{0,8},{8,16},{16,21},{21,3},{16,17},{17,30},{24,30},{30,26},{26,3},
    {3,14},{14,33},{8,30},{10,24},{25,24},{5,29},{29,33},{33,27},{3,27},{27,4}
};
static int num_road_edges = 50;

// ==========================================
// Exported FFI Functions
// ==========================================

void israel_init() {
    precompute_all_pairs_shortest_paths();
}

int israel_num_cities() { return NUM_ISRAEL_CITIES; }
int israel_num_vertices() { return NUM_ISRAEL_VERTICES; }

double israel_city_x(int idx) { return (idx >= 0 && idx < 34) ? city_x[idx] : 0; }
double israel_city_y(int idx) { return (idx >= 0 && idx < 34) ? city_y[idx] : 0; }

void israel_city_name(int idx, char* buf) {
    if (idx < 0 || idx >= 34) { buf[0] = 0; return; }
    int i = 0;
    while (city_names[idx][i]) { buf[i] = city_names[idx][i]; i++; }
    buf[i] = 0;
}

int israel_get_road_edges(int* edge_buf) {
    for (int i = 0; i < num_road_edges; i++) {
        edge_buf[2*i]   = road_edges[i].u;
        edge_buf[2*i+1] = road_edges[i].v;
    }
    return num_road_edges;
}

double israel_apsp_dist(int a, int b) {
    if (a < 0 || a >= NUM_ISRAEL_CITIES || b < 0 || b >= NUM_ISRAEL_CITIES) return -1.0;
    return apsp_dist[a][b];
}

double israel_apsp_time(int a, int b) {
    if (a < 0 || a >= NUM_ISRAEL_CITIES || b < 0 || b >= NUM_ISRAEL_CITIES) return -1.0;
    return apsp_time[a][b];
}

int israel_get_path(int city_a, int city_b, int use_time_metric, int* out_path) {
    int* prev = use_time_metric ? apsp_prev_time[city_a] : apsp_prev_dist[city_a];
    int stack[NUM_ISRAEL_VERTICES];
    int sp = 0;
    int cur = city_b;
    while (cur != -1 && cur != city_a && sp < NUM_ISRAEL_VERTICES) {
        stack[sp++] = cur;
        cur = prev[cur];
    }
    if (cur != city_a) {
        out_path[0] = city_a; out_path[1] = city_b; return 2;
    }
    out_path[0] = city_a;
    for (int i = sp - 1; i >= 0; i--) out_path[sp - i] = stack[i];
    return sp + 1;
}

#include "constants.h"

typedef int (*TspVizCallback)(int event_type, int* path_indices, int path_len, double current_dist);

double israel_tsp_nearest_neighbor(int start_city, int use_time_metric, int* out_tour, TspVizCallback cb) {
    int visited[NUM_ISRAEL_CITIES];
    for (int i = 0; i < NUM_ISRAEL_CITIES; i++) visited[i] = 0;
    out_tour[0] = start_city;
    visited[start_city] = 1;
    double total = 0.0;
    int cur = start_city;
    
    int viz_edges[NUM_ISRAEL_CITIES * 2];
    
    for (int step = 1; step < NUM_ISRAEL_CITIES; step++) {
        double best = INF; int best_city = -1;
        for (int j = 0; j < NUM_ISRAEL_CITIES; j++) {
            if (!visited[j]) {
                double d = use_time_metric ? apsp_time[cur][j] : apsp_dist[cur][j];
                if (d < best) { best = d; best_city = j; }
            }
        }
        out_tour[step] = best_city;
        visited[best_city] = 1;
        total += best;
        
        for (int i = 0; i < step; i++) {
            viz_edges[2*i] = out_tour[i];
            viz_edges[2*i+1] = out_tour[i+1];
        }
        if (cb && cb(EVENT_GREEDY_EDGES, viz_edges, 2 * step, total)) {
            if (cb) cb(EVENT_DONE, NULL, 0, 0);
            return total;
        }
        cur = best_city;
    }
    double final_d = use_time_metric ? apsp_time[cur][start_city] : apsp_dist[cur][start_city];
    total += final_d;
    
    viz_edges[2*(NUM_ISRAEL_CITIES-1)] = cur;
    viz_edges[2*(NUM_ISRAEL_CITIES-1)+1] = start_city;
    if (cb && cb(EVENT_GREEDY_EDGES, viz_edges, 2 * NUM_ISRAEL_CITIES, total)) {
        if (cb) cb(EVENT_DONE, NULL, 0, 0);
        return total;
    }
    
    if (cb) cb(EVENT_PATH_CONFIRMED, out_tour, NUM_ISRAEL_CITIES, total);
    if (cb) cb(EVENT_DONE, NULL, 0, 0);
    return total;
}

typedef struct { int u; int v; double w; } WEdge;
static int cmp_wedge(const void* a, const void* b) {
    double da = ((WEdge*)a)->w, db = ((WEdge*)b)->w;
    return (da > db) - (da < db);
}
static int gfind(int* par, int x) {
    while (par[x] != x) { par[x] = par[par[x]]; x = par[x]; } return x;
}

double israel_tsp_greedy(int use_time_metric, int* out_tour, TspVizCallback cb) {
    int N = NUM_ISRAEL_CITIES;
    int ne = N * (N-1) / 2;
    WEdge* edges = (WEdge*)malloc(ne * sizeof(WEdge));
    int idx = 0;
    for (int i = 0; i < N; i++)
        for (int j = i+1; j < N; j++) {
            edges[idx].u = i; edges[idx].v = j;
            edges[idx].w = use_time_metric ? apsp_time[i][j] : apsp_dist[i][j];
            idx++;
        }
    qsort(edges, ne, sizeof(WEdge), cmp_wedge);
    int degree[NUM_ISRAEL_CITIES], par[NUM_ISRAEL_CITIES], adj[NUM_ISRAEL_CITIES][2];
    for (int i = 0; i < N; i++) { degree[i]=0; par[i]=i; adj[i][0]=adj[i][1]=-1; }
    int added = 0; double total = 0.0;
    
    int* viz_edges = (int*)malloc(2 * N * sizeof(int));
    int aborted = 0;
    
    for (int e = 0; e < ne && added < N; e++) {
        int u = edges[e].u, v = edges[e].v;
        if (degree[u]>=2 || degree[v]>=2) continue;
        if (added < N-1 && gfind(par,u)==gfind(par,v)) continue;
        adj[u][degree[u]++]=v; adj[v][degree[v]++]=u;
        par[gfind(par,u)]=gfind(par,v);
        total += edges[e].w;
        
        viz_edges[2*added] = u;
        viz_edges[2*added+1] = v;
        added++;
        
        if (cb && cb(EVENT_GREEDY_EDGES, viz_edges, 2 * added, total)) {
            aborted = 1; break;
        }
    }
    free(edges);
    
    if (!aborted && added == N) {
        int vis[NUM_ISRAEL_CITIES]; for(int i=0;i<N;i++) vis[i]=0;
        int cur=0, pv=-1;
        for (int step=0; step<N; step++) {
            out_tour[step]=cur; vis[cur]=1;
            int nxt=-1;
            for (int k=0;k<2;k++)
                if (adj[cur][k]!=-1 && adj[cur][k]!=pv && !vis[adj[cur][k]])
                    { nxt=adj[cur][k]; break; }
            pv=cur; cur=(nxt==-1)?0:nxt;
        }
        if (cb) cb(EVENT_PATH_CONFIRMED, out_tour, N, total);
    }
    
    if (cb) cb(EVENT_DONE, NULL, 0, 0);
    free(viz_edges);
    return total;
}

double israel_tsp_2opt(int use_time_metric, int* tour, TspVizCallback cb) {
    int N = NUM_ISRAEL_CITIES;
    double cost = 0.0;
    for (int i=0;i<N;i++) {
        int u=tour[i], v=tour[(i+1)%N];
        cost += use_time_metric ? apsp_time[u][v] : apsp_dist[u][v];
    }
    
    if (cb && cb(EVENT_PATH_CONFIRMED, tour, N, cost)) {
        if (cb) cb(EVENT_DONE, NULL, 0, 0);
        return cost;
    }
    
    int improved = 1;
    int passes = 0;
    while (improved && passes < 1) {
        improved = 0;
        passes++;
        for (int i=0; i<N-1; i++) {
            for (int j=i+2; j<N; j++) {
                if (i==0 && j==N-1) continue;
                int u1=tour[i],v1=tour[i+1],u2=tour[j],v2=tour[(j+1)%N];
                double db = (use_time_metric ? apsp_time[u1][v1] : apsp_dist[u1][v1])
                          + (use_time_metric ? apsp_time[u2][v2] : apsp_dist[u2][v2]);
                double da = (use_time_metric ? apsp_time[u1][u2] : apsp_dist[u1][u2])
                          + (use_time_metric ? apsp_time[v1][v2] : apsp_dist[v1][v2]);
                if (da < db - 1e-9) {
                    int lo=i+1, hi=j;
                    while(lo<hi){int t=tour[lo];tour[lo]=tour[hi];tour[hi]=t;lo++;hi--;}
                    cost = cost - db + da;
                    improved = 1;
                    
                    if (cb && cb(EVENT_PATH_CONFIRMED, tour, N, cost)) {
                        if (cb) cb(EVENT_DONE, NULL, 0, 0);
                        return cost;
                    }
                }
            }
        }
    }
    if (cb) cb(EVENT_DONE, NULL, 0, 0);
    return cost;
}

double israel_tsp_christofides(int use_time_metric, int* out_tour, TspVizCallback cb) {
    int N = NUM_ISRAEL_CITIES;
    double (*W)[NUM_ISRAEL_CITIES] = use_time_metric ? apsp_time : apsp_dist;

    int mst_parent[NUM_ISRAEL_CITIES];
    double mst_key[NUM_ISRAEL_CITIES];
    int in_mst[NUM_ISRAEL_CITIES];
    for (int i = 0; i < N; i++) { mst_key[i] = INF; in_mst[i] = 0; mst_parent[i] = -1; }
    mst_key[0] = 0.0;
    double mst_cost = 0.0;
    for (int count = 0; count < N; count++) {
        int u = -1;
        for (int v = 0; v < N; v++)
            if (!in_mst[v] && (u == -1 || mst_key[v] < mst_key[u])) u = v;
        in_mst[u] = 1;
        if (mst_parent[u] != -1) mst_cost += W[u][mst_parent[u]];
        for (int v = 0; v < N; v++) {
            if (!in_mst[v] && W[u][v] < INF && W[u][v] < mst_key[v]) {
                mst_key[v] = W[u][v];
                mst_parent[v] = u;
            }
        }
    }

    int* mst_edges = malloc(2 * N * sizeof(int));
    int mst_edge_idx = 0;
    for (int v = 1; v < N; v++) {
        int u = mst_parent[v];
        if (u >= 0) {
            mst_edges[mst_edge_idx++] = u;
            mst_edges[mst_edge_idx++] = v;
        }
    }
    if (cb && cb(EVENT_MST_CONFIRMED, mst_edges, mst_edge_idx, mst_cost)) {
        free(mst_edges);
        if (cb) cb(EVENT_DONE, NULL, 0, 0);
        return 0.0;
    }

    int multi[NUM_ISRAEL_CITIES][NUM_ISRAEL_CITIES];
    int mst_deg[NUM_ISRAEL_CITIES];
    for (int i = 0; i < N; i++) { mst_deg[i] = 0; for (int j = 0; j < N; j++) multi[i][j] = 0; }
    for (int v = 1; v < N; v++) {
        int u = mst_parent[v];
        if (u >= 0) { multi[u][v]++; multi[v][u]++; mst_deg[u]++; mst_deg[v]++; }
    }

    int odd[NUM_ISRAEL_CITIES]; int n_odd = 0;
    for (int v = 0; v < N; v++) if (mst_deg[v] % 2 == 1) odd[n_odd++] = v;

    int matched[NUM_ISRAEL_CITIES];
    for (int i = 0; i < N; i++) matched[i] = 0;
    
    int* match_edges = malloc(2 * N * sizeof(int));
    int match_edge_idx = 0;
    double match_cost = 0.0;
    
    for (int i = 0; i < n_odd; i++) {
        if (matched[odd[i]]) continue;
        double best = INF; int best_j = -1;
        for (int j = i + 1; j < n_odd; j++) {
            if (!matched[odd[j]] && W[odd[i]][odd[j]] < best) {
                best = W[odd[i]][odd[j]]; best_j = j;
            }
        }
        if (best_j >= 0) {
            int u = odd[i], v = odd[best_j];
            multi[u][v]++; multi[v][u]++;
            matched[u] = 1; matched[v] = 1;
            
            match_edges[match_edge_idx++] = u;
            match_edges[match_edge_idx++] = v;
            match_cost += best;
        }
    }

    if (cb && cb(EVENT_MWPM_CONFIRMED, match_edges, match_edge_idx, match_cost)) {
        free(mst_edges); free(match_edges);
        if (cb) cb(EVENT_DONE, NULL, 0, 0);
        return 0.0;
    }

    int euler[200]; int elen = 0;
    int stk[200]; int sp = 0;
    stk[sp++] = 0;
    while (sp > 0) {
        int v = stk[sp - 1];
        int found = 0;
        for (int u = 0; u < N; u++) {
            if (multi[v][u] > 0) {
                multi[v][u]--; multi[u][v]--;
                stk[sp++] = u;
                found = 1; break;
            }
        }
        if (!found) euler[elen++] = stk[--sp];
    }

    int visited[NUM_ISRAEL_CITIES];
    for (int i = 0; i < N; i++) visited[i] = 0;
    int tlen = 0;
    for (int i = 0; i < elen; i++) {
        int v = euler[i];
        if (!visited[v]) { out_tour[tlen++] = v; visited[v] = 1; }
    }
    for (int v = 0; v < N; v++)
        if (!visited[v]) { out_tour[tlen++] = v; }

    double total = 0.0;
    for (int i = 0; i < N; i++) {
        int u = out_tour[i], v = out_tour[(i + 1) % N];
        total += W[u][v];
    }

    if (cb) cb(EVENT_PATH_CONFIRMED, out_tour, N, total);
    if (cb) cb(EVENT_DONE, NULL, 0, 0);

    free(mst_edges);
    free(match_edges);
    return total;
}
