import re
import os
from typing import Iterator, Optional


def check_vcf(infile, log):
    log.info("Checking VCF file")
    # Check if file exists. Raise if it doesn't.
    if os.path.exists(infile) == False:
        raise RuntimeError(f'Given file path "{infile}" could not be located')

    if not (infile.endswith((".vcf", ".txt", ".vcf.gz", ".txt.gz"))):
        raise RuntimeError(f'Given file "{infile}" must be in vcf, txt, vcf.gz, or txt.gz format')


def read_variants(f) -> Iterator[str]:
    for line in f:
        record = re.sub(" ", "", line.rstrip("\r\n"))
        if record.startswith("#"):
            continue
        yield record


def write_csv(
    variants_gen: Iterator[Optional[str]],
    outfile: str,
    log,
):
    log.info(f"Writing annotated variants to {outfile}")

    written_line_count = 0
    with open(outfile, "wt") as w:
        w.write(
            "chromosome,position,ref,alt,qual,filter,total_site_depth,supporting_variant_depth,variant_allele_frequency,vep_gene,vep_variant_class,vep_variant_effect,minor_allele_frequency\n"
        )
        for variant in variants_gen:
            written_line_count += 1
            if variant:
                w.write(variant + "\n")

    return written_line_count
