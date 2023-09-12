import argparse
from pathlib import Path
import sys

from ecghelper.convert import convert

def parse_arguments(arguments: list) -> argparse.Namespace:
    """Initialize argument parser and sub-argument parsters."""
    parser = argparse.ArgumentParser(description="mimic command line interface")

    subparsers = parser.add_subparsers(dest="action", title="action")
    subparsers.required = True

    # === convert a dataset
    convert = subparsers.add_parser(
        "convert", help="Convert a dataset into a common HDF5 format."
    )
    convert.add_argument(
        "-i", "--input", type=str, required=True, help="Source record."
    )
    convert.add_argument(
        "-f", "--format", type=str, required=True, help="Source record format."
    )
    convert.add_argument(
        "-o", "--output", type=str, required=True, help="Output directory."
    )
    convert.add_argument(
        "-t", "--target", type=str, required=False, help="Target record format."
    )

    return parser.parse_args(arguments)


def convert_cli(args):
    """Convert a dataset into a simple HDF5 format."""
    source_record = Path(args.input)
    source_format = args.format
    target_record = Path(args.output)
    target_format = args.target

    # convert the dataset
    convert(source_record, source_format, target_record, target_format)


def main_cli(argv=sys.argv):
    # load in a trained model
    args = parse_arguments(argv[1:])

    # convert the dataset
    convert_cli(args)


if __name__ == "__main__":
    main_cli()
