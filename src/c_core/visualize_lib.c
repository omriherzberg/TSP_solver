#include "sort_bus_lines.h"

// Callback function signature: Returns 1 if aborted, 0 otherwise
typedef int (*VizCallback)(int event_type, int p1, int p2, int p3, int p4);

// C-driven Bubble Sort visualization
void visualize_bubble_sort_c(BusLine *start, BusLine *end, VizCallback cb) {
    int const total_buses = (int)(end - start);
    for (int i = 0; i < total_buses; i++) {
        BusLine *cur_p = start;
        BusLine *next_p = start + 1;
        
        while (cur_p < end - i) {
            int cur_idx = (int)(cur_p - start);
            int next_idx = (int)(next_p - start);
            
            // Compare event
            if (cb && cb(1, cur_idx, next_idx, -1, -1)) return;
            
            if (strcmp(cur_p->name, next_p->name) > 0) {
                // Swap event
                if (cb && cb(2, cur_idx, next_idx, -1, -1)) return;
                
                // Actual Swap in C
                BusLine temp = *next_p;
                *next_p = *cur_p;
                *cur_p = temp;
            }
            cur_p++; 
            next_p++;
        }
    }
    // Done event
    if (cb) cb(3, -1, -1, -1, -1);
}

// Helper for partition
int visualize_partition_c(BusLine *arr_start, BusLine *start, BusLine *end, SortType sort_type, VizCallback cb, BusLine** out_pivot) {
    BusLine *pivot = end;
    BusLine *cur_p = start;
    BusLine *lower_than_pivot = start;
    
    int pivot_idx = (int)(pivot - arr_start);
    
    while (cur_p != end) {
        int cur_idx = (int)(cur_p - arr_start);
        int low_idx = (int)(lower_than_pivot - arr_start);
        
        // Compare event
        if (cb && cb(1, cur_idx, low_idx, pivot_idx, -1)) return 1;
        
        if (is_lower_field(*cur_p, *pivot, sort_type)) {
            // Swap event
            if (cb && cb(2, cur_idx, low_idx, pivot_idx, -1)) return 1;
            
            // Actual Swap in C
            BusLine temp = *cur_p;
            *cur_p = *lower_than_pivot;
            *lower_than_pivot = temp;
            
            lower_than_pivot++;
        }
        cur_p++;
    }
    
    int low_idx = (int)(lower_than_pivot - arr_start);
    
    // Swap pivot event
    if (cb && cb(2, pivot_idx, low_idx, pivot_idx, -1)) return 1;
    
    BusLine temp = *pivot;
    *pivot = *lower_than_pivot;
    *lower_than_pivot = temp;
    
    *out_pivot = lower_than_pivot;
    return 0;
}

// Recursive quick sort visualization
int visualize_quick_sort_recursive(BusLine *arr_start, BusLine *start, BusLine *end, SortType sort_type, VizCallback cb) {
    if (start >= end) return 0;
    
    BusLine *pivot;
    if (visualize_partition_c(arr_start, start, end, sort_type, cb, &pivot)) return 1;
    if (visualize_quick_sort_recursive(arr_start, start, pivot - 1, sort_type, cb)) return 1;
    if (visualize_quick_sort_recursive(arr_start, pivot + 1, end, sort_type, cb)) return 1;
    return 0;
}

// C-driven Quick Sort visualization entry
void visualize_quick_sort_c(BusLine *start, BusLine *end, SortType sort_type, VizCallback cb) {
    if (visualize_quick_sort_recursive(start, start, end, sort_type, cb)) return;
    // Done event
    if (cb) cb(3, -1, -1, -1, -1);
}
