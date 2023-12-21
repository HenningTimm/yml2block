# Lints

This file contains a list of all lints checked by yml2block.

| Rule Name               | Code | Test |
|-------------------------|------|------|
| `unique_names`          | b001 | Ensure that within a block (e.g. DatasetField) all names are unique. |
| `block_is_list`         | b002 | Ensure that each block content is a valid yaml list. |
| `keywords_valid`        | k001 | Ensure top level keywords (i.e. block names) are present and contain no typos. |
| `keywords_unique`       | k002 | Ensure no top level keyword occurs multiple times. |
| `keys_valid`            | e001 | Ensure that no invalid keys are present, e.g. through typos. |
| `required_keys_present` | e002 | Ensure that all required keys for the block entry are present (e.g. DatasetField has a name, etc. ...). |
| `no_substructures`      | e003 | Ensure entries in yaml format have no unexpected substructures but adhere to dataverse-compatible format. |
| `no_trailing_spaces`    | e004 | Ensure that block entries do not have trailing white spaces. |

