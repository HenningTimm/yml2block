# Changelog

## Version 0.8.0 (2025-01-01)

### Lint Changes

- Added lints (e005 and e006) to detect [nested compound metadata](https://github.com/IQSS/dataverse/issues/9911).
- Demote e004 to be a warning by default (Fixes https://github.com/HenningTimm/yml2block/issues/23).
  Since Dataverse 6.5, trailing whitespaces [are trimmed](https://github.com/IQSS/dataverse/pull/10696).
- Tweak `unique_title` (b003) lint to allow identical titles as long as
  they are part of different compound field. (Fixed https://github.com/HenningTimm/yml2block/issues/22)

### CLI Changes

- Add `--error` flag that allows warnings to be treated as errors instead.

### Test Changes

- Fixed multi version tests not working properly

### Other Changes

- Dropped support for Python versions below 3.12 for better string formatting (cf. [PEP 701](https://peps.python.org/pep-0701/))



## Version 0.7.0 (2024-12-10)

- Fixed bug where converting files without lint violations would result in an error (https://github.com/HenningTimm/yml2block/issues/16). Thanks @Athemis
- Fixed bug where non-string watermarks caused an error (https://github.com/HenningTimm/yml2block/issues/19). Thanks @Athemis
- Added minimal test for conversion function.
- Add tests to PRs.
- Add lint `b003` that checks if all titles within the DatasetField block are unique.


## Version 0.6.0 (2024-03-18)

- Added a CHANGELOG file.
- Switched yaml input to use the ruamel.yaml round trip parser.
  This parser is also "safe", i.e. does not allow code execution. 
- Added line numbers and columns to error messages where possible.
  For yaml files, these are taken from the ruamel.yaml round trip parser.
  For tsv files, the column names within the specified block are reported.
- Added `--strict` flag to the `convert` sub-command that prevents converting files that produced warnings.
- The rules `keys_valid` and `keys_unique` now correctly report their name in output.
- Added integration tests checking tsv files.
- Improved user feedback for parameters dealing with rule names, e.g. `--skip`.


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
