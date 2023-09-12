import requests


def get_vep_data(variant_key) -> dict:
    url = f"https://rest.ensembl.org/vep/human/hgvs/{variant_key}?"
    headers = {"Content-Type": "application/json"}
    r = requests.get(url, headers=headers)

    if not r.ok:
        return {}

    vep_dict = r.json()
    return vep_dict[0]


def get_vep_gene(vep_data: dict) -> str:
    no_gene = "N/A"
    consequences = vep_data.get("transcript_consequences", {})
    if consequences:
        if isinstance(consequences, list):
            consequences = consequences[0]
        gene_symbol = consequences.get("gene_symbol", "N/A")
        if gene_symbol != "N/A":
            return gene_symbol
        else:
            gene_id = consequences.get("gene_id", "N/A")
            return gene_id
    return no_gene


def get_vep_variant_effect(vep_data: dict) -> str:
    variant_effect = vep_data.get("most_severe_consequence", "N/A")
    return variant_effect


def get_vep_maf(vep_data: dict, alt) -> str:
    maf = "N/A"
    colocated_vars = vep_data.get("colocated_variants")
    if colocated_vars:
        freqs = colocated_vars[0].get("frequencies")
        if freqs:
            target_var = freqs.get(alt)
            if target_var:
                maf = target_var.get("af", "N/A")
                return maf
    return maf


def get_vep_variant_class(ref, alt):
    if len(ref) == len(alt):
        variant_class = "SNV"
    elif len(ref) > len(alt):
        variant_class = "Deletion"
    else:
        variant_class = "Insertion"
    return variant_class
