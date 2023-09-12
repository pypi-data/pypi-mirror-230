from vcf_handler.utils.read_write import (
    write_csv,
    check_vcf,
    read_variants,
)
from vcf_handler.utils.Variant import Variant, format_variant
from vcf_handler.utils.vep_helpers import (
    get_vep_data,
    get_vep_gene,
    get_vep_variant_class,
    get_vep_variant_effect,
    get_vep_maf,
)
import os
import pytest


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


def test_get_vep_maf():
    vep_data = {"colocated_variants": [{"frequencies": {"A": {"af": 0.0002}}}]}
    maf = get_vep_maf(vep_data, "A")
    assert maf == 0.0002


def test_get_vep_maf_negative_cases():
    vep_data = {}
    maf = get_vep_maf(vep_data, "A")
    assert maf == "N/A"
    vep_data = {"colocated_variants": []}
    maf = get_vep_maf(vep_data, "A")
    assert maf == "N/A"
    vep_data = {"colocated_variants": [{"frequencies": {}}]}
    maf = get_vep_maf(vep_data, "A")
    assert maf == "N/A"
    vep_data = {"colocated_variants": [{"frequencies": {"A": {}}}]}
    maf = get_vep_maf(vep_data, "A")
    assert maf == "N/A"
    vep_data = {"colocated_variants": [{"frequencies": {"A": {"af": "0.0002"}}}]}
    maf = get_vep_maf(vep_data, "T")
    assert maf == "N/A"


def test_get_vep_annotations():
    # Annotation of all except MAF
    variant = Variant(
        [
            "chr1",
            "13173106",
            ".",
            "A",
            "G",
            "2500",
            "PASS",
            "FAKE=INFO",
            "NV:FORMAT",
            "000:111",
        ]
    )
    variant.get_vep_annotations(mock_log)
    assert variant.outbound_annotations.get("vep_gene") == "PRAMEF9"
    assert variant.outbound_annotations.get("vep_variant_class") == "SNV"
    assert variant.outbound_annotations.get("vep_variant_effect") == "intron_variant"
    assert variant.outbound_annotations.get("minor_allele_frequency") == "N/A"

    # Annotation with MAF
    variant = Variant(
        [
            "chr2",
            "11053740",
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
    assert variant.outbound_annotations.get("vep_variant_effect") == "intergenic_variant"
    assert variant.outbound_annotations.get("minor_allele_frequency") == 0.0002


def test_scrape_total_depth():
    variant = Variant(
        [
            "chr1",
            "13173106",
            ".",
            "A",
            "G",
            "2500",
            "PASS",
            "TC=1000",
            "NV:FORMAT",
            "000:111",
        ]
    )
    variant.scrape_total_depth(mock_log)
    assert variant.outbound_annotations.get("total_site_depth") == 1000


def test_scrape_total_depth_missing():
    variant = Variant(
        [
            "chr1",
            "13173106",
            ".",
            "A",
            "G",
            "2500",
            "PASS",
            "FAKE=INFO",
            "NV:FORMAT",
            "000:111",
        ]
    )
    variant.scrape_total_depth(mock_log)
    assert variant.outbound_annotations.get("total_site_depth") == "N/A"


def test_scrape_variant_depth():
    variant = Variant(
        [
            "chr1",
            "13173106",
            ".",
            "A",
            "G",
            "2500",
            "PASS",
            "FAKE=INFO",
            "NV:FORMAT",
            "1000:111",
        ]
    )
    variant.scrape_variant_depth(mock_log)
    assert variant.outbound_annotations.get("supporting_variant_depth") == 1000


def test_scrape_variant_depth_missing():
    variant = Variant(
        [
            "chr1",
            "13173106",
            ".",
            "A",
            "G",
            "2500",
            "PASS",
            "FAKE=INFO",
            "FAKE:FORMAT",
            "000:111",
        ]
    )
    variant.scrape_variant_depth(mock_log)
    assert variant.outbound_annotations.get("supporting_variant_depth") == "N/A"


def test_calculate_variant_allele_frequency():
    variant = Variant(
        [
            "chr1",
            "13173106",
            ".",
            "A",
            "G",
            "2500",
            "PASS",
            "TC=1000",
            "NV:FORMAT",
            "1000:111",
        ]
    )
    variant.outbound_annotations.update(
        {"total_site_depth": 1000, "supporting_variant_depth": 1000}
    )
    variant.calculate_variant_allele_frequency(mock_log)
    assert variant.outbound_annotations.get("variant_allele_frequency") == 1.0


def test_calculate_variant_allele_frequency_missing():
    variant = Variant(
        [
            "chr1",
            "13173106",
            ".",
            "A",
            "G",
            "2500",
            "PASS",
            "TC=1000",
            "FAKE:FORMAT",
            "1000:111",
        ]
    )
    variant.calculate_variant_allele_frequency(mock_log)
    assert variant.outbound_annotations.get("variant_allele_frequency") == "N/A"


def test_format_variant():
    variant = "\t".join(
        [
            "chr1",
            "13173106",
            ".",
            "A",
            "G",
            "2500",
            "PASS",
            "TC=1000",
            "NV:FORMAT",
            "1000:111",
        ]
    )
    formatted_variant = format_variant(variant, mock_log)
    assert (
        formatted_variant
        == "chr1,13173106,A,G,2500,PASS,1000,1000,1.0,PRAMEF9,SNV,intron_variant,N/A"
    )


def test_format_variant_with_decomp():
    variant = "\t".join(
        [
            "chr1",
            "13173106",
            ".",
            "A",
            "G,T",
            "2500",
            "PASS",
            "TC=1000",
            "NV:FORMAT",
            "400,600:111",
        ]
    )
    formatted_variant = format_variant(variant, mock_log)
    assert formatted_variant == [
        "chr1,13173106,A,G,2500,PASS,1000,400,0.4,PRAMEF9,SNV,intron_variant,N/A",
        "chr1,13173106,A,T,2500,PASS,1000,600,0.6,PRAMEF9,SNV,intron_variant,N/A",
    ]
