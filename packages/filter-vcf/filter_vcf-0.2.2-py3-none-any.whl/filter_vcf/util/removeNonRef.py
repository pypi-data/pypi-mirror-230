from typing import Optional


def filter_non_ref_from_line(line: Optional[str]) -> Optional[str]:
    if not line:
        return None

    working_line = line.split("\t")
    if working_line[4] == "<NON_REF>":
        return None

    return line
