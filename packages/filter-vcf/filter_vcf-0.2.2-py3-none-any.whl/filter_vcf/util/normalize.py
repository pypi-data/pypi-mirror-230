from logging import Logger
import os
import subprocess

from filter_vcf.util.detectVcf import detect_vcf
from filter_vcf.util.convertChrName import convert_chr_name


def normalize(in_file: str, ref_file: str, tmp_dir: str, filter_contig: bool, log: Logger):
    vcfChr = detect_vcf(in_file)
    log.info(f"Input vcf file <{in_file}> has type <{ vcfChr }>")

    if vcfChr == "chr":
        convert_chr_name(in_file, "num")
        if os.path.exists(f"{in_file}.tbi"):
            os.remove(f"{in_file}.tbi")
        subprocess.run(f"tabix -p vcf {in_file}", shell=True, check=True)
        subprocess.run(
            f"vt normalize -n -r {ref_file} {in_file} -o {tmp_dir}/normalized.vcf",
            shell=True,
            check=True,
        )
        subprocess.run(f"gzip {tmp_dir}/normalized.vcf", shell=True, check=True)
        os.rename(f"{tmp_dir}/normalized.vcf.gz", in_file)
        convert_chr_name(in_file, "chr")

    else:
        if not filter_contig:
            subprocess.run(f"tabix -p vcf {in_file}", shell=True, check=True)
        subprocess.run(
            f"vt normalize -n -r {ref_file} {in_file} -o {tmp_dir}/normalized.vcf",
            shell=True,
            check=True,
        )
        subprocess.run(f"gzip {tmp_dir}/normalized.vcf", shell=True, check=True)
        os.rename(f"{tmp_dir}/normalized.vcf.gz", in_file)
