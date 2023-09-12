import gzip
import subprocess

from filter_vcf.util.cleanAD import clean_ad
from filter_vcf.util.cleanGT import clean_gt


def decompose(in_file: str, tmp_dir: str):
    subprocess.run(
        f"vt decompose -s {in_file} -o {tmp_dir}/decomposed.vcf",
        shell=True,
        check=True,
    )
    with open(f"{tmp_dir}/decomposed.vcf", "rt") as in_vcf:
        with gzip.open(f"{in_file}.tmp", "wt") as out_vcf:
            for line in in_vcf:
                if line and line.startswith("#"):
                    out_vcf.write(line)
                    continue
                cleaned_line = clean_gt(line)
                cleaned_line = clean_ad(cleaned_line)
                if not cleaned_line:
                    continue
                out_vcf.write(cleaned_line)

    subprocess.run(
        f"bcftools view -Oz -o {in_file} {in_file}.tmp",
        shell=True,
        check=True,
    )
