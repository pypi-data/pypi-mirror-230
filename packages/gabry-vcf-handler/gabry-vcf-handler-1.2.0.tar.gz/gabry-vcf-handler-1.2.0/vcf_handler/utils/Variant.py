from logging import Logger
from vcf_handler.utils.vep_helpers import (
    get_vep_data,
    get_vep_gene,
    get_vep_variant_class,
    get_vep_variant_effect,
    get_vep_maf,
)


class Variant:
    def __init__(self, fields):
        self.chr = fields[0]
        self.pos = fields[1]
        self.rsid = fields[2]
        self.ref = fields[3]
        self.alt = fields[4]
        self.qual = fields[5]
        self.filt = fields[6]
        self.info = {x.split("=")[0]: x.split("=")[1] for x in fields[7].split(";") if "=" in x}
        self.frmt = fields[8].split(":")
        self.smpl = fields[9].split(":")
        self.multi_allelic = False
        self.outbound_annotations = {
            "total_site_depth": "N/A",
            "supporting_variant_depth": "N/A",
            "variant_allele_frequency": "N/A",
            "vep_gene": "N/A",
            "vep_variant_class": "N/A",
            "vep_variant_effect": "N/A",
            "minor_allele_frequency": "N/A",
        }

    def scrape_total_depth(self, log):
        # Scrape depth of sequence coverage at the site of variation from the TC field in the INFO column
        depth = self.info.get("TC", "N/A")
        if depth != "N/A":
            self.outbound_annotations.update({"total_site_depth": int(depth)})
        return self

    def scrape_variant_depth(self, log):
        # Scrape number of reads supporting the variant from the NV field in the FORMAT column
        frmt_smpl_dict = dict(zip(self.frmt, self.smpl))
        var_depth = frmt_smpl_dict.get("NV", "N/A")
        if var_depth != "N/A":
            self.outbound_annotations.update({"supporting_variant_depth": int(var_depth)})
        return self

    def calculate_variant_allele_frequency(self, log):
        # Calculate percentage of reads supporting the variant from the NV and TC fields
        total_depth = self.outbound_annotations.get("total_site_depth")
        var_depth = self.outbound_annotations.get("supporting_variant_depth")

        if total_depth != "N/A" and var_depth != "N/A":
            vaf = float(var_depth / total_depth)
            self.outbound_annotations.update({"variant_allele_frequency": vaf})

        return self

    def get_vep_annotations(self, log):
        vep_data = get_vep_data(f"{self.chr}:g.{self.pos}{self.ref}>{self.alt}")

        variant_class = get_vep_variant_class(self.ref, self.alt)
        self.outbound_annotations.update({"vep_variant_class": variant_class})

        if vep_data:
            gene_id = get_vep_gene(vep_data)
            self.outbound_annotations.update({"vep_gene": gene_id})

            variant_effect = get_vep_variant_effect(vep_data)
            self.outbound_annotations.update({"vep_variant_effect": variant_effect})

            maf = get_vep_maf(vep_data, self.alt)
            self.outbound_annotations.update({"minor_allele_frequency": maf})

        return self

    def assemble_variant(self):
        # Reassemble variant into csv row
        updated_variant = ",".join(
            [
                self.chr,
                self.pos,
                self.ref,
                self.alt,
                self.qual,
                self.filt,
            ]
            + [str(item) for item in self.outbound_annotations.values()]
        )
        return updated_variant


def check_formatting(var: str) -> Variant:
    # Loose formatting check, return as Variant class object
    split_var = var.split("\t")
    if len(split_var) != 10 or not split_var[1].isdigit():
        raise RuntimeError(f"Variant contains incorrect number, or invalid fields:  {var}")

    working_variant = Variant(split_var)
    return working_variant


def format_variant(variant: str, log: Logger):
    # Working variant
    wv = check_formatting(variant)

    # Multi-allelic check and handle
    if wv.alt.count(",") > 0:
        updated_variants = []
        for i in range(wv.alt.count(",") + 1):
            # Decomp sample
            decomp_sample = []
            for sample_list in wv.smpl:
                if len(sample_list.split(",")) > 1:
                    decomp_sample.append(sample_list.split(",")[i])
                else:
                    decomp_sample.append(sample_list)

            new_wv = check_formatting(
                "\t".join(
                    [
                        wv.chr,
                        wv.pos,
                        wv.rsid,
                        wv.ref,
                        wv.alt.split(",")[i],
                        wv.qual,
                        wv.filt,
                        ";".join([f"{k}={v}" for k, v in wv.info.items()]),
                        ":".join(wv.frmt),
                        ":".join(decomp_sample),
                    ]
                )
            )
            new_wv.scrape_total_depth(log)
            new_wv.scrape_variant_depth(log)
            new_wv.calculate_variant_allele_frequency(log)
            new_wv.get_vep_annotations(log)
            updated_variant = new_wv.assemble_variant()
            updated_variants.append(updated_variant)

        return updated_variants

    else:
        wv.scrape_total_depth(log)
        wv.scrape_variant_depth(log)
        wv.calculate_variant_allele_frequency(log)
        wv.get_vep_annotations(log)
        updated_variant = wv.assemble_variant()
        return updated_variant
