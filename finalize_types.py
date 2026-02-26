import re
import sys
from pathlib import Path


def transform_file(file_path):
    print(f"Transforming {file_path}")
    content = Path(file_path).read_text()

    # Very flexible pattern to find Annotated[...] = None
    # We look for the start of Annotated, then the inner type, then RdfProperty, then end.

    # We'll use re.sub with a function that actually inspects the whole Annotated block.
    # Pattern: Annotated[ something ] = None
    pattern = re.compile(r"Annotated\[(.*?RdfProperty\(.*?\).*?)\] = None", re.DOTALL)

    def replacer(match):
        full_block = match.group(1)

        # Split into type part and property part.
        # Usually: type_part, RdfProperty(...)
        # But type_part might contain commas if it's a Union or has multiple args.
        # However, RdfProperty is usually the last (or only) metadata.

        prop_start = full_block.rfind("RdfProperty(")
        if prop_start == -1:
            return match.group(0)

        type_part = full_block[:prop_start].strip().rstrip(",")
        prop_part = full_block[prop_start:].strip()

        # Now analyze type_part. It should end with "| None" or "Optional[...]"
        # But here it's usually "Something | None" or "list[Something] | None"

        if "| None" not in type_part:
            # If it doesn't have | None, it might not be optional or uses Optional[]
            return match.group(0)

        inner_type = type_part.replace("| None", "").strip()

        # If it's already a flexible type, skip
        if " | list[" in inner_type:
            return match.group(0)

        # If it is just list[T], extract T
        list_match = re.match(r"list\[(.*)\]", inner_type)
        if list_match:
            base_type = list_match.group(1).strip()
            return f"Annotated[{base_type} | list[{base_type}] | None, {prop_part}] = None"

        # Otherwise it's a single type T, make it T | list[T]
        return f"Annotated[{inner_type} | list[{inner_type}] | None, {prop_part}] = None"

    new_content = pattern.sub(replacer, content)

    if new_content != content:
        Path(file_path).write_text(new_content)
        print(f"Updated {file_path}")
    else:
        print(f"No changes in {file_path}")


if __name__ == "__main__":
    files = sys.argv[1:]
    for f in files:
        transform_file(f)
