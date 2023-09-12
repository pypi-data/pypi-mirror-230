# This file contains functions that are used to normalize a single VCF line.

import gzip
import os
from typing import Optional

from filter_vcf.util.userFilter import filter_line
from filter_vcf.util.addDepth import add_depth_to_line
from filter_vcf.util.removeNonRef import filter_non_ref_from_line
from filter_vcf.util.unique import keep_unique_line


def normalize_vcf_line(
    line: str, maybe_previous_line: Optional[str], arguments: dict
) -> Optional[str]:
    line = line.strip()

    maybe_normalized_line: Optional[str] = line

    if arguments["filters"] != "":
        maybe_normalized_line = filter_line(maybe_normalized_line, arguments["filters"])

    if arguments["depth"]:
        maybe_normalized_line = add_depth_to_line(maybe_normalized_line)

    # Always performed
    maybe_normalized_line = filter_non_ref_from_line(maybe_normalized_line)

    if arguments["unique"]:
        maybe_normalized_line = keep_unique_line(maybe_normalized_line, maybe_previous_line)

    return f"{maybe_normalized_line}\n" if maybe_normalized_line else None


def perform_line_normalization(in_file: str, tmp_dir: str, args: dict):
    os.rename(in_file, f"{tmp_dir}/working.vcf.gz")
    with gzip.open(f"{tmp_dir}/working.vcf.gz", "rt") as in_vcf:
        with gzip.open(in_file, "wt") as out_vcf:
            previous_line = None
            for line in in_vcf:
                if line.startswith("#"):
                    out_vcf.write(line)
                    continue
                normalized_line = normalize_vcf_line(line, previous_line, args)
                if normalized_line:
                    out_vcf.write(normalized_line)
                    previous_line = normalized_line
