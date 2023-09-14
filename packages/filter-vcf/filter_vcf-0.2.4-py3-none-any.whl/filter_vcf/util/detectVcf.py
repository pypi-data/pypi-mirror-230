import gzip


def detect_vcf(vcf_file: str) -> str:
    # Detects whether variants are prefixed with 'chr' or not.
    # Return variable for input int convertChrName.py

    first_fields = set()

    with gzip.open(vcf_file, "rt") as in_file:
        for line in in_file:
            if line != "":
                if line.startswith("#"):
                    continue
                else:
                    working_line = line.split("\t")
                    first_fields.add(working_line[0])

    # Identify if we have any 'chr' first fields or not
    uniq_first_fields = [i for i in first_fields if i.startswith("chr")]
    if len(uniq_first_fields) == 0:
        return "num"
    else:
        return "chr"
