from typing import Optional


def keep_unique_line(line: Optional[str], previous_line: Optional[str]) -> Optional[str]:
    if not line:
        return None

    if not previous_line:
        return line

    current_key = ":".join(line.split("\t")[0:5])
    previous_key = ":".join(previous_line.split("\t")[0:5])

    # Check if current_key is the same as the previous_key
    if current_key == previous_key:
        return None

    return line
