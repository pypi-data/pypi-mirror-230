from typing import Optional


def clean_ad(line: Optional[str]) -> Optional[str]:
    # Re-compute AD (allelic depth) field for multi-allelic variants after decomposition

    if not line or line == "":
        return None

    working_line = line.split("\t")
    info = working_line[7]

    # Processing for if we find decomposed variants
    if "OLD_MULTIALLELIC" in info:
        labels = working_line[8].split(":")
        values = working_line[9].split(":")
        variant_dict = dict(zip(labels, values))

        gt_value = variant_dict.get("GT", "")
        ad_values = variant_dict.get("AD", "").split(",")

        new_ad_values = None

        if len(ad_values) == 2:
            new_ad_values = [ad_values[0], ad_values[1]]

        # First variant will correspond with first and second AD values
        elif gt_value == "1/.":
            new_ad_values = [ad_values[0], ad_values[1]]

        # Second variant will correspond with first and third AD values
        elif gt_value == "./1":
            new_ad_values = [ad_values[0], ad_values[2]]

        if new_ad_values:
            variant_dict.update({"AD": ",".join(new_ad_values)})

            working_line[9] = ":".join(list(variant_dict.values()))
            return "\t".join(working_line)

    return line
