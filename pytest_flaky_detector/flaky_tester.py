import pytest
import random
from datetime import datetime
from freezegun import freeze_time


class FlakyTestDetector:
    def __init__(self, config):
        self.config = config
        self.flaky_tests = {}
        self.reorder_runs = config.getoption("--reorder-runs", default=3)
        self.time_freeze_times = config.getoption("--time-freeze-values", default="2024-01-01,2024-12-31").split(",")
        self.random_seeds = config.getoption("--random-seeds", default="42,123,999").split(",")

    def record_test_result(self, nodeid, outcome):
        if nodeid not in self.flaky_tests:
            self.flaky_tests[nodeid] = set()
        self.flaky_tests[nodeid].add(outcome)

    def is_flaky(self, nodeid):
        outcomes = self.flaky_tests.get(nodeid, set())
        return len(outcomes) > 1  # Flaky if it produces more than one outcome


def pytest_addoption(parser):
    """Add options for flaky test detection."""
    parser.addoption(
        "--detect-flaky", action="store_true", default=False, help="Enable flaky test detection."
    )
    parser.addoption(
        "--reorder-runs", action="store", default=3, type=int, help="Number of reordering runs for flaky test detection."
    )
    parser.addoption(
        "--time-freeze-values",
        action="store",
        default="2024-01-01,2024-12-31",
        help="Comma-separated list of times to freeze during flaky detection.",
    )
    parser.addoption(
        "--random-seeds",
        action="store",
        default="42,123,999",
        help="Comma-separated list of seeds for flaky detection.",
    )


@pytest.hookimpl
def pytest_configure(config):
    if config.getoption("--detect-flaky"):
        detector = FlakyTestDetector(config)
        config.pluginmanager.register(detector, "flaky_test_detector")


@pytest.hookimpl
def pytest_collection_modifyitems(session, config, items):
    """Reorder tests randomly for flaky detection."""
    detector = config.pluginmanager.get_plugin("flaky_test_detector")
    if not detector:
        return

    # Shuffle test order for flaky detection
    random.shuffle(items)


@pytest.hookimpl
def pytest_runtest_protocol(item, nextitem):
    detector = item.config.pluginmanager.get_plugin("flaky_test_detector")
    if not detector:
        return None

    flaky_nodeid = item.nodeid

    # Detect flakiness by reordering
    for _ in range(detector.reorder_runs):
        item.ihook.pytest_runtest_setup(item=item)
        reports = item.ihook.pytest_runtest_call(item=item)
        for report in reports:
            detector.record_test_result(flaky_nodeid, report.outcome)
        item.ihook.pytest_runtest_teardown(item=item)

    # Detect flakiness by freezing time
    for time in detector.time_freeze_times:
        with freeze_time(time):
            item.ihook.pytest_runtest_setup(item=item)
            reports = item.ihook.pytest_runtest_call(item=item)
            for report in reports:
                detector.record_test_result(flaky_nodeid, report.outcome)
            item.ihook.pytest_runtest_teardown(item=item)

    # Detect flakiness by seeding random
    for seed in detector.random_seeds:
        random.seed(int(seed))
        item.ihook.pytest_runtest_setup(item=item)
        reports = item.ihook.pytest_runtest_call(item=item)
        for report in reports:
            detector.record_test_result(flaky_nodeid, report.outcome)
        item.ihook.pytest_runtest_teardown(item=item)

    if detector.is_flaky(flaky_nodeid):
        print(f"Detected flaky test: {flaky_nodeid} with outcomes: {detector.flaky_tests[flaky_nodeid]}")

    return True
