import pytest
import random
from datetime import datetime


@pytest.mark.flaky
def test_random_behavior():
    # Test that depends on random behavior
    assert random.choice([True, False])


@pytest.mark.flaky
def test_time_dependent():
    # Test that depends on the current time
    now = datetime.now()
    assert now.year == 2024


@pytest.mark.flaky
def test_deterministic_behavior():
    # Test that fails based on order
    global order_count
    order_count += 1
    assert order_count % 2 == 0


order_count = 0
