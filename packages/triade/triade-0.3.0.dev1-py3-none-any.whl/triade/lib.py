import sys
import json

import yaml
import toml

from triade.xml_formatter import XML


def write_toml(input_data: object) -> str:
    if not isinstance(input_data, dict):
        print("Error: input data for TOML writer should be a dictionary",
              file=sys.stderr)
        sys.exit(1)

    return toml.dumps(input_data)


parsers = {
    "json": json.loads,
    "yaml": yaml.safe_load,
    "toml": toml.loads,
}

writers = {
    "json": lambda data: json.dumps(data, ensure_ascii=False),
    "yaml": lambda data: yaml.dump(data, Dumper=yaml.SafeDumper,
                                   allow_unicode=True),
    "toml": write_toml,
    "xml": XML.dumps,
}


def parse(input_data: str, data_format: str) -> object:
    if data_format not in parsers:
        raise ValueError("format not recognized")

    output_data = parsers[data_format](input_data)

    if data_format != "json":
        output_data = json.loads(json.dumps(output_data))

    return output_data


def write(input_data: object, data_format: str) -> str:
    if data_format not in writers:
        raise ValueError("format not recognized")

    return writers[data_format](input_data).strip()
