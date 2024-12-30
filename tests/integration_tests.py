import yml2block
from click.testing import CliRunner


def test_basic_execution_works():
    """This test ensures that the program runs at all."""
    runner = CliRunner()
    result = runner.invoke(yml2block.__main__.main, ["--help"])
    assert result.exit_code == 0, result

    result = runner.invoke(yml2block.__main__.main, ["check", "--help"])
    assert result.exit_code == 0, result

    result = runner.invoke(yml2block.__main__.main, ["convert", "--help"])
    assert result.exit_code == 0, result


def test_minimal_valid_example_check():
    """This test ensures that a valid files do not throw errors during check."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main, ["check", "tests/valid/minimal_working_example.yml"]
    )
    assert result.exit_code == 0, result


def test_minimal_valid_example_convert():
    """This test ensures that a valid file is translated without throwing an error."""
    runner = CliRunner()
    path_expected = "tests/valid/minimal_working_example_expected.tsv"
    path_output = "/tmp/y2b_mwe.tsv"
    result = runner.invoke(
        yml2block.__main__.main,
        ["convert", "tests/valid/minimal_working_example.yml", "-o", path_output],
    )
    assert result.exit_code == 0, result.stdout
    with open(path_output, "r") as converted_file, open(
        path_expected, "r"
    ) as expected_file:
        converted_tsv = converted_file.read()
        expected_tsv = expected_file.read()
        assert converted_tsv == expected_tsv
        assert len(converted_tsv) > 0
        assert len(expected_tsv) > 0


def test_duplicate_names_detected():
    """This test ensures that duplicate names are detected."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main,
        ["check", "tests/invalid/duplicate_datasetfield_name.yml"],
    )
    assert result.exit_code == 1, result.output

    result = runner.invoke(
        yml2block.__main__.main,
        ["check", "tests/invalid/duplicate_datasetfield_name.tsv"],
    )
    assert result.exit_code == 1, result.output


def test_duplicate_titles_detected():
    """This test ensures that duplicate titles are detected."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main,
        ["check", "tests/invalid/duplicate_datasetfield_title.yml"],
    )
    assert result.exit_code == 1, result.output

    result = runner.invoke(
        yml2block.__main__.main,
        ["check", "tests/invalid/duplicate_datasetfield_title.tsv"],
    )
    assert result.exit_code == 1, result.output

    # Acceptable duplications are not reported as errors
    result = runner.invoke(
        yml2block.__main__.main,
        ["check", "tests/valid/duplicate_compound_titles.yml"],
    )
    assert result.exit_code == 0, result.output


def test_duplicate_top_level_key_detected():
    """This test ensures that duplicates in top-level keys are detected."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main,
        ["check", "tests/invalid/duplicate_top-level_key.yml"],
    )
    assert result.exit_code == 1, result.output


def test_typo_in_keyword_detected():
    """This test ensures that typos in top-level keywords are detected."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main, ["check", "tests/invalid/typo_in_keyword.yml"]
    )
    assert result.exit_code == 1, result.output

    result = runner.invoke(
        yml2block.__main__.main, ["check", "tests/invalid/typo_in_keyword.tsv"]
    )
    assert result.exit_code == 1, result.output


def test_trailing_whitespace_detected():
    """This test ensures that typos in keys are detected."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main,
        ["check", "--warn-ec 2", "tests/invalid/whitespace_in_key.yml"],
    )
    assert result.exit_code == 2, result.output

    result = runner.invoke(
        yml2block.__main__.main,
        ["check", "--warn-ec 2", "tests/invalid/whitespace_in_key.tsv"],
    )
    assert result.exit_code == 2, result.output


def test_wrong_extensions_fail():
    """Ensure that files that do not end in tsv, csv, yml or yaml fail."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main, ["check", "tests/invalid/minimal_example.xlsx"]
    )
    assert result.exit_code == 1, result.output


def test_nested_compound_metadata():
    """Ensure nested compound metadata are detected and classified correctly."""

    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main, ["check", "tests/invalid/nested_compound_metadata.yml"]
    )
    assert result.exit_code == 1, result.output

    result = runner.invoke(
        yml2block.__main__.main, ["check", "tests/invalid/nested_compound_metadata.tsv"]
    )
    assert result.exit_code == 1, result.output

    result = runner.invoke(
        yml2block.__main__.main,
        ["check", "--warn-ec 2", "tests/valid/nested_compound_metadata.yml"],
    )
    assert result.exit_code == 2, result.output

    result = runner.invoke(
        yml2block.__main__.main,
        ["check", "--warn-ec 2", "tests/valid/nested_compound_metadata.tsv"],
    )
    assert result.exit_code == 2, result.output
