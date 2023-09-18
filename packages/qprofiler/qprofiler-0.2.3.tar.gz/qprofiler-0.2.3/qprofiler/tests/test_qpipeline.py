import pytest
from typing import Dict, Any
import os
import sys

sys.path.append(os.path.abspath("../.."))
from qprofiler import DataProfiler
from qprofiler import QTest
from qprofiler import QPipeline

DATA_PATH = "datasets/loan-perf.csv"
TEST_DATA_PATH = "datasets/loan-perf-test.csv"


@pytest.fixture
def profiler() -> DataProfiler:
    profiler = DataProfiler()
    ref = profiler.scan_csv_file(DATA_PATH, unique_identifier="customerid")
    profiler.create_profile(ref, "reference", True)
    return profiler


@pytest.fixture
def checks(profiler: DataProfiler) -> QTest:
    return QTest(profile_path=profiler.profiler_config.joinpath("reference.yml"))


@pytest.fixture
def test_profile(checks: QTest) -> Dict:
    return checks.scan_csv_file(TEST_DATA_PATH, unique_identifier="customerid")


def test_missing_pipeline_params() -> None:
    with pytest.raises(TypeError):
        QPipeline(varbose=True)


def test_append_wrong_error_level(checks: QTest, test_profile: Dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        pipeline = QPipeline(test_obj=checks)
        pipeline.append(
            name="check_columns",
            check=checks.check_columns,
            error_level="hint",
            test_profile=test_profile,
        )


def test_append_wrong_method(test_profile: Dict[str, Any]) -> None:
    def func(x):
        return x * 2

    with pytest.raises(TypeError):
        pipeline = QPipeline(test_obj=checks)
        pipeline.append(
            name="check_columns",
            check=func,
            error_level="hint",
            test_profile=test_profile,
        )


def test_append_3_tests(checks: QTest, test_profile: Dict[str, Any]) -> None:
    pipeline = QPipeline(test_obj=checks)
    pipeline.append(
        name="check_columns",
        check=checks.check_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_if_matched_const_columns",
        check=checks.check_if_matched_const_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_row_duplicates",
        check=checks.check_row_duplicates,
        error_level="error",
        test_profile=test_profile,
    )
    assert len(pipeline.tests) == 3


def test_clear_pipeline(checks: QTest, test_profile: Dict[str, Any]) -> None:
    pipeline = QPipeline(test_obj=checks)
    pipeline.append(
        name="check_columns",
        check=checks.check_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_if_matched_const_columns",
        check=checks.check_if_matched_const_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_row_duplicates",
        check=checks.check_row_duplicates,
        error_level="error",
        test_profile=test_profile,
    ).clear_pipeline()
    assert len(pipeline.tests) == 0


def test_remove_one_test(checks: QTest, test_profile: Dict[str, Any]) -> None:
    pipeline = QPipeline(test_obj=checks)
    pipeline.append(
        name="check_columns",
        check=checks.check_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_if_matched_const_columns",
        check=checks.check_if_matched_const_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_row_duplicates",
        check=checks.check_row_duplicates,
        error_level="error",
        test_profile=test_profile,
    ).remove_step(
        name="check_if_matched_const_columns"
    )
    assert pipeline.tests == ["check_columns", "check_row_duplicates"]


def test_running_failed_pipeline(checks: QTest, test_profile: Dict[str, Any]) -> None:
    pipeline = QPipeline(test_obj=checks)
    pipeline.append(
        name="check_columns",
        check=checks.check_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_if_matched_const_columns",
        check=checks.check_if_matched_const_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_row_duplicates",
        check=checks.check_row_duplicates,
        error_level="error",
        test_profile=test_profile,
    )
    res = pipeline.run()
    assert res == False


def test_running_success_pipeline(checks: QTest, test_profile: Dict[str, Any]) -> None:
    pipeline = QPipeline(test_obj=checks)
    pipeline.append(
        name="check_columns",
        check=checks.check_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_if_matched_const_columns",
        check=checks.check_if_matched_const_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_row_duplicates",
        check=checks.check_row_duplicates,
        error_level="error",
        test_profile=test_profile,
    ).remove_step(
        name="check_columns"
    )
    res = pipeline.run()
    assert res == True


def test_running_warn_error_msg_success_pipeline(
    checks: QTest, test_profile: Dict[str, Any]
) -> None:
    pipeline = QPipeline(test_obj=checks)
    pipeline.append(
        name="check_columns",
        check=checks.check_columns,
        error_level="warn",
        test_profile=test_profile,
    ).append(
        name="check_if_matched_const_columns",
        check=checks.check_if_matched_const_columns,
        error_level="error",
        test_profile=test_profile,
    ).append(
        name="check_row_duplicates",
        check=checks.check_row_duplicates,
        error_level="error",
        test_profile=test_profile,
    )
    res = pipeline.run()
    assert res == True
