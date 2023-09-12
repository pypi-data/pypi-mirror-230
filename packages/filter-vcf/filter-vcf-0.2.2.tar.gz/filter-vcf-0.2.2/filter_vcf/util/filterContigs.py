import os
import subprocess

regions = ",".join(
    ["chr" + str(i) for i in range(1, 23)]
    + [str(i) for i in range(1, 23)]
    + ["X", "Y", "M", "MT", "chrX", "chrY", "chrM", "chrMT"]
)


def filter_contigs(in_file: str, tmp_dir: str):
    subprocess.run(f"tabix -p vcf {in_file}", shell=True, check=True)
    subprocess.run(
        f'bcftools view  -r "{regions}" {in_file} -o {tmp_dir}/regions.vcf.gz -O z ',
        shell=True,
        check=True,
    )
    os.rename(f"{tmp_dir}/regions.vcf.gz", in_file)
