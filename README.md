# yml2block

The yml2block script converts a YAML description of a dataverse-compliant
metadata schema into a Dataverse metadata block TSV file.
Additionally, it can lint both YAML and TSV metadata block files for common errors.


## Requirements and Installation

To use `yml2block` you will need the following Python packages

- ruamel.yaml
- click
- poetry (for installation)

and use Python 3.10 or newer.

Currently, the only way to install is from this GitHub repo.
After cloning, you can install `yml2block` and its requirements using `poetry`:

```bash
~ $ git clone https://github.com/HenningTimm/yml2block.git
~ $ cd yml2block
yml2block $ poetry install
```

This will install `yml2block` in your current Python environment
and give you access to the `yml2block` command line entry point.


### Conda

If you are using conda, the installation as shown above only works within a dedicated
environment other than `base`. For this, create a new conda environment:

```bash
~ (base) $ conda create -n y2b poetry
~ (base) $ conda activate y2b
# Clone and install as shown above [...]
yml2block (y2b) $ poetry install
```


## Usage

You can call the script directly (without installation) using `Python` from the cloned repository folder:

```bash
yml2block $ python yml2block --help
```

If you followed the installation instructions using poetry shown above,
you can also call `yml2block` directly:

```bash
~ $ yml2block convert path/to/inout_metadata_schema.yml -o path/to/dataverse_metadata_block.tsv
```

Additionally, you can use poetry to run yml2block:

```bash
~ $ poetry run yml2block convert path/to/inout_metadata_schema.yml -o path/to/dataverse_metadata_block.tsv
```


## Tests

Tests for yml2block are implemented using pytest and can be run as follows:

```bash
~ $ poetry install --extras tests
~ $ poetry run pytest -v tests/unit_tests.py
~ $ poetry run pytest -v tests/integration_tests.py
```


## Parameters and Subcommands

### Input

The path to the input file containing the metadata schema in YAML format
is given as the positional parameter.

For linting using the `yml2block check` subcommand, both YAML and TSV files
can be provided. For actually converting files using `yml2block convert`,
only YAML files may be passed.


### Output

By default, the output will be written to the same path as the input file,
replacing the `.yml`/ `.yaml` suffix with `.tsv`.

You can explicitly specify an output file name using the `-o file/path.tsv` parameter.


## Employed Lints

All checks performed during the `check` and `convert` commands are described in the file `RULES.md`.
Each rule can be toggled to be a warning instead of an error using the `--warn` parameter and
skipped entirely by using the `--skip` parameter. Both need to be followed by a rule name
or rule id. Both can be found in the file `RULES.md`.

```bash
~ $ yml2block check block_with_trailing_spaces.tsv
# Fails and returns error code 1

~ $ yml2block check --warn no_trailing_spaces block_with_trailing_spaces.tsv
# Completes with error code 0, but prints a warning

~ $ yml2block check --warn e004 block_with_trailing_spaces.tsv
# As above, but using a short rule code

~ $ yml2block check --skip no_trailing_spaces block_with_trailing_spaces.tsv
# Completes with error code 0, skips the whitespace check entirely
```


## YAML Metadata Schema Definition

An example for a valid YAML file can be found in `tests/minimal_working_example.yml`.
Such a file is expected to contain a YAML dictionary with three entries at the top level:
- `metadataBlock`
- `datasetField`
- `controlledVocabulary`
These define the three parts of a [Dataverse metadata block](https://guides.dataverse.org/en/latest/admin/metadatacustomization.html).

Each of these top-level entries contains a list of records, which are also dictionaries.
The `metadataBlock` entry contains name, alias, and display name as follows:
```yaml
metadataBlock:
  - name: ValidExample
    dataverseAlias:
    displayName: Valid
```
Additional fields, like `blockURI`, can be added as additional key-value pairs.

The format for `datasetField` entries is identical, but requires other keys:
```yaml
# [...]
datasetField:
  - name: Description
    title: Description
    description: This field describes.
    watermark:
    fieldType: textbox
    displayOrder:
    displayFormat:
    advancedSearchField: true
    allowControlledVocabulary: false
    allowmultiples: false
    facetable: false
    displayoncreate: true
    required: true
    parent:
    metadatablock_id: ValidExample
  - name: Answer
    title: Answer
    # [...]
```
For each additional dataset field, add another entry to this list.
Empty values are replaced with empty entries in the TSV file.
Note that YAML parsers identify several "truthy" values as Boolean variables.
These can include `true`/`false`, `yes`/`no`, and `True`/`False`.
If you want to preserve these as strings, you need to wrap these in quotes: `'true'`.
All truthy values are replaced by `TRUE`/`FALSE` in the TSV output.
Optional fields, like `termURI` can be added as additional key-value pairs.

Finally, records for `controlledVocabulary` behave as the two previous blocks:
```yaml
# [...]
controlledVocabulary:
  - DatasetField: AnswerYes
    Value: "Yes"
    identifier: answer_positive
    displayOrder:
  - DatasetField: AnswerNo
    # [...]
```
Again, additional fields can be added as additional key-value pairs.
