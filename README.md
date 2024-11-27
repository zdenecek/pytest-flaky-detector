

# Flaky Test Detection Plugin for Pytest

This plugin detects flaky tests by re-running them under different conditions such as randomized execution order, specific random seeds, and frozen times. Flaky tests are those that yield inconsistent results (`passed`, `failed`) when executed multiple times.

---

## Features

- **Random Seed Testing**: Re-runs tests with different random seeds to detect flakiness caused by randomness.
- **Time Freezing**: Re-runs tests with frozen system times to detect flakiness caused by time-dependent logic.
- **Reordering Runs**: Re-runs tests multiple times to detect non-deterministic behavior.

---

## Installation

This plugin requires **pytest** and **freezegun**. Install the dependencies using:

```bash
pip install pytest freezegun
```

Add the `conftest.py` file containing the plugin code to your test directory.

---

## Usage

### Enabling Flaky Detection

Run pytest with the `--detect-flaky` flag to enable flaky test detection:

```bash
pytest --detect-flaky
```

### Additional Options

You can customize the behavior of the plugin with the following options:

- **`--reorder-runs`**:
  Number of times to re-run each test to detect randomness issues.

  Default: `3`

  Example:

  ```bash
  pytest --detect-flaky --reorder-runs=5
  ```

- **`--time-freeze-values`**:
  Comma-separated list of frozen times to test time-sensitive logic.

  Default: `2024-01-01,2024-12-31`

  Example:

  ```bash
  pytest --detect-flaky --time-freeze-values="2023-01-01,2023-06-01"
  ```

- **`--random-seeds`**:
  Comma-separated list of random seeds to test randomness-related issues.

  Default: `42,123,999`

  Example:

  ```bash
  pytest --detect-flaky --random-seeds="10,20,30"
  ```

---

## Example

Here’s an example of flaky tests:

**`test_flaky.py`**

```python
import random
from datetime import datetime

def test_random():
    # Flaky: May fail for random values <= 5
    assert random.randint(1, 10) > 5

def test_time():
    # Flaky: Passes only in the year 2024
    assert datetime.now().year == 2024

def test_stable():
    # Stable: Always passes
    assert 2 + 2 == 4
```

Run the flaky test detection:

```bash
pytest --detect-flaky
```

### Expected Output

```plaintext
Detected flaky test: test_flaky.py::test_random with outcomes: {'passed', 'failed'}
Detected flaky test: test_flaky.py::test_time with outcomes: {'passed', 'failed'}
```

---

## How It Works

1. **Normal Execution**: Each test is run once to record its initial outcome.
2. **Reorder Runs**: Tests are re-run multiple times to detect non-deterministic behavior.
3. **Frozen Times**: Tests are re-run with fixed system times to identify time-sensitive logic.
4. **Random Seeds**: Tests are re-run with different random seeds to expose randomness-induced flakiness.

If a test produces more than one unique outcome (`passed`, `failed`), it is flagged as **flaky**.
