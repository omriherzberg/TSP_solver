#include "test_bus_lines.h"
#include <string.h>

int is_sorted_by_distance (const BusLine *start, const BusLine *end)
{
  const BusLine *cur_p = start;
  while (cur_p != end)
    {
      if (cur_p->distance > (cur_p+1)->distance)
        {
          return 0;
        }
      cur_p++;
    }
  return 1;
}

int is_sorted_by_duration (const BusLine *start, const BusLine *end)
{
  const BusLine *cur_p = start;
  while (cur_p != end)
    {
      if (cur_p->duration > (cur_p+1)->duration)
        {
          return 0;
        }
      cur_p++;
    }
  return 1;
}

int is_sorted_by_frequency (const BusLine *start, const BusLine *end)
{
  const BusLine *cur_p = start;
  while (cur_p != end)
    {
      if (cur_p->frequency > (cur_p+1)->frequency)
        {
          return 0;
        }
      cur_p++;
    }
  return 1;
}

int is_sorted_by_name (const BusLine *start, const BusLine *end)
{
  const BusLine *cur_p = start;
  while (cur_p != end)
    {
      if (strcmp(cur_p->name, (cur_p+1)->name) > 0)
        {
          return 0;
        }
      cur_p++;
    }
  return 1;
}

int is_equal (const BusLine *start_sorted,
              const BusLine *end_sorted,
              const BusLine *start_original,
              const BusLine *end_original)
{
  if (end_sorted - start_sorted != end_original - start_original)
    {
      return 0;
    }
  const BusLine *sorted_p = start_sorted;
  const BusLine *original_p = start_original;
  while (original_p != end_original)
    {
      sorted_p = start_sorted;
      while (original_p->name != sorted_p->name)
        {
          if (sorted_p == end_sorted)
            {
              return 0;
            }
          sorted_p++;
        }
      original_p++;
    }
  return 1;
}