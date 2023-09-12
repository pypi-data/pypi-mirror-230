"""
Command line interface implementation for the vcf-handler
"""

import argparse

from vcf_handler.process import process_vcf


def parse_arguments():
    """
    Parse and handle CLI arguments
    """
    parser = argparse.ArgumentParser(
        description="Convert VCF to CSV with additional annotations",
    )

    parser.add_argument(
        "-i",
        "--vcf_in",
        metavar="vcf_in",
        required=True,
        help="VCF file to process. Maybe be in .vcf, .txt, " ".vcf.gz, or .txt.gz format.",
    )
    parser.add_argument(
        "-o",
        "--csv_out",
        metavar="csv_out",
        required=False,
        default="output.csv",
        help="CSV file to output. Maybe be in .csv or .csv.gz format.",
    )

    args = parser.parse_args()
    return args


def process():
    """
    Entry point
    """
    args = parse_arguments()
    try:
        process_vcf(args.vcf_in, args.csv_out)
    except Exception as err:
        raise SystemExit(err)
