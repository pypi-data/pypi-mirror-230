import sys
import argparse

from triade.lib import parse, write


FORMAT_LIST = ["json", "yaml", "toml", "xml"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", nargs="?", type=argparse.FileType("r"),
                        default=sys.stdin)
    parser.add_argument("-o", "--output-file", type=argparse.FileType("w"),
                        default=sys.stdout)
    parser.add_argument("-I", "--input-format", default=None)
    parser.add_argument("-O", "--output-format", default=None)

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    input_ext = input_file.name.split(".")[-1] \
        if input_file is not sys.stdin else None
    input_ext = "yaml" if input_ext == "yml" else input_ext

    output_ext = output_file.name.split(".")[-1] \
        if output_file is not sys.stdout else None
    output_ext = "yaml" if output_ext == "yml" else output_ext

    input_format = input_ext \
        if args.input_format is None else args.input_format
    output_format = output_ext \
        if args.output_format is None else args.output_format


    if input_format is None:
        input_format=input_ext

    if input_format not in FORMAT_LIST:
        print("Error: input format not recognized", file=sys.stderr)
        print(f"Valid formats: {FORMAT_LIST}", file=sys.stderr)
        return 1

    if args.output_format not in [*FORMAT_LIST, None]:
        print("Error: output format not recognized", file=sys.stderr)
        print(f"Valid formats: {FORMAT_LIST}", file=sys.stderr)
        return 1

    input_data = input_file.read()

    if output_format is None:
        output_data = parse(input_data, input_format)
    elif output_ext is not None and output_format not in FORMAT_LIST:
        output_data = parse(input_data, input_format)
        print("Warning: the output file's format is not recognized. Defaulting to object as standard format.",
              file=sys.stderr)
    else:
        parsed_data = parse(input_data, input_format)
        output_data = write(parsed_data, output_format)

    print(output_data, file=output_file)

    return 0
