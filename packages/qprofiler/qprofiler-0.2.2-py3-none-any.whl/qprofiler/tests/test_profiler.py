import pytest
from pathlib import Path
import os
import sys

sys.path.append(os.path.abspath("../.."))
from qprofiler import DataProfiler

DATA_PATH = "datasets/loan-perf.csv"


@pytest.fixture
def profiler() -> DataProfiler:
    return DataProfiler()


def test_profiler_cwd_attribute(profiler: DataProfiler) -> None:
    assert profiler.cwd == Path(os.getcwd())


def test_profiler_path_attribute(profiler: DataProfiler) -> None:
    assert profiler.profiler_path == Path(os.getcwd())


def test_dprofiler_creation(profiler: DataProfiler) -> None:
    assert profiler.profiler_config.exists() == True


def test_dataset_profile_creation(profiler: DataProfiler) -> None:
    ref = profiler.scan_csv_file(DATA_PATH, unique_identifier="customerid")
    profiler.create_profile(ref, "reference")
    assert len(os.listdir(os.path.join(os.getcwd(), ".dprofiler"))) == 1


def test_dataset_profile_removal(profiler: DataProfiler) -> None:
    ref = profiler.scan_csv_file(DATA_PATH, unique_identifier="customerid")
    profiler.create_profile(ref, "reference")
    profiler.del_profile("reference")
    assert len(os.listdir(os.path.join(os.getcwd(), ".dprofiler"))) == 0


def test_exception_if_profile_not_exist(profiler: DataProfiler) -> None:
    with pytest.raises(FileNotFoundError):
        profiler.del_profile("reference")
