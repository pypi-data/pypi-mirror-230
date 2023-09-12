import gzip
import logging
from typing import Iterator, Optional


from vcf_handler.utils.read_write import (
    check_vcf,
    read_variants,
    write_csv,
)
from vcf_handler.utils.Variant import format_variant


def process_vcf(vcf_in: str, csv_out="output.csv"):
    """
    Process a VCF file and write annotated variants to a CSV file
        Read in using a generator as well as write out using a generator to optimize memory usage
    """
    handle = "vcf-handling"
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(handle)

    check_vcf(vcf_in, log)

    with gzip.open(vcf_in, "rt") if vcf_in.endswith(".gz") else open(vcf_in, "r") as f:
        input_variants = read_variants(f)

        def output_variants_gen() -> Iterator[Optional[str]]:
            for variant in input_variants:
                formatted_variant = format_variant(variant, log)
                if isinstance(formatted_variant, list):
                    for fv in formatted_variant:
                        yield fv
                else:
                    yield formatted_variant

        output_variants = output_variants_gen()

        written_line_count = write_csv(
            output_variants,
            f"{csv_out}",
            log,
        )
    log.info(f"Wrote {written_line_count} variants to {csv_out}")
    return
