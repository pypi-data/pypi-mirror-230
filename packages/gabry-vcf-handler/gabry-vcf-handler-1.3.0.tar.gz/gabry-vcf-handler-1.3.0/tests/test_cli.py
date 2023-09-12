"""
Tests for the vcf-handler CLI
"""
from importlib import import_module

from unittest.mock import patch

import pytest
from cli_test_helpers import ArgvContext, shell

import vcf_handler.cli


def test_main_module():
    """
    Exercise the code in the ``__main__`` module.
    """
    import_module("vcf_handler.__main__")


def test_runas_module():
    """
    Can this package be run as a Python module?
    """
    result = shell("python -m vcf_handler --help")
    assert result.exit_code == 0


@patch("vcf_handler.process.process_vcf")
def test_args(mock_process_vcf):
    """
    Test I/O arguments are parsed correctly
    """
    with ArgvContext("process", "-i/vcf_in", "-o/csv_out"):
        args = vcf_handler.cli.parse_arguments()

    assert args.vcf_in == "/vcf_in"
    assert args.csv_out == "/csv_out"


@patch("vcf_handler.process.process_vcf")
def test_missing_out_arg(mock_process_vcf):
    """
    Test missing O arg is auto-populated
    """
    with ArgvContext("process", "-i/vcf_in"):
        args = vcf_handler.cli.parse_arguments()

    assert args.vcf_in == "/vcf_in"
    assert args.csv_out == "output.csv"


@patch("vcf_handler.process.process_vcf")
def test_missing_in_arg(mock_process_vcf):
    """
    Test missing I arg fails
    """
    with ArgvContext("process", "-o/csv_out"):
        with pytest.raises(SystemExit):
            vcf_handler.cli.parse_arguments()


def test_process():
    """
    Test process entry point
    """
    with ArgvContext("process", "-i/vcf_in", "-o/csv_out"):
        with pytest.raises(SystemExit):
            vcf_handler.cli.process()
