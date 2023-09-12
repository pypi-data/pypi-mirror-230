import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

import nbformat as nbf

from nbdump.helper import construct_mkdir_commands, dedup_folders, generate_target_files


def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("files", nargs="+", help="Files to write to notebook")
    parser.add_argument(
        "-o", "--out", type=Path, required=True, help="Filepath to dump (.ipynb)"
    )
    parser.add_argument(
        "-c", "--code", default=[], action="append", help="Extra code cell to add"
    )
    # TODO quiet + version? version need to quit immediately
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    files = generate_target_files(args.files)
    folders = dedup_folders(files)
    mkdir_cmds = construct_mkdir_commands(folders)

    ipynb_json = nbf.v4.new_notebook()

    # topmost mkdir cells
    if mkdir_cmds != "":
        mkdir_cell = nbf.v4.new_code_cell(mkdir_cmds)
        ipynb_json["cells"].append(mkdir_cell)

    # code cells from files
    for file in files:
        print(f"write: {file}")
        content = file.read_text()
        wf = f'%%writefile "{file}"\n{content}'.strip()
        code_cell = nbf.v4.new_code_cell(wf)
        ipynb_json["cells"].append(code_cell)

    # extra code cells
    for code in args.code:
        print(f"code: {code}")
        code_cell = nbf.v4.new_code_cell(code)
        ipynb_json["cells"].append(code_cell)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(ipynb_json, f)
