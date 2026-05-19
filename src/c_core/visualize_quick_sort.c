#include "sort_bus_lines.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Helper function to print the current state of the array with simulated memory addresses
void print_qsort_state(BusLine *arr_start, BusLine *arr_end, BusLine *sub_start, BusLine *sub_end, BusLine *cur_p, BusLine *lower_than_pivot, BusLine *pivot) {
    printf("               [ Memory ]   [ Data (Distance) ]\n");
    BusLine *p = arr_start;
    while (p <= arr_end) {
        char prefix[40] = "";
        
        // If outside the current sub-array being partitioned
        if (p < sub_start || p > sub_end) {
            strcpy(prefix, "  (out of bounds) ->");
        } else {
            // Label the active pointers
            if (p == pivot && p == cur_p && p == lower_than_pivot) strcpy(prefix, "cur,low,pivot->");
            else if (p == pivot && p == lower_than_pivot) strcpy(prefix, "low,pivot   ->");
            else if (p == pivot && p == cur_p) strcpy(prefix, "cur,pivot   ->");
            else if (p == cur_p && p == lower_than_pivot) strcpy(prefix, "cur,low     ->");
            else if (p == pivot) strcpy(prefix, "pivot       ->");
            else if (p == lower_than_pivot) strcpy(prefix, "low_than_piv->");
            else if (p == cur_p) strcpy(prefix, "cur_p       ->");
            else strcpy(prefix, "            ->");
        }

        // Simulate the hex address by calculating offset from the base pointer
        int offset = (int)(p - arr_start);
        int mock_address = 0x1000 + (offset * 0x40);

        if (p < sub_start || p > sub_end) {
            // Dimmed output for out-of-bounds elements (using ANSI escape codes if terminal supports it, but keeping it plain text here for clarity)
            printf("%-16s | 0x%X | = \"%s\" (%d)\n", prefix, mock_address, p->name, p->distance);
        } else {
            printf("%-16s | 0x%X | = \"%s\" (%d)\n", prefix, mock_address, p->name, p->distance);
        }
        p++;
    }
    printf("\n");
}

// A visualization version of partition
BusLine *visualize_partition(BusLine *arr_start, BusLine *arr_end, BusLine *start, BusLine *end, SortType sort_type, int depth) {
    BusLine *pivot = end;
    BusLine *cur_p = start;
    BusLine *lower_than_pivot = start;
    
    printf("\n");
    for(int i=0; i<depth; i++) printf("  ");
    printf("--- PARTITION Sub-Array [%s to %s] ---\n", start->name, end->name);

    int step = 1;
    while (cur_p != end) {
        for(int i=0; i<depth; i++) printf("  ");
        printf("Step %d: Compare %s(%d) < Pivot %s(%d)?\n", step++, cur_p->name, cur_p->distance, pivot->name, pivot->distance);
        
        print_qsort_state(arr_start, arr_end, start, end, cur_p, lower_than_pivot, pivot);

        if (is_lower_field(*cur_p, *pivot, sort_type)) {
            for(int i=0; i<depth; i++) printf("  ");
            printf("Result: YES. Swap cur_p with lower_than_pivot.\n\n");
            
            // Swap
            BusLine temp = *cur_p;
            *cur_p = *lower_than_pivot;
            *lower_than_pivot = temp;
            
            lower_than_pivot++;
        } else {
            for(int i=0; i<depth; i++) printf("  ");
            printf("Result: NO. No swap. Advance cur_p.\n\n");
        }
        cur_p++;
    }
    
    for(int i=0; i<depth; i++) printf("  ");
    printf("End of partition loop. Swapping lower_than_pivot with pivot!\n\n");
    
    // Swap pivot into its correct place
    BusLine temp = *pivot;
    *pivot = *lower_than_pivot;
    *lower_than_pivot = temp;
    
    // lower_than_pivot is the new pivot position, we print state with pivot moved here
    print_qsort_state(arr_start, arr_end, start, end, NULL, lower_than_pivot, lower_than_pivot); 
    
    return lower_than_pivot;
}

// A visualization version of bus_quick_sort
void visualize_bus_quick_sort(BusLine *arr_start, BusLine *arr_end, BusLine *start, BusLine *end, SortType sort_type, int depth) {
    if (start >= end) {
        return;
    }
    BusLine *pivot = visualize_partition(arr_start, arr_end, start, end, sort_type, depth);
    
    // Recursive left
    visualize_bus_quick_sort(arr_start, arr_end, start, pivot - 1, sort_type, depth + 1);
    
    // Recursive right
    visualize_bus_quick_sort(arr_start, arr_end, pivot + 1, end, sort_type, depth + 1);
}

#ifdef STANDALONE
int main() {
    // Array of 4 elements to clearly demonstrate quick sort partitioning
    BusLine arr[4] = {
        {"Alice", 50, 20, 30},
        {"Bob", 20, 25, 35},
        {"Charlie", 80, 10, 15},
        {"Dan", 30, 40, 50}
    };

    BusLine *start = &arr[0];
    BusLine *end = &arr[3];

    printf("============= QUICK SORT VISUALIZATION =============\n");
    printf("Sorting by DISTANCE.\n\n");
    printf("Initial Array:\n");
    print_qsort_state(start, end, start, end, NULL, NULL, NULL);
    
    visualize_bus_quick_sort(start, end, start, end, DISTANCE, 0);

    printf("============= FINAL SORTED ARRAY =============\n");
    print_qsort_state(start, end, start, end, NULL, NULL, NULL);

    return 0;
}
#endif
