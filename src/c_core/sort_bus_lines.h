#ifndef EX2_REPO_SORTBUSLINES_H
#define EX2_REPO_SORTBUSLINES_H
// write only between #define EX2_REPO_SORTBUSLINES_H and #endif //EX2_REPO_SORTBUSLINES_H
#include <string.h>
#define NAME_LEN 21
/**
 * bus line struct containing 4 args: 1 string and 3 ints.
 */
typedef struct BusLine
{
    char name[NAME_LEN];
    int distance, duration, frequency;
} BusLine;

typedef enum SortType
{
    DISTANCE,
    DURATION,
    FREQUENCY
} SortType;

/**
 * performs bubble sort on the bus name
 */
void bus_bubble_sort (BusLine *start, BusLine *end);

/**
 * performs quicksort depending on the argument to be sorted
 */
void bus_quick_sort (BusLine *start, BusLine *end, SortType sort_type);

/**
 * partition function as part of quicksort, uses the last element as pivot,
 * returns pivot pointer
 */
BusLine *partition (BusLine *start, BusLine *end, SortType sort_type);

/**
 * gets 2 BusLine pointers and swaps their contents
 */
void swap_lines (BusLine *a, BusLine *b);

/**
 *
 gets 2 BusLine structs and a field on which to compare returns true if the
 first is lower than the second
 */
int is_lower_field(BusLine a, BusLine b, SortType sort_type);

// write only between #define EX2_REPO_SORTBUSLINES_H and #endif //EX2_REPO_SORTBUSLINES_H
#endif //EX2_REPO_SORTBUSLINES_H
