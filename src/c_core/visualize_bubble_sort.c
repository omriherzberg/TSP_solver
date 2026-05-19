#include "sort_bus_lines.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Helper function to print the current state of the array with simulated memory addresses
void print_visualization_state(BusLine *start, BusLine *end, BusLine *cur_p, BusLine *next_p) {
    printf("               [ Memory ]   [ Data ]\n");
    BusLine *p = start;
    while (p <= end) {
        char prefix[20] = "";
        
        // Determine the pointer labels pointing to this specific struct
        if (p == start && p == cur_p) strcpy(prefix, "start, j    ->");
        else if (p == start) strcpy(prefix, "start       ->");
        else if (p == end && p == next_p) strcpy(prefix, "end, j+1    ->");
        else if (p == end) strcpy(prefix, "end         ->");
        else if (p == cur_p) strcpy(prefix, "       j    ->");
        else if (p == next_p) strcpy(prefix, "       j+1  ->");
        else strcpy(prefix, "            ->");

        // Simulate the hex address by calculating offset from the base pointer
        int offset = (int)(p - start);
        int mock_address = 0x1000 + (offset * 0x40);

        printf("%-14s | 0x%X | = \"%s\"\n", prefix, mock_address, p->name);
        p++;
    }
    printf("\n");
}

// A visualization version of bus_bubble_sort. 
// The core logic is identical, but decorated with printf statements.
void visualize_bus_bubble_sort(BusLine *start, BusLine *end) {
    int const total_buses = (int)(end - start);

    printf("=== Initial Setup ===\n");
    printf("Total elements: %d\n", total_buses + 1);
    printf("Passes needed: %d\n\n", total_buses);

    for (int i = 0; i < total_buses; i++) {
        printf("============= PASS i = %d =============\n", i);
        BusLine *cur_p = start;
        BusLine *next_p = start + 1;
        
        int step = 1;
        while (cur_p < end - i) {
            printf("--- Step %d.%d ---\n", i + 1, step++);
            print_visualization_state(start, end, cur_p, next_p);
            
            printf("Comparison: Is \"%s\" > \"%s\"?\n", cur_p->name, next_p->name);
            
            if (strcmp(cur_p->name, next_p->name) > 0) {
                printf("Result: YES. SWAP!\n\n");
                
                // Swap logic (Identical to your original code)
                BusLine temp = *next_p;
                *next_p = *cur_p;
                *cur_p = temp;
                
                printf("State after swap:\n");
                print_visualization_state(start, end, cur_p, next_p); 
            } else {
                printf("Result: NO. No swap occurs.\n\n");
            }
            cur_p++; 
            next_p++;
        }
    }
    
    printf("============= Final State =============\n");
    print_visualization_state(start, end, NULL, NULL);
}

#ifdef STANDALONE
int main() {
    // Create the exact example array discussed
    BusLine arr[3] = {
        {"Dan", 10, 20, 30},
        {"Alice", 15, 25, 35},
        {"Charlie", 5, 10, 15}
    };

    BusLine *start = &arr[0];
    BusLine *end = &arr[2];

    visualize_bus_bubble_sort(start, end);

    return 0;
}
#endif
