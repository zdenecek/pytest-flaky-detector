### Updated README for `pytest-myplugin`

---

# `pytest-myplugin`

`pytest-myplugin` is a Pytest plugin designed to detect flaky tests caused by:

1. **Reordering tests**: Runs the test suite in different orders.
2. **Freezing time**: Runs the tests with fixed and variable times.
3. **Seeding the random number generator**: Runs the tests with different random seeds.

It helps identify and debug non-deterministic behavior in your tests.

---

## Features

- **Reorder tests**: Runs the tests multiple times in random orders to detect flakiness.
- **Time freezing**: Simulates different times during test execution using `freezegun`.
- **Random seeding**: Reruns tests with various random seeds to detect RNG-related flakiness.
- Outputs flaky test information including outcomes and reasons.

---

## Installation

### Local Installation for Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pytest-myplugin.git
   cd pytest-myplugin
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Build the package:
   ```bash
   poetry build
   ```

4. Install the plugin locally:
   ```bash
   pip install dist/pytest_myplugin-0.1.0.tar.gz
   ```

---

## Usage

Run Pytest with the plugin enabled using the `--detect-flaky` option:

```bash
pytest --detect-flaky
```

### Additional Options

- `--reorder-runs=<number>`: Number of times to reorder and rerun the tests. Default is 3.
- `--time-freeze-values=<times>`: Comma-separated list of times to freeze during test runs. Default is `"2024-01-01,2024-12-31"`.
- `--random-seeds=<seeds>`: Comma-separated list of seeds for the random number generator. Default is `"42,123,999"`.

#### Example:

```bash
pytest --detect-flaky --reorder-runs=5 --time-freeze-values="2024-01-01,2024-06-15" --random-seeds="1,2,3,42"
```

---

## Testing the Plugin Locally

### Step 1: Add a Test Suite

Create a sample test suite (`tests/test_flaky_tester.py`) with flaky behavior to test the plugin:

```python
import pytest
import random
from datetime import datetime


@pytest.mark.flaky
def test_random_behavior():
    assert random.choice([True, False])


@pytest.mark.flaky
def test_time_dependent():
    now = datetime.now()
    assert now.year == 2024


@pytest.mark.flaky
def test_order_dependent():
    global order_count
    order_count += 1
    assert order_count % 2 == 0


order_count = 0
```

### Step 2: Run the Plugin

Run the plugin against the test suite:

```bash
pytest --detect-flaky --reorder-runs=5 --time-freeze-values="2024-01-01,2024-12-31" --random-seeds="42,123,999"
```

### Step 3: View the Output

The plugin will detect flaky tests and display them in the console. For example:

```
Detected flaky test: test_random_behavior with outcomes: {'passed', 'failed'}
Detected flaky test: test_time_dependent with outcomes: {'passed', 'failed'}
Detected flaky test: test_order_dependent with outcomes: {'passed', 'failed'}
```

---

## Development

### Run Tests for the Plugin

Run tests for the plugin using:

```bash
poetry run pytest
```

---
