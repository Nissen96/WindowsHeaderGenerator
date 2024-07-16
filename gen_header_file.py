from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Set

import requests


BASE_URL = "https://www.vergiliusproject.com"

# Known unreferenced special cases, must be added manually
UNREFERENCED = {
    "_PEB_LDR_DATA": ["_LDR_DATA_TABLE_ENTRY"]  # Only references LIST_ENTRY
}


class Kind(Enum):
    ENUM = "enum"
    STRUCT = "struct"
    UNION = "union"


@dataclass(unsafe_hash=True)
class Type:
    name: str
    path: str = field(compare=False)
    kind: Kind = field(init=False, compare=False)
    declaration: str = field(init=False, compare=False, repr=False)


def choose(prompt: str, options: List[str], suggestions: Iterable[str] = None) -> str:
    # First option is default
    print(f"{prompt} (default: {options[0]}):")
    for i, o in enumerate(options):
        print(f"  {i}) {o}")

    if suggestions is not None:
        allowed = [s for s in suggestions if s in options]
        if len(allowed) > 0:
            print(f"\nInput index OR exact option (e.g. {' / '.join(allowed)}):")

    choice = input("> ").strip()
    print()

    if choice == "":
        return options[0]  # default

    if choice in options:
        return choice

    if int(choice) in range(len(options)):
        return options[int(choice)]

    raise ValueError(f"Choice must be in options or in range 0..{len(options) - 1}")


def get_website_options(path: str, cls: str) -> Dict[str, str]:
    r = requests.get(f"{BASE_URL}{path}")
    soup = BeautifulSoup(r.text, features="lxml")
    links = soup.find_all("a", class_=cls)
    return {a.text: a["href"] for a in links}


def choose_from_website(prompt: str, url: str, cls: str) -> str:
    options = get_website_options(url, cls)
    choice = choose(prompt, list(options))
    return choice, options[choice]


def choose_os(arch: str) -> str:
    return choose_from_website("Choose OS", f"/kernels/{arch}", "arch-link")[1]


def choose_version(os: str) -> str:
    return choose_from_website("Choose version", os, "fam-link")[1]


def choose_kernel() -> str:
    arch = choose("Choose system architecture", ("x64", "x86"))
    os = choose_os(arch)
    version = choose_version(os)
    return version


def get_types(version: str) -> Dict[str, Type]:
    options = get_website_options(version, "list-link")
    return {name: Type(name, path) for name, path in options.items()}


def choose_type(types: Dict[str, Type]) -> Type:
    type_choice = choose("Choose type", list(types), suggestions=["_TEB", "_PEB"])
    return types[type_choice]


def parse_datatype(datatype: Type, all_types: Dict[str, Type]) -> Set[Type]:
    """
    Fetch and set the declaration of the provided datatype
    and find its dependencies (including unreferenced, manually)
    """
    r = requests.get(f"{BASE_URL}{datatype.path}")
    soup = BeautifulSoup(r.text, features="lxml")
    code = soup.find(id="copyblock")

    declaration = code.text.strip()
    datatype.declaration = declaration
    datatype.kind = Kind(declaration.split("\n")[1].split()[0])

    type_references = code.find_all("a", class_="str-link")
    dependencies = set()
    for ref in type_references:
        dependencies.add(all_types[ref.text.strip()])

    # Manually add known unreferenced dependencies
    for ref in UNREFERENCED.get(datatype.name, []):
        dependencies.add(all_types[ref])

    return dependencies


def process_type(base_type: Type, all_types: List[Type]) -> Set[Type]:
    """
    Process type and dependencies recursively
    until no references are unhandled
    """
    remaining = {base_type}
    processed = set()

    nprocessed = 0
    while len(remaining) > 0:
        datatype: Type = remaining.pop()
        print(f"Processing {datatype.name}...")
        processed.add(datatype)
        dependencies = parse_datatype(datatype, all_types)
        nprocessed += 1

        # Only add unprocessed dependencies for handling
        remaining |= dependencies - processed

    print(f"\nFetched a total of {nprocessed} types\n")

    return processed


def write_header_file(filename: str, types: Iterable[Type]) -> None:
    with open(filename, "w") as f:
        f.write("typedef void VOID;\n")

        # Write typedefs for all types to avoid ordering and cyclic issues
        for t in types:
            f.write(f"typedef {t.kind.value} {t.name} {t.name};\n")

        for t in types:
            f.write(f"\n\n{t.declaration}")


def main():
    kernel_version = choose_kernel()
    all_types = get_types(kernel_version)
    base_type = choose_type(all_types)
    processed_types = process_type(base_type, all_types)

    suggested_filename = f"{base_type.name.strip('_').lower()}.h"
    print(f"Output file (default: {suggested_filename})")
    filename = input("> ") or suggested_filename
    write_header_file(filename, processed_types)


if __name__ == "__main__":
    main()
