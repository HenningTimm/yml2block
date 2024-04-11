from yml2block.__main__ import guess_input_type
from yml2block.rules import Level
from yml2block.tsv_input import _identify_break_points


def test_input_guessing_valid_tsv():
    """Are valid paths to TSV files handled correctly?"""
    valid_tsv_paths = [
        "foo.tsv",
        "foo.Tsv",
        "foo.TSV",
        "~/foo.tsv",
        "~/foo.Tsv",
        "~/foo.TSV",
        "../foo.tsv",
        "../foo.Tsv",
        "../foo.TSV",
        "bar/foo.tsv",
        "bar/foo.Tsv",
        "bar/foo.TSV",
        "/bar/foo.tsv",
        "/bar/foo.Tsv",
        "/bar/foo.TSV",
    ]
    for path in valid_tsv_paths:
        guessed_type, violations = guess_input_type(path)
        assert len(violations) == 0
        assert guessed_type == "tsv"


def test_input_guessing_valid_csv():
    """Are valid paths to CSV files handled correctly?"""
    valid_csv_paths = [
        "foo.csv",
        "foo.Csv",
        "foo.CSV",
        "~/foo.csv",
        "~/foo.Csv",
        "~/foo.CSV",
        "../foo.csv",
        "../foo.Csv",
        "../foo.CSV",
        "bar/foo.csv",
        "bar/foo.Csv",
        "bar/foo.CSV",
        "/bar/foo.csv",
        "/bar/foo.Csv",
        "/bar/foo.CSV",
    ]
    for path in valid_csv_paths:
        guessed_type, violations = guess_input_type(path)
        assert len(violations) == 1
        assert violations[0].level == Level.WARNING
        assert guessed_type == "csv"


def test_input_guessing_valid_yaml():
    """Are valid paths to YML and YAML files handled correctly?"""
    valid_yml_paths = [
        "foo.yml",
        "foo.Yml",
        "foo.YML",
        "~/foo.yml",
        "~/foo.Yml",
        "~/foo.YML",
        "../foo.yml",
        "../foo.Yml",
        "../foo.YML",
        "bar/foo.yml",
        "bar/foo.Yml",
        "bar/foo.YML",
        "/bar/foo.yml",
        "/bar/foo.Yml",
        "/bar/foo.YML",
        "foo.yaml",
        "foo.Yaml",
        "foo.YAML",
        "~/foo.yaml",
        "~/foo.Yaml",
        "~/foo.YAML",
        "../foo.yaml",
        "../foo.Yaml",
        "../foo.YAML",
        "bar/foo.yaml",
        "bar/foo.Yaml",
        "bar/foo.YAML",
        "/bar/foo.yaml",
        "/bar/foo.Yaml",
        "/bar/foo.YAML",
    ]
    for path in valid_yml_paths:
        guessed_type, violations = guess_input_type(path)
        assert len(violations) == 0
        assert guessed_type == "yaml"


def test_input_guessing_invalid_extension():
    """Are invalid extensions handled correctly?"""
    invalid_extension_paths = [
        "foo.yam",
        "foo.xls",
        "foo.xlsx",
        "~/foo.dat",
        "~/foo.txt",
        "~/foo.gz",
        "../foo.tar.gz",
        "../foo.zip",
        "../foo.bar",
        "bar/foo.baz",
        "bar/foo.foo",
        "bar/foo.sdf",
        "/bar/foo.äöü",
        "/bar/foo.123",
        "/bar/foo.foo",
    ]
    for path in invalid_extension_paths:
        guessed_type, violations = guess_input_type(path)
        assert len(violations) == 1
        assert violations[0].level == Level.ERROR
        assert guessed_type is False


def test_breakpoint_identification():
    """ """
    test_cases = [
        {
            "file": "tests/valid/minimal_working_example_expected.tsv",
            "expected_blocks": (
                "#metadataBlock\tname\tdataverseAlias\tdisplayName\t\t\t\t\t\t\t\t\t\t\t\t\n\tValidExample\t\tValid\t\t\t\t\t\t\t\t\t\t\t\t\n",
                "#datasetField\tname\ttitle\tdescription\twatermark\tfieldType\tdisplayOrder\tdisplayFormat\tadvancedSearchField\tallowControlledVocabulary\tallowmultiples\tfacetable\tdisplayoncreate\trequired\tparent\tmetadatablock_id\n\tDescription\tDescription\tThis field describes.\t\ttextbox\t\t\tTRUE\tFALSE\tFALSE\tFALSE\tTRUE\tTRUE\t\tValidExample\n\tAnswer\tAnswer\t\t\ttext\t\t\tTRUE\tTRUE\tTRUE\tTRUE\tTRUE\tTRUE\t\tValidExample\n",
                "#controlledVocabulary\tDatasetField\tValue\tidentifier\tdisplayOrder\t\t\t\t\t\t\t\t\t\t\t\n\tAnswerYes\tYes\tanswer_positive\t\t\t\t\t\t\t\t\t\t\t\t\n\tAnswerNo\tNo\tanswer_negative\t\t\t\t\t\t\t\t\t\t\t\t\n\tAnswerMaybeSo\tMaybe\tanswer_unclear\t\t\t\t\t\t\t\t\t\t\t\t\n",
            ),
            "expected_violations": [],
        },
        {
            "file": "tests/snippets/minimal_snippet.tsv",
            "expected_blocks": (
                "#metadataBlock\n",
                "#datasetField\n",
                None,
            ),
            "expected_violations": [],
        },
        {
            "file": "tests/snippets/three_item_snippet.tsv",
            "expected_blocks": (
                "#metadataBlock\n",
                "#datasetField\n",
                "#controlledVocabulary\n",
            ),
            "expected_violations": [],
        },
        {
            "file": "tests/snippets/one_item_snippet.tsv",
            "expected_blocks": "#metadataBlock\n",
            "expected_violations": [
                {
                    "level": Level.WARNING,
                    "rule": "identify_break_points",
                }
            ],
        },
        {
            "file": "tests/snippets/four_item_snippet.tsv",
            "expected_blocks": "#metadataBlock\n#datasetField\n#controlledVocabulary\n#controlledVocabulary\n",
            "expected_violations": [
                {
                    "level": Level.WARNING,
                    "rule": "identify_break_points",
                }
            ],
        },
    ]

    for test_case in test_cases:
        with open(test_case["file"], "r") as case_file:
            split_blocks, violations = _identify_break_points(case_file.read())
        assert split_blocks == test_case["expected_blocks"]
        assert len(violations) == len(test_case["expected_violations"])
        for vio, exp_vio in zip(violations, test_case["expected_violations"]):
            assert vio.level == exp_vio["level"]
            assert vio.rule == exp_vio["rule"]


def test_breakpoint_suggestions():
    """ """
    raise NotImplemented
