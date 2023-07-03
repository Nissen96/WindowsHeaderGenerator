from bs4 import BeautifulSoup
import requests
from typing import List, Dict


BASE_URL = "https://www.vergiliusproject.com"


def choose(prompt: str, options: List[str], suggestions: List[str] = None) -> str:
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
        return options[0]
    
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


def choose_from_website(prompt: str, url: str, cls: str, suggestions: List[str] = None) -> str:
    options = get_website_options(url, cls)
    choice = choose(prompt, list(options), suggestions)
    return options[choice]


def get_os(arch: str) -> str:
    return choose_from_website("Choose OS", f"/kernels/{arch}", "arch-link")


def get_version(os: str) -> str:
    return choose_from_website("Choose version", os, "fam-link")


def get_type(version: str) -> str:
    return choose_from_website(
        "Choose type",
        version,
        "list-link",
        suggestions=["_TEB", "_PEB"]
    )


def get_type_declaration(typ: str) -> BeautifulSoup:
    r = requests.get(f"{BASE_URL}{typ}")
    soup = BeautifulSoup(r.text, features="lxml")
    return soup.find(id="copyblock")


def get_type_declarations(base_type: str) -> List[str]:
    # Fetch code for chosen base type and all dependencies recursively
    type_declarations = []
    processed = {}
    remaining = {base_type.split("/")[-1]: base_type}
    ldr_data_table_entry = False

    nprocessed = 0
    while len(remaining) > 0:
        type_name, type_path = remaining.popitem()
        print(f"{'=' * 80}\nPROCESSING {type_name}\n{'=' * 80}")
        processed[type_name] = type_path
        type_decl = get_type_declaration(type_path)
        type_declarations.append(type_decl.text)

        type_paths = type_decl.find_all("a", class_="str-link")
        dependencies = {link.text.strip(): link["href"] for link in type_paths}
        print(f"Dependencies: {list(dependencies)}\n")

        # _LDR_DATA_TABLE_ENTRY is often not referenced, but is needed for _LIST_ENTRY
        if "_LIST_ENTRY" in dependencies and not ldr_data_table_entry:
            path = get_website_options(
                "/".join(type_path.split("/")[:-1]),
                "list-link"
            )["_LDR_DATA_TABLE_ENTRY"]
            dependencies["_LDR_DATA_TABLE_ENTRY"] = path
            ldr_data_table_entry = True

        # Only add not yet processed dependencies for handling
        remaining |= {dep: path for dep, path in dependencies.items() if dep not in processed}
        nprocessed += 1
        
        print(f"Processed: {list(processed)}")
        print(f"Remaining: {list(remaining)}\n")

    print(f"\nFetched a total of {nprocessed} new types")

    return type_declarations


def write_header_file(filename: str, types: List[str]) -> None:
    types.insert(0, "typedef void VOID;")
    header = "\n\n".join(types)
    with open(filename, "w") as f:
        f.write(header)


def main():
    arch = choose("Choose system architecture", ("x64", "x86"))
    os = get_os(arch)
    version = get_version(os)
    typ = get_type(version)
    types = get_type_declarations(typ)
    suggested_filename = f"{typ.split('/')[-1].lower().strip('_')}.h"
    filename = input(f"Output file (default: {suggested_filename})\n> ") or suggested_filename
    write_header_file(filename, types)


if __name__ == "__main__":
    main()
