def create_counter(initial_value=0):
    """
    Module-pattern counter using closures.
    Supports increment, decrement, and reset operations.
    The internal state is encapsulated and not directly accessible.
    """
    count = initial_value

    def increment():
        nonlocal count
        count += 1
        return count

    def decrement():
        nonlocal count
        count -= 1
        return count

    def reset():
        nonlocal count
        count = initial_value
        return count

    def get_count():
        return count

    return {
        'increment': increment,
        'decrement': decrement,
        'reset': reset,
        'get_count': get_count
    }


def test_counter():
    """Comprehensive tests for the closure-based counter."""
    # Test 1: Basic increment
    counter = create_counter()
    assert counter['get_count']() == 0, "Initial value should be 0"
    assert counter['increment']() == 1, "After increment should be 1"
    assert counter['increment']() == 2, "After second increment should be 2"
    assert counter['get_count']() == 2, "get_count should reflect current value"

    # Test 2: Decrement
    assert counter['decrement']() == 1, "After decrement should be 1"
    assert counter['decrement']() == 0, "After second decrement should be 0"

    # Test 3: Reset
    counter['increment']()
    counter['increment']()
    counter['increment']()
    assert counter['get_count']() == 3, "Should be 3 before reset"
    assert counter['reset']() == 0, "After reset should be 0"

    # Test 4: Custom initial value
    counter2 = create_counter(10)
    assert counter2['get_count']() == 10, "Custom initial value should be 10"
    assert counter2['increment']() == 11, "Increment from 10 should be 11"
    assert counter2['reset']() == 10, "Reset should return to 10"

    # Test 5: Independence of separate counters
    counter3 = create_counter()
    counter4 = create_counter()
    counter3['increment']()
    counter3['increment']()
    assert counter3['get_count']() == 2, "counter3 should be 2"
    assert counter4['get_count']() == 0, "counter4 should remain 0 (independent)"

    # Test 6: Negative values
    counter5 = create_counter()
    counter5['decrement']()
    counter5['decrement']()
    assert counter5['get_count']() == -2, "Should support negative values"

    # Test 7: Reset to custom initial value
    counter6 = create_counter(5)
    counter6['increment']()
    counter6['decrement']()
    counter6['decrement']()
    assert counter6['get_count']() == 4, "Should be 4 before reset"
    assert counter6['reset']() == 5, "Reset should return to initial value 5"

    print("All tests passed!")


if __name__ == '__main__':
    test_counter()
