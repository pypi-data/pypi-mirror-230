from heapq import merge
import gzip
from natsort import natsorted, natsort_keygen
from pathlib import Path
import subprocess


def get_sort_key(row: str):
    split_row = row.strip().split("\t")
    return (split_row[0], int(split_row[1]), split_row[3], split_row[4])


def write_chunk(lines: list[str], chunk_number: int, out_dir: str) -> str:
    chunk_file = f"{out_dir}/chunk_{chunk_number}.vcf.gz"
    with gzip.open(chunk_file, "wt") as out_file:
        out_file.writelines(natsorted(lines, key=get_sort_key))
    return chunk_file


def sort_vcf(vcf_file: str, working_dir: str, out_vcf: str, chunk_size: int = 100_000):
    # Make working_dir if it doesn't exist
    Path(working_dir).mkdir(parents=True, exist_ok=True)

    header_lines = []
    lines = []

    chunks = []
    chunk_number = 0
    # Handle opening both gzipped and non-gzipped files
    with gzip.open(vcf_file, "rt") if vcf_file.endswith("gz") else open(vcf_file, "rt") as in_file:
        line_num = 1
        for line in in_file:
            if line.startswith("#"):
                header_lines.append(line)
                continue
            lines.append(line)

            if line_num % chunk_size == 0:
                chunks.append(write_chunk(lines, chunk_number, working_dir))
                lines = []
                chunk_number += 1

            line_num += 1

    if lines:
        chunks.append(write_chunk(lines, chunk_number, working_dir))

    tmp_out_vcf = f"{working_dir}/tmp_out.vcf.gz"
    chunk_files = list(map(lambda x: gzip.open(x, "rt"), chunks))
    get_merge_key = natsort_keygen(get_sort_key)
    with gzip.open(tmp_out_vcf, "wt") as out_file:
        out_file.writelines(header_lines)
        out_file.writelines(merge(*chunk_files, key=get_merge_key))

    subprocess.run(f"bcftools view -Oz -o {out_vcf} {tmp_out_vcf}", shell=True, check=True)
