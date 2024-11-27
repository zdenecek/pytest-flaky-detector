import pytest
import random
from datetime import datetime
from freezegun import freeze_time
from _pytest.runner import runtestprotocol


def get_outcome_from_reports(reports):
    """Extract the outcome ('passed', 'failed', 'skipped') from test reports."""
    for report in reports:
        if report.failed:
            return 'failed'
        elif report.skipped:
            return 'skipped'
    return 'passed'


class FlakyTestDetector:
    def __init__(self, config):
        self.config = config
        self.flaky_tests = {}
        self.reorder_runs = config.getoption("--reorder-runs", default=3)
        self.time_freeze_times = config.getoption(
            "--time-freeze-values", default="2024-01-01,2024-12-31"
        ).split(",")
        self.random_seeds = config.getoption(
            "--random-seeds", default="42,123,999"
        ).split(",")

    def record_test_result(self, nodeid, outcome):
        if nodeid not in self.flaky_tests:
            self.flaky_tests[nodeid] = set()
        self.flaky_tests[nodeid].add(outcome)

    def is_flaky(self, nodeid):
        outcomes = self.flaky_tests.get(nodeid, set())
        return len(outcomes) > 1  # Flaky if it produces more than one outcome

    @pytest.hookimpl
    def pytest_runtest_protocol(self, item, nextitem):
        if not self.config.getoption("--detect-flaky"):
            return None

        flaky_nodeid = item.nodeid
        outcomes = set()

        # Original run
        reports = runtestprotocol(item, log=False)
        outcome = get_outcome_from_reports(reports)
        outcomes.add(outcome)
        self.record_test_result(flaky_nodeid, outcome)

        # Reordering runs (may not affect a single test item)
        for _ in range(self.reorder_runs):
            reports = runtestprotocol(item, log=False)
            outcome = get_outcome_from_reports(reports)
            outcomes.add(outcome)
            self.record_test_result(flaky_nodeid, outcome)

        # Time freezing runs
        for time_str in self.time_freeze_times:
            with freeze_time(time_str):
                reports = runtestprotocol(item, log=False)
                outcome = get_outcome_from_reports(reports)
                outcomes.add(outcome)
                self.record_test_result(flaky_nodeid, outcome)

        # Random seed runs
        for seed in self.random_seeds:
            random.seed(int(seed))
            reports = runtestprotocol(item, log=False)
            outcome = get_outcome_from_reports(reports)
            outcomes.add(outcome)
            self.record_test_result(flaky_nodeid, outcome)

        if len(outcomes) > 1:
            print(
                f"Detected flaky test: {flaky_nodeid} with outcomes: {outcomes}"
            )

        return True  # Skip normal test execution


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
        type=int,
        help="Number of reordering runs for flaky test detection.",
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


def pytest_configure(config):
    if config.getoption("--detect-flaky"):
        detector = FlakyTestDetector(config)
        config.pluginmanager.register(detector, "flaky_test_detector")
