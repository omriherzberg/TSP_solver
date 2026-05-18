#include "sort_bus_lines.h"

// Callback function signature:
// event_type: 1 = Compare, 2 = Swap, 3 = Done
// p1, p2, p3, p4: indices of pointers (-1 if not used)
typedef void (*VizCallback)(int event_type, int p1, int p2, int p3, int p4);

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
            cb(1, cur_idx, next_idx, -1, -1);
            
            if (strcmp(cur_p->name, next_p->name) > 0) {
                // Swap event
                cb(2, cur_idx, next_idx, -1, -1);
                
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
    cb(3, -1, -1, -1, -1);
}

// Helper for partition
void visualize_partition_c(BusLine *arr_start, BusLine *start, BusLine *end, SortType sort_type, VizCallback cb, BusLine** out_pivot) {
    BusLine *pivot = end;
    BusLine *cur_p = start;
    BusLine *lower_than_pivot = start;
    
    int pivot_idx = (int)(pivot - arr_start);
    
    while (cur_p != end) {
        int cur_idx = (int)(cur_p - arr_start);
        int low_idx = (int)(lower_than_pivot - arr_start);
        
        // Compare event
        cb(1, cur_idx, low_idx, pivot_idx, -1);
        
        if (is_lower_field(*cur_p, *pivot, sort_type)) {
            // Swap event
            cb(2, cur_idx, low_idx, pivot_idx, -1);
            
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
    cb(2, pivot_idx, low_idx, pivot_idx, -1);
    
    BusLine temp = *pivot;
    *pivot = *lower_than_pivot;
    *lower_than_pivot = temp;
    
    *out_pivot = lower_than_pivot;
}

// Recursive quick sort visualization
void visualize_quick_sort_recursive(BusLine *arr_start, BusLine *start, BusLine *end, SortType sort_type, VizCallback cb) {
    if (start >= end) return;
    
    BusLine *pivot;
    visualize_partition_c(arr_start, start, end, sort_type, cb, &pivot);
    visualize_quick_sort_recursive(arr_start, start, pivot - 1, sort_type, cb);
    visualize_quick_sort_recursive(arr_start, pivot + 1, end, sort_type, cb);
}

// C-driven Quick Sort visualization entry
void visualize_quick_sort_c(BusLine *start, BusLine *end, SortType sort_type, VizCallback cb) {
    visualize_quick_sort_recursive(start, start, end, sort_type, cb);
    // Done event
    cb(3, -1, -1, -1, -1);
}
