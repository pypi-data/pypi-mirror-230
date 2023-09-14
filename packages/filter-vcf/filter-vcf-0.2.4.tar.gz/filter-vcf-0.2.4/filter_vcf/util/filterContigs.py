from logging import Logger
import os
import subprocess

regions = ",".join(
    ["chr" + str(i) for i in range(1, 23)]
    + [str(i) for i in range(1, 23)]
    + ["X", "Y", "M", "MT", "chrX", "chrY", "chrM", "chrMT"]
)


def filter_contigs(in_file: str, tmp_dir: str, log: Logger):
    log.info("Indexing with tabix")
    subprocess.run(f"tabix -p vcf {in_file}", shell=True, check=True)
    log.info("Filtering contigs")
    subprocess.run(
        f'bcftools view  -r "{regions}" {in_file} -o {tmp_dir}/regions.vcf.gz -O z ',
        shell=True,
        check=True,
    )
    os.rename(f"{tmp_dir}/regions.vcf.gz", in_file)
