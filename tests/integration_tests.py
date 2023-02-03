import yml2block
from click.testing import CliRunner


def test_basic_execution_works():
    """This test ensures that the program runs at all."""
    runner = CliRunner()
    result = runner.invoke(yml2block.__main__.main, ["--help"])
    assert result.exit_code == 0, result


def test_minimal_valid_example():
    """This test ensures that a valid file is translated without throwing an error."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main, ["tests/valid/minimal_working_example.yml", "--check"]
    )
    assert result.exit_code == 0, result


def test_duplicate_names_detected():
    """This test ensures that duplicate names are detected."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main, ["tests/invalid/duplicate_name.yml", "--check"]
    )
    assert result.exit_code == 1, result.output


def test_duplicate_top_level_key_detected():
    """This test ensures that duplicates in top-level keys are detected."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main,
        ["tests/invalid/duplicate_top-level_key.yml", "--check"],
    )
    assert result.exit_code == 1, result.output


def test_typo_in_key_key_detected():
    """This test ensures that typos in keys are detected."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main, ["tests/invalid/typo_in_key.yml", "--check"]
    )
    assert result.exit_code == 1, result.output


def test_wrong_extensions_fail():
    """Ensure that files that do not end in tsv, csv, yml or yaml fail."""
    runner = CliRunner()
    result = runner.invoke(
        yml2block.__main__.main, ["tests/invalid/minimal_example.xlsx", "--check"]
    )
    assert result.exit_code == 1, result.output
