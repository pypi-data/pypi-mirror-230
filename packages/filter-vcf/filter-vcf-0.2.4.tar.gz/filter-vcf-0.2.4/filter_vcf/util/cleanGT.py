from typing import Optional


def remove_gt_dot(line: Optional[str]) -> Optional[str]:
    # Check the GT in genotype field if there more than 2 entries,
    # remove "." values if total entries - number of "." == 2
    # otherwise leave it the same

    if not line:
        return None

    working_line = line.split("\t")

    labels = working_line[8].split(":")
    values = working_line[9].split(":")
    variant_dict = dict(zip(labels, values))

    gt_values = variant_dict.get("GT", "")

    # Detect and set separator
    sep = "|" if "|" in gt_values else "/"

    gt_split = gt_values.split(sep)

    # Processing if there are more than two values in GT array
    if len(gt_split) > 2:
        new_gt_vals = []
        dot_count = 0

        for item in gt_split:
            if item == ".":
                dot_count += 1
            else:
                new_gt_vals.append(f"{sep}{item}")

        if len(gt_split) - dot_count == 2:
            new_gt_string = "".join(new_gt_vals).strip(sep)
            variant_dict.update({"GT": new_gt_string})

            working_line[9] = ":".join(list(variant_dict.values()))
            return "\t".join(working_line)

        else:
            return line

    else:
        return line


def fix_gt_extra(line: Optional[str]) -> Optional[str]:
    # Check the alt field to be single value but the genotype field has more
    # than 2 entries or contain enumeration 2 or higher
    # e.g.
    # chr1	11138938	rs17417751	C	T	8355.2	PASS	.	GT:AD:DP:GQ:PL	0/0/1/1:324,290:617:99:8382,307,0,455,2147483647

    if not line:
        return None

    working_line = line.split("\t")

    alt = working_line[4].split(",")

    labels = working_line[8].split(":")
    values = working_line[9].split(":")
    variant_dict = dict(zip(labels, values))

    gt_values = variant_dict.get("GT", "")

    # Detect and set separator
    sep = "|" if "|" in gt_values else "/"

    gt_split = gt_values.split(sep)

    # Processing if there is a single ALT value and multiple GT values
    if len(alt) == 1 and len(gt_split) > 2:
        # Log each value, add to a list if it's novel. max length of two. return it.
        new_gt_vals: list[str] = []

        for item in gt_split:
            if item not in new_gt_vals and len(new_gt_vals) < 2:
                new_gt_vals.append(item)

        new_gt_string = f"{sep}".join(new_gt_vals)
        variant_dict.update({"GT": new_gt_string})

        working_line[9] = ":".join(list(variant_dict.values()))
        return "\t".join(working_line)

    else:
        return line


def clean_gt(line: Optional[str]) -> Optional[str]:
    cleaned = remove_gt_dot(line)
    cleaned = fix_gt_extra(cleaned)

    return cleaned
