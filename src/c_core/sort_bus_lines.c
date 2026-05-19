#include "sort_bus_lines.h"
#include <stdio.h>
#include <stdlib.h>

void swap_lines (BusLine *a, BusLine *b)
{
  if (a == NULL || b == NULL)
    {
      return;
    }
  const BusLine temp = *b;
  *b = *a;
  *a = temp;
}

void bus_bubble_sort (BusLine *start, BusLine *end)
{
  int const total_buses = (int)(end - start);

  for (int i = 0; i < total_buses; i++)
    {
      BusLine *cur_p = start;
      BusLine *next_p = start + 1;
      while (cur_p < end - i)
        {
          if (strcmp(cur_p->name,next_p->name) > 0)
            {
              swap_lines(cur_p, next_p);
            }
          cur_p++, next_p++;
        }
    }
}

int is_lower_field(const BusLine a,const BusLine b, const SortType sort_type)
{
  switch (sort_type)
    {
    case DISTANCE:
      return a.distance < b.distance;
    case DURATION:
      return a.duration < b.duration;
    case FREQUENCY:
      return a.frequency < b.frequency;
    }
  printf("Invalid sort type: %d\n", sort_type);
  return EXIT_FAILURE;
}

BusLine *partition (BusLine *start, BusLine *end, SortType sort_type)
{
  BusLine *pivot = end;
  BusLine *cur_p = start;
  BusLine *lower_than_pivot = start;

  while (cur_p != end)
    {
      if (is_lower_field (*cur_p, *pivot, sort_type))
        {
          swap_lines(lower_than_pivot, cur_p);
          lower_than_pivot++;
        }
      cur_p++;
    }
  swap_lines(lower_than_pivot, pivot);
  return lower_than_pivot;
}

void bus_quick_sort(BusLine *start, BusLine *end, SortType sort_type)
{
  if (start >= end)
    {
      return;
    }
  BusLine *pivot = partition(start,end,sort_type);
  bus_quick_sort (start,pivot-1,sort_type);
  bus_quick_sort (pivot+1,end,sort_type);
}