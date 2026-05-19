#ifndef CONSTANTS_H
#define CONSTANTS_H

// Core Solver Configurations
#define MAX_STATIONS 20
#define NAME_LEN 21

// TSP Visualization Event Types (for C-to-Python callbacks)
typedef enum {
    EVENT_EVALUATING = 1,       // Path/Edge is being evaluated/considered
    EVENT_PATH_CONFIRMED = 2,   // Exact/greedy path confirmed
    EVENT_DONE = 3,             // Done/cleanup signal to unlock UI
    EVENT_MST_CONFIRMED = 4,    // MST edges computed (Christofides Step 1)
    EVENT_MWPM_CONFIRMED = 5,    // MWPM edges computed (Christofides Step 2)
    EVENT_GREEDY_EDGES = 6,     // Greedy Edge-Insertion intermediate state
    EVENT_1TREE_EVALUATING = 7, // 1-Tree evaluating state
    EVENT_1TREE_CONFIRMED = 8,  // Final Max 1-Tree locked in
    EVENT_MWPM_DELEGATE = 9,    // exact MWPM computation delegation request
    EVENT_2OPT_SWAP = 10,       // 2-opt edge uncrossing performed
    EVENT_1OPT_SWAP = 11,       // 1-opt node relocation performed
    EVENT_2OPT_EVALUATING = 12, // evaluating a 2-opt swap
    EVENT_1OPT_EVALUATING = 13, // evaluating a 1-opt insertion
    EVENT_SA_SWAP = 14,         // simulated annealing swap performed
    EVENT_SA_EVALUATING = 15    // evaluating a simulated annealing swap
} TspEventType;

#endif // CONSTANTS_H
