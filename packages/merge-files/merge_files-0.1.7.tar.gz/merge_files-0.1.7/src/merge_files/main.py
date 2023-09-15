#!/usr/bin/env python3
"""Merges the source file into the destination file.

Supports .env, text and binary files.
"""
import argparse
import os
import sys
from typing import List

from .mergers import get


def parse_args(command_line: List[str]) -> argparse.Namespace:
    """
    Parse the command line arguments, or a list of strings.

    Might call sys.exit() if the arguments are invalid.
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("source", help="The source file")
    parser.add_argument("dest", help="The destination file")
    parser.add_argument(
        "--update", help="Update values?", default=False, action="store_true"
    )

    return parser.parse_args(command_line)


def main():
    """
    Main entry point for the merge-files command line tool.
    """
    args = parse_args(sys.argv[1:])

    with open(args.source, "rb") as source_file:
        source = source_file.read()

    if not os.path.exists(args.dest):
        dest = b""
    else:
        with open(args.dest, "rb") as dest_file:
            dest = dest_file.read()

    merger = get(args.source, args.dest)
    output_data = merger(source, dest, args.update)

    with open(args.dest, "wb") as dest_file:
        dest_file.write(output_data)


if __name__ == "__main__":
    main()
