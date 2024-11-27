import pytest
import random
from freezegun import freeze_time


class FlakyTestDetector:
    def __init__(self, config):
        self.config = config
        self.flaky_tests = {}
        self.reorder_runs = int(config.getoption("--reorder-runs", default=3))
        self.time_freeze_values = config.getoption("--time-freeze-values", default="2024-01-01,2024-12-31").split(",")
        self.random_seeds = config.getoption("--random-seeds", default="42,123,999").split(",")

    def record_outcome(self, nodeid, outcome):
        """Record the outcome of the test."""
        if nodeid not in self.flaky_tests:
            self.flaky_tests[nodeid] = set()
        self.flaky_tests[nodeid].add(outcome)

    def is_flaky(self, nodeid):
        """Check if a test is flaky."""
        outcomes = self.flaky_tests.get(nodeid, set())
        return len(outcomes) > 1

    def run_test(self, item):
        """Run a test and return its outcome."""
        try:
            item.ihook.pytest_runtest_setup(item=item)
            item.ihook.pytest_runtest_call(item=item)
            outcome = "passed"
        except Exception:
            outcome = "failed"
        finally:
            item.ihook.pytest_runtest_teardown(item=item, nextitem=None)
        return outcome

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        if not self.config.getoption("--detect-flaky", default=False):
            yield  # Let pytest handle test execution normally
            return

        nodeid = item.nodeid
        outcomes = set()

        # Run the test normally
        normal_outcome = self.run_test(item)
        outcomes.add(normal_outcome)
        self.record_outcome(nodeid, normal_outcome)

        # Run the test with different random seeds
        for seed in self.random_seeds:
            random.seed(int(seed.strip()))
            outcome = self.run_test(item)
            outcomes.add(outcome)
            self.record_outcome(nodeid, outcome)

        # Run the test with frozen times
        for time_str in self.time_freeze_values:
            with freeze_time(time_str.strip()):
                outcome = self.run_test(item)
                outcomes.add(outcome)
                self.record_outcome(nodeid, outcome)

        # Run the test multiple times for reordering
        for _ in range(self.reorder_runs):
            outcome = self.run_test(item)
            outcomes.add(outcome)
            self.record_outcome(nodeid, outcome)

        # Report if flaky
        if self.is_flaky(nodeid):
            print(f"Detected flaky test: {nodeid} with outcomes: {self.flaky_tests[nodeid]}")

        # Continue with pytest's normal test execution after this hook
        yield


def pytest_addoption(parser):
    """Add command-line options for flaky test detection."""
    parser.addoption(
        "--detect-flaky",
        action="store_true",
        default=False,
        help="Enable flaky test detection.",
    )
    parser.addoption(
        "--reorder-runs",
        action="store",
        default=3,
        help="Number of times to rerun tests for flaky detection.",
    )
    parser.addoption(
        "--time-freeze-values",
        action="store",
        default="2024-01-01,2024-12-31",
        help="Comma-separated list of frozen times for flaky detection.",
    )
    parser.addoption(
        "--random-seeds",
        action="store",
        default="42,123,999",
        help="Comma-separated list of random seeds for flaky detection.",
    )


def pytest_configure(config):
    """Register the flaky test detector plugin."""
    if config.getoption("--detect-flaky"):
        detector = FlakyTestDetector(config)
        config.pluginmanager.register(detector, "flaky_test_detector")
