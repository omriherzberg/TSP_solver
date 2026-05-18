#include "sort_bus_lines.h"
#include "test_bus_lines.h"
#include <stdio.h>
#include <stdlib.h>

#define NUM_BUSES_ERROR "Error: Number of lines should be a positive integer\n"
#define LINE_NAME_ERROR "Error: line name\n"
#define DISTANCE_ERROR "Error: distance should be an integer between 0 and 1000 (includes)\n"
#define DURATION_ERROR "Error: duration should be an integer between 10 and 100 (includes)\n"
#define FREQUENCY_ERROR "Error: frequency should be an integer between 1 and 50 (includes)\n"
#define USAGE_ERROR "Usage: by_name / by_distance / by_frequency / by duration\n"


#define LINE_NAME_MAX_LEN 21
#define INPUT_MAX_LEN 60
#define ARG_COUNT 2
#define MAX_DISTANCE 1000
#define MAX_DURATION 100
#define MIN_DURATION 10
#define MAX_FREQUENCY 50
#define ERROR_NUM 104

void print_buses(BusLine *start, BusLine *end)
{
  BusLine *tmp = start;
  while (tmp <= end)
    {
      printf("%s,%d,%d,%d\n", tmp->name, tmp->distance,
                            tmp->duration, tmp->frequency);
      tmp++;
    }
}

void print_bus(BusLine b)
{
  printf("cur bus: %s, dis: %d, duration: %d, freq: %d\n", b.name, b.distance, b.duration, b.frequency);
}

int get_num_buses(void)
{
  int num_buses = 0;
  while (num_buses <= 0)
    {
      printf("Enter number of lines. Then enter\n");
      char input[INPUT_MAX_LEN] = {0};
      if (!fgets(input, INPUT_MAX_LEN, stdin))
        {
          return 0;
        }
      sscanf(input, "%d", &num_buses);
      if (num_buses <= 0)
        {
          printf(NUM_BUSES_ERROR);
        }
    }
  return num_buses;
}

int check_bus_name(const char name[])
{
  const char * str_p = name;
  if (strlen(str_p) > LINE_NAME_MAX_LEN)
    {
      return 0;
    }
  while (*str_p != '\0')
    {
      if (*str_p < '0' || (*str_p > '9' && *str_p < 'a') || *str_p > 'z')
        {
          return 0;
        }
      str_p++;
    }
  return 1;
}


int get_bus_line(BusLine *bus_p)
{
  char input[INPUT_MAX_LEN] = {0};
  printf("Enter line info. Then enter\n");
  if (fgets(input, INPUT_MAX_LEN, stdin) == NULL)
  {
    return 0;
  }
  char line_name[LINE_NAME_MAX_LEN];
  int distance = 0;
  int duration = 0;
  int frequency = 0;

  sscanf(input, "%20[^,],%d,%d,%d", line_name, &distance, &duration, &frequency);

  if (!check_bus_name(line_name))
    {
      printf(LINE_NAME_ERROR);
      return 0;
    }

  if (distance < 0 || distance > MAX_DISTANCE)
    {
      printf(DISTANCE_ERROR);
      return 0;
    }
  if (duration < MIN_DURATION || duration > MAX_DURATION)
    {
      printf(DURATION_ERROR);
      return 0;
    }
  if (frequency < 1 || frequency > MAX_FREQUENCY)
    {
      printf(FREQUENCY_ERROR);
      return 0;
    }
  strcpy(bus_p->name,line_name);
  bus_p->distance = distance;
  bus_p->duration = duration;
  bus_p->frequency = frequency;
  return 1;
}



void tests_1_to_4 (BusLine *start, BusLine *end)
{
  BusLine *start_temp = start; BusLine *end_temp = end;
  bus_quick_sort (start_temp, end_temp, DISTANCE);
  if (is_sorted_by_distance (start_temp, end_temp))
    {
      printf("TEST 1 PASSED: The array is sorted by distance\n");
    }
  else
    {
      printf("TEST 1 FAILED: Not sorted by distance\n");
    }
  if (is_equal (start_temp, end_temp, start, end))
    {
      printf("TEST 2 PASSED: The array has the same items after sorting\n");
    }
  else
    {
      printf("TEST 2 FAILED: Items changed\n");
    }
  start_temp = start, end_temp = end;
  bus_quick_sort (start_temp, end_temp, DURATION);
  if (is_sorted_by_duration (start_temp, end_temp))
    {
      printf("TEST 3 PASSED: The array is sorted by duration\n");
    }
  else
    {
      printf("TEST 3 FAILED: Not sorted by duration\n");
    }
  if (is_equal (start_temp, end_temp, start, end))
    {
      printf("TEST 4 PASSED: The array has the same items after sorting\n");
    }
  else
    {
      printf("TEST 4 FAILED: Items changed\n");
    }
}
  void tests_5_to_8(BusLine *start, BusLine *end)
{
  BusLine *start_temp = start; BusLine *end_temp = end;
  bus_quick_sort (start_temp, end_temp, FREQUENCY);
  if (is_sorted_by_frequency (start_temp, end_temp))
    {
      printf("TEST 5 PASSED: The array is sorted by frequency\n");
    }
  else
    {
      printf("TEST 5 FAILED: Not sorted by frequency\n");
    }
  if (is_equal (start_temp, end_temp, start, end))
    {
      printf("TEST 6 PASSED: The array has the same items after sorting\n");
    }
  else
    {
      printf("TEST 6 FAILED: Items changed\n");
    }
  start_temp = start, end_temp = end;
  bus_bubble_sort (start_temp, end_temp);
  if (is_sorted_by_name (start_temp, end_temp))
    {
      printf("TEST 7 PASSED: The array is sorted by name\n");
    }
  else
    {
      printf("TEST 7 FAILED: Not sorted by name\n");
    }
  if (is_equal (start_temp, end_temp, start, end))
    {
      printf("TEST 8 PASSED: The array has the same items after sorting\n");
    }
  else
    {
      printf("TEST 8 FAILED: Items changed\n");
    }
}

void run_tests (BusLine *start, BusLine *end)
{
  tests_1_to_4(start, end);
  tests_5_to_8(start, end);
}

int check_args(char arg[])
{
  SortType sort_type = 0;
  if (strcmp(arg, "by_duration") == 0)
    {
      sort_type = DURATION;
    }
  else if (strcmp(arg, "by_distance") == 0)
    {
      sort_type = DISTANCE;
    }
  else if (strcmp(arg, "by_frequency") == 0)
    {
      sort_type = FREQUENCY;
    }
  else if (strcmp(arg, "by_name") != 0 && strcmp(arg, "test") != 0)
    {
      printf(USAGE_ERROR);
      return ERROR_NUM;
    }
  return sort_type;
}

int main (int argc, char *argv[])
{
  if (argc != ARG_COUNT)
    {
      printf(USAGE_ERROR);
      return EXIT_FAILURE;
    }
  const SortType sort_type = check_args(argv[1]);
  if (sort_type != DISTANCE && sort_type != FREQUENCY && sort_type != DURATION)
    {
      return EXIT_FAILURE;
    }
  const int num_buses = get_num_buses();
  BusLine* start = malloc(sizeof(BusLine)*num_buses);
  if (start == NULL)
    {
      return EXIT_FAILURE;
    }
  int cur_buses = 0;
  while (cur_buses < num_buses)
    {
      BusLine *cur_bus = start + cur_buses;
      if (get_bus_line(cur_bus))
        {
          cur_buses++;
        }
    }
  if (strcmp(argv[1], "by_name") == 0)
    {
      bus_bubble_sort (start, start+num_buses-1);
      print_buses (start, start+num_buses-1);
    }
  else if (strcmp(argv[1], "test") == 0)
    {
      run_tests(start, start+num_buses-1);
    }
  else
    {
      bus_quick_sort (start, start+num_buses-1, sort_type);
      print_buses (start, start+num_buses-1);
    }
  free(start);
  return EXIT_SUCCESS;
}
