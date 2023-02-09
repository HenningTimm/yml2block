# yml2block
The yml2block script converts a YAML description of a dataverse-compliant
metadata schema into a Dataverse metadata block TSV file.

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

## Usage
You can call the script directly (without installation) using `Python` from the cloned repository folder:

```bash
yml2block $ python yml2block --help
```

If you followed the installation instructions using poetry shown above,
you can also call `yml2block` directly:

```bash
~ $ yml2block path/to/inout_metadata_schema.yml -o path/to/dataverse_metadata_block.tsv
```

## Parameters

### Input
The path to the input file containing the metadata schema in YAML format
is given as the positional parameter.

If a path to a tsv file is given as the positional parameter, this file
will only be linted as if the `--check` parameter was passed.
No output is written in this case.

### Output
By default, the output will be written to the same path as the input file,
replacing the `.yml`/ `.yaml` suffix with `.tsv`.

You can explicitly specify an output file name using the `-o file/path.tsv` parameter.

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
