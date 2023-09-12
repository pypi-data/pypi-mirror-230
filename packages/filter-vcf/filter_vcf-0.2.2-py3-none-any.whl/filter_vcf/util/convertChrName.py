import gzip
import os
import subprocess
from typing import Literal


def convert_chr_name(in_vcf: str, chr_var: Literal["chr", "num"]):
    tmp_file = f"{in_vcf}.tmp"
    with gzip.open(in_vcf, "rt") as in_file:
        with gzip.open(tmp_file, "wt") as out_file:
            # Change MT -> M, add chr to every entry.
            for line in in_file:
                if line == "":
                    continue

                if line.startswith("#"):
                    out_file.write(line)
                    continue

                working_line = line.split("\t")
                chromosome = working_line[0]
                if chr_var == "chr":
                    # Change MT -> M, add chr to every entry.
                    if chromosome == "MT":
                        chromosome = "M"
                    converted_chromosome = "chr" + chromosome
                    working_line[0] = converted_chromosome
                else:
                    # Change M -> MT, remove chr from every entry.
                    converted_chromosome = chromosome.strip("chr")
                    if converted_chromosome == "M":
                        converted_chromosome = "MT"
                    working_line[0] = converted_chromosome
                joined = "\t".join(working_line)
                out_file.write(f"{joined}")

    os.remove(in_vcf)
    subprocess.run(
        f"bcftools view -Oz -o {in_vcf} {tmp_file}",
        shell=True,
        check=True,
    )
