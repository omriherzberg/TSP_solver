#ifndef EX2_REPO_TESTBUSLINES_H
#define EX2_REPO_TESTBUSLINES_H
// write only between #define EX2_REPO_TESTBUSLINES_H and #endif //EX2_REPO_TESTBUSLINES_H
#include "sort_bus_lines.h"

/**
 * Checks if buses are sorted by distance
 */
int is_sorted_by_distance (const BusLine *start, const BusLine *end);

/**
 * Checks if buses are sorted by duration
 */
int is_sorted_by_duration (const BusLine *start, const BusLine *end);

/**
 * Checks if buses are sorted by frequency
 */
int is_sorted_by_frequency (const BusLine *start, const BusLine *end);

/**
 * Checks if buses are sorted by name
 */
int is_sorted_by_name (const BusLine *start, const BusLine *end);

/**
 * Checks if buses are unchanged
 */
int is_equal (const BusLine *start_sorted,
              const BusLine *end_sorted,
              const BusLine *start_original,
              const BusLine *end_original);

// write only between #define EX2_REPO_TESTBUSLINES_H and #endif //EX2_REPO_TESTBUSLINES_H
#endif //EX2_REPO_TESTBUSLINES_H
