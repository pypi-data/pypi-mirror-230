## 0.3.0.dev1 - 2023-09-14

### Added

- Added support for XML output. XML input is yet to be implemented.

## 0.2.1 - 2023-05-20

### Fixed

- Fixed special unicode characters on JSON output

## 0.2.0 - 2023-04-28

### Added

- Added custom error message when TOML writer tries to convert invalid data.
The input data should be a dictionary.

## 0.1.1 - 2023-04-22

### Fixed

- Fixed lib import. The previous version didn't import the parse and write
functions correctly.
- Warn the user when writing to output file in an unrecognized format.

## 0.1.0 - 2023-04-22

### Added

- Released version 0.1. The cli application freely converts from and to JSON,
YAML and TOML.
