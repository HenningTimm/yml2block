from yml2block.__main__ import guess_input_type


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
        assert violations[0].level == "WARNING"
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
        assert violations[0].level == "ERROR"
        assert guessed_type == False
