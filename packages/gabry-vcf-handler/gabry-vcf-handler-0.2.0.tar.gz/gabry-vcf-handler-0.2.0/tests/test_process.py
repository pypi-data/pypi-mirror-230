from src.process import process_vcf
from logging import Logger
import filecmp
import unittest
import pytest
import os

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
OUT_PATH = f"{BASE_PATH}/data/out"


# Mock logging for testing
class MockLog:
    def info(self, _: str):
        return None

    def error(self, _: str):
        return None


mock_log = MockLog()


# System Level Tests
def test_process_vcf():
    out_file = f"{BASE_PATH}/data/out/test_vcf_data.csv"
    written_line_count = process_vcf(
        f"{BASE_PATH}/data/in/test_vcf_data.txt", out_file, log=mock_log
    )

    assert filecmp.cmp(out_file, f"{BASE_PATH}/data/expected/expected_output.csv") == True
    assert written_line_count == 6
    os.remove(out_file)


def test_standardize_bad_vcf():
    out_file = f"{BASE_PATH}/data/out/bad_vars.csv"
    with pytest.raises(RuntimeError) as pytest_wrapped_e:
        written_line_count = process_vcf(
            f"{BASE_PATH}/data/in/bad_vars.vcf",
            out_file,
            log=mock_log,
        )
    assert pytest_wrapped_e.type == RuntimeError
