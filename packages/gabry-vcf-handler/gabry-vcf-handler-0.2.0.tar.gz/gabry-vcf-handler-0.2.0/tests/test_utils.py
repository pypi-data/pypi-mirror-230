from src.utils.read_write import (
    write_csv,
    check_vcf,
    read_variants,
)
from src.utils.Variant import Variant
from src.utils.vep_helpers import (
    get_vep_data,
    get_vep_gene,
    get_vep_variant_class,
    get_vep_variant_effect,
)
import os
from pathlib import Path
import logging
import unittest
import filecmp
import pytest
from copy import deepcopy


BASE_PATH = os.path.abspath(os.path.dirname(__file__))


# Mock logging for testing
class MockLog:
    def info(self, _: str):
        return None

    def error(self, _: str):
        return None


mock_log = MockLog()


def test_read_variants():
    with open(f"{BASE_PATH}/data/in/read_write.txt", "r") as f:
        variants = read_variants(f)

        assert list(variants) == [
            "1	1158631	.	A	G	2965	PASS	BRF=0.16;FR=1.0000	GT:GL	1/1:-300.0,-43.88,0.0",
            "1	1246004	.	A	G	2965	PASS	BRF=0.09;FR=1.0000	GT:GL	1/1:-300.0,-41.24,0.0",
        ]


def test_check_vcf():
    with pytest.raises(RuntimeError) as e:
        check_vcf(f"{BASE_PATH}/data/in/does_not_exist.vcf", mock_log)

    assert (
        str(e.value)
        == f'Given file path "{BASE_PATH}/data/in/does_not_exist.vcf" could not be located'
    )

    with pytest.raises(RuntimeError) as e:
        check_vcf(f"{BASE_PATH}/data/in/read_write.tsv", mock_log)

    assert (
        str(e.value)
        == f'Given file "{BASE_PATH}/data/in/read_write.tsv" must be in vcf, txt, vcf.gz, or txt.gz format'
    )


def test_write_csv():
    variants = [
        "1	35885022	rs1474253187	T	C	.	.   Test",
        "2	44622946	rs9291422989	C	G	.	.	Test",
        "9	30912459	rs1330713521	A	G	.	.	Test",
        "1	42641414	rs1006891614	C	T	.   .	Test",
    ]

    written_line_count = write_csv(
        variants,
        f"{BASE_PATH}/data/out/written.csv",
        log=mock_log,
    )
    assert os.path.exists(f"{BASE_PATH}/data/out/written.csv") == True

    assert written_line_count == 4

    os.remove(f"{BASE_PATH}/data/out/written.csv")


def test_assemble_row():
    variant = Variant(
        [
            "chr1",
            "01",
            ".",
            "C",
            "T",
            "2500",
            "PASS",
            "FAKE=INFO",
            "FAKE:FORMAT",
            "000:111",
        ]
    )

    assembled_variant = variant.assemble_variant()
    assert assembled_variant == "chr1,01,C,T,2500,PASS,N/A,N/A,N/A,N/A,N/A,N/A,N/A"


def test_get_vep_data():
    vep_data = get_vep_data("chr1:g.1000A>T")
    assert vep_data == {}


def test_get_vep_gene():
    vep_data = {
        "transcript_consequences": [
            {
                "gene_symbol": "FAKE_GENE",
                "gene_id": "FAKE_GENE_ID",
            }
        ]
    }
    gene = get_vep_gene(vep_data)
    assert gene == "FAKE_GENE"


def test_get_vep_gene_no_gene_symbol():
    vep_data = {
        "transcript_consequences": [
            {
                "gene_id": "FAKE_GENE_ID",
            }
        ]
    }
    gene = get_vep_gene(vep_data)
    assert gene == "FAKE_GENE_ID"


def test_get_vep_variant_class():
    variant_class = get_vep_variant_class("A", "T")
    assert variant_class == "SNV"

    variant_class = get_vep_variant_class("A", "AT")
    assert variant_class == "Insertion"

    variant_class = get_vep_variant_class("AT", "A")
    assert variant_class == "Deletion"


def test_get_vep_variant_effect():
    vep_data = {"most_severe_consequence": "fake_consequence"}
    variant_effect = get_vep_variant_effect(vep_data)
    assert variant_effect == "fake_consequence"


def test_get_vep_varriant_effect_no_most_severe_consequence():
    vep_data = {}
    variant_effect = get_vep_variant_effect(vep_data)
    assert variant_effect == "N/A"


def test_get_vep_annotations():
    variant = Variant(
        [
            "chr1",
            "01",
            ".",
            "C",
            "T",
            "2500",
            "PASS",
            "FAKE=INFO",
            "NV:FORMAT",
            "000:111",
        ]
    )
    variant.get_vep_annotations(mock_log)
    assert variant.outbound_annotations.get("vep_gene") == "N/A"
    assert variant.outbound_annotations.get("vep_variant_class") == "SNV"
    assert variant.outbound_annotations.get("vep_variant_effect") == "N/A"
