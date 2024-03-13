# Changelog

## Version 0.6.0 (2024-03-??)

- Added a CHANGELOG file.
- Switched yaml input to use the ruamel.yaml round trip parser.
  This parser is also "safe", i.e. does not allow code execution. 
- Added line numbers and columns to error messages where possible.
  For yaml files, these are taken from the ruamel.yaml round trip parser.
  For tsv files, the column names within the specified block are reported.
- Added `--strict` flag to the `convert` sub-command that prevents converting files that produced warnings.
- The rules `keys_valid` and `keys_unique` now correctly report their name in output.
- Added integration tests checking tsv files.


## Version 0.5.0 (2024-01-10)

- Improved documentation and user feedback
- Added option to check multiple files. You can now specify multiple input file paths for the check sub-command and those file paths can be glob patterns.
- Added suggestions for fixes to some lints.

Please note that the convert sub-command currently only works with one input file.


## Version 0.4.0 (2023-12-21)

- Added option to skip lints or reduce their severity to warning.
- Added first suggestions for fixes, e.g. minor typo detection with string matching.
- Added RULES.md to have a human readable documentation of employed lints.


## Version 0.3.0 (2023-12-05)

This release adds:

- Lints to detect trailing spaces
- Internal preparations to support multiple files
- Minor documentation improvements
