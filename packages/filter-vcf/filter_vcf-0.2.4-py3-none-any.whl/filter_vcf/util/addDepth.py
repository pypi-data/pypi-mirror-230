from typing import Optional


def add_depth_to_line(line: Optional[str]) -> Optional[str]:
    if not line or not len(line.split("\t")) > 1:
        return None

    working_line = line.split("\t")
    labels = working_line[8].split(":")
    values = working_line[9].split(":")

    if "DP" in labels or "AD" not in labels:
        return line

    variant_dict = dict(zip(labels, values))

    ad_values = variant_dict.get("AD", "").split(",")
    dp_value = sum([int(ad_value) for ad_value in ad_values])

    labels.append("DP")
    values.append(f"{dp_value}")

    working_line[8] = ":".join(labels)
    working_line[9] = ":".join(values)

    return "\t".join(working_line)
