import pytest
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'py_ui'))
from main import process_buses

# --- ORIGINAL TESTS ---

def test_empty_input(capsys):
    process_buses([], "by_distance")
    captured = capsys.readouterr()
    assert captured.out == ""

def test_single_bus(capsys):
    process_buses(["busa,500,20,5"], "by_distance")
    captured = capsys.readouterr()
    assert captured.out == "busa,500,20,5\n"

def test_sort_by_distance(capsys):
    inputs = ["busa,500,20,5", "busc,100,10,2", "busb,200,15,3"]
    process_buses(inputs, "by_distance")
    captured = capsys.readouterr()
    assert captured.out == "busc,100,10,2\nbusb,200,15,3\nbusa,500,20,5\n"

def test_sort_by_duration(capsys):
    inputs = ["busa,500,50,5", "busc,100,10,2", "busb,200,80,3"]
    process_buses(inputs, "by_duration")
    captured = capsys.readouterr()
    assert captured.out == "busc,100,10,2\nbusa,500,50,5\nbusb,200,80,3\n"

def test_sort_by_frequency(capsys):
    inputs = ["busa,500,50,50", "busc,100,10,1", "busb,200,80,10"]
    process_buses(inputs, "by_frequency")
    captured = capsys.readouterr()
    assert captured.out == "busc,100,10,1\nbusb,200,80,10\nbusa,500,50,50\n"

def test_sort_by_name(capsys):
    inputs = ["zebra,500,50,50", "alpha,100,10,1", "bravo,200,80,10"]
    process_buses(inputs, "by_name")
    captured = capsys.readouterr()
    assert captured.out == "alpha,100,10,1\nbravo,200,80,10\nzebra,500,50,50\n"

def test_already_sorted(capsys):
    inputs = ["a,10,10,1", "b,20,20,2", "c,30,30,3"]
    process_buses(inputs, "by_distance")
    captured = capsys.readouterr()
    assert captured.out == "a,10,10,1\nb,20,20,2\nc,30,30,3\n"

def test_reverse_sorted(capsys):
    inputs = ["c,30,30,3", "b,20,20,2", "a,10,10,1"]
    process_buses(inputs, "by_distance")
    captured = capsys.readouterr()
    assert captured.out == "a,10,10,1\nb,20,20,2\nc,30,30,3\n"

def test_extreme_values(capsys):
    inputs = ["maxdist,1000,10,1", "mindist,0,10,1", "mid,500,10,1"]
    process_buses(inputs, "by_distance")
    captured = capsys.readouterr()
    assert captured.out == "mindist,0,10,1\nmid,500,10,1\nmaxdist,1000,10,1\n"

# --- NEW INCORRECT INPUT SCENARIOS ---

def test_missing_fields():
    """Test that missing commas/fields raises an unpacking ValueError."""
    inputs = ["busa,500,20"] # missing frequency
    with pytest.raises(ValueError):
        process_buses(inputs, "by_distance")

def test_invalid_distance_type():
    """Test that non-integer distance raises a ValueError."""
    inputs = ["busa,not_a_number,20,5"]
    with pytest.raises(ValueError):
        process_buses(inputs, "by_distance")

def test_invalid_duration_type():
    """Test that non-integer duration raises a ValueError."""
    inputs = ["busa,500,not_a_number,5"]
    with pytest.raises(ValueError):
        process_buses(inputs, "by_distance")

def test_empty_string_input():
    """Test that an empty string line raises a ValueError."""
    inputs = [""]
    with pytest.raises(ValueError):
        process_buses(inputs, "by_distance")

def test_invalid_sort_type_defaults_to_distance(capsys):
    """Test that passing a garbage sort type defaults safely to distance."""
    inputs = ["busc,100,10,2", "busb,200,15,3", "busa,500,20,5"]
    process_buses(inputs, "by_garbage_sort")
    captured = capsys.readouterr()
    expected = "busc,100,10,2\nbusb,200,15,3\nbusa,500,20,5\n"
    assert captured.out == expected

def test_duplicate_elements(capsys):
    """Test that identical elements are sorted stably without corruption."""
    inputs = ["busa,100,10,2", "busa,100,10,2", "busa,100,10,2"]
    process_buses(inputs, "by_distance")
    captured = capsys.readouterr()
    expected = "busa,100,10,2\nbusa,100,10,2\nbusa,100,10,2\n"
    assert captured.out == expected

def test_negative_distance():
    """Test that a distance < 0 is rejected."""
    inputs = ["busa,-10,10,2"]
    with pytest.raises(ValueError, match="Distance must be between 0 and 1000"):
        process_buses(inputs, "by_distance")

def test_out_of_bounds_duration():
    """Test that a duration > 100 is rejected."""
    inputs = ["busa,100,101,2"]
    with pytest.raises(ValueError, match="Duration must be between 10 and 100"):
        process_buses(inputs, "by_distance")

def test_zero_frequency():
    """Test that a frequency < 1 is rejected."""
    inputs = ["busa,100,10,0"]
    with pytest.raises(ValueError, match="Frequency must be between 1 and 50"):
        process_buses(inputs, "by_distance")

def test_invalid_name_characters():
    """Test that names with capital letters or symbols are rejected."""
    inputs = ["Bus_A,100,10,2"]
    with pytest.raises(ValueError, match="Bus name must contain only lowercase letters and digits"):
        process_buses(inputs, "by_distance")

def test_large_array(capsys):
    """Test sorting a large number of buses dynamically."""
    inputs = [f"bus{i},{1000-i},50,25" for i in range(50)]
    process_buses(inputs, "by_distance")
    captured = capsys.readouterr()
    # Ensure all 50 printed correctly
    lines = captured.out.strip().split("\n")
    assert len(lines) == 50
    # The first one should be bus49 (distance 951)
    assert lines[0] == "bus49,951,50,25"
    # The last one should be bus0 (distance 1000)
    assert lines[-1] == "bus0,1000,50,25"

