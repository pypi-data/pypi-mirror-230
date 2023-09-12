from typing import Optional


def filter_line(line: Optional[str], filters: str) -> Optional[str]:
    # Only keep user specified filters
    # Entries in VCF must strictly consist of allowed filters
    # e.g. filters = Pass:sb
    # entry = sb = KEPT
    # entry = sb;lowQ = DISCARDED

    if not line:
        return None

    allowed_filters = set(filters.split(":"))

    working_line = line.split("\t")
    working_filters = set(working_line[6].split(";"))

    # if both sets are exact matches, great, lets move on
    if working_filters == allowed_filters:
        return line

    # if they aren't exact matches and working_filter_set has more than one filter values
    # then we discard as we don't let combinations exist in the record for filter
    if len(working_filters) != 1:
        return None

    if len(allowed_filters.intersection(working_filters)) > 0:
        return line

    return None
