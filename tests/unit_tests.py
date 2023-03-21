from yml2block.__main__ import guess_input_type
from yml2block.prefix_analysis import split_by_common_prefixes, estimate_typos


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


def test_prefix_splitting_one_group():
    kws = ["fooBarBaz", "fooBarTest", "fooBar"]
    expected_groups = {
        "fooBar": ["fooBarBaz", "fooBarTest", "fooBar"],
    }

    result = split_by_common_prefixes(kws, verbose=True)

    assert result == expected_groups


def test_prefix_splitting_no_prefix():
    kws = ["1FooBar", "2FooBar", "3FooBar"]
    expected_groups = {
        "1FooBar": [
            "1FooBar",
        ],
        "2FooBar": [
            "2FooBar",
        ],
        "3FooBar": [
            "3FooBar",
        ],
    }

    result = split_by_common_prefixes(kws)

    assert result == expected_groups


def test_prefix_splitting_multiple_groups():
    kws = ["1FooBar", "FooBar", "3FooBar", "FooBarBaz"]
    expected_groups = {
        "1FooBar": [
            "1FooBar",
        ],
        "FooBar": [
            "FooBar",
            "FooBarBaz",
        ],
        "3FooBar": [
            "3FooBar",
        ],
    }

    result = split_by_common_prefixes(kws)

    assert result == expected_groups


def test_prefix_splitting_min_pref_len():
    kws = ["Foo1", "Foo2", "Foo3"]
    expected_groups_min_pref_len_4 = {
        "Foo1": ["Foo1"],
        "Foo2": ["Foo2"],
        "Foo3": ["Foo3"],
    }
    result_min_pref_len_4 = split_by_common_prefixes(kws, min_prefix_length=4)
    assert result_min_pref_len_4 == expected_groups_min_pref_len_4

    expected_groups_min_pref_len_3 = {"Foo": ["Foo1", "Foo2", "Foo3"]}
    result_min_pref_len_3 = split_by_common_prefixes(kws, min_prefix_length=3)
    assert result_min_pref_len_3 == expected_groups_min_pref_len_3


def test_prefix_splitting_longest_binding():
    kws = [
        "FoobarAttr1",
        "FoobarAttr2",
        "FoobarAlt1",
        "FoobarAlt2",
        "FoobarOpt1",
        "FoobarOpt2",
        "FoobarOtp3",  # This typo is intentional
        "1Foobar",
    ]
    expected_groups = {
        "FoobarAttr": [
            "FoobarAttr1",
            "FoobarAttr2",
        ],
        "FoobarAlt": [
            "FoobarAlt1",
            "FoobarAlt2",
        ],
        "FoobarOpt": [
            "FoobarOpt1",
            "FoobarOpt2",
        ],
        # This typo is intentional
        "FoobarOtp3": ["FoobarOtp3"],
        "1Foobar": ["1Foobar"],
    }

    result = split_by_common_prefixes(kws)
    assert expected_groups == result


def test_typo_detection_no_typo():
    """Are prefix sets without probable typos handled correctly?"""
    keywords = [
        "FoobarAttr1",
        "FoobarAttrZwo",
        "FoobarAttrDrei",
        "BarfooAttr1",
        "BarfooAttr2",
        "Bar",
    ]
    # NOTE: The keywords above should split into the groups shown below
    # keywords = {
    #     "FoobarAttr": ["FoobarAttr1", "FoobarAttrZwo", "FoobarAttrDrei"],
    #     "BarfooAttr": ["BarfooAttr1", "BarfooAttr2"],
    #     "Bar": "Bar",
    # }

    expected_typo_candidates = []

    typo_candidates = estimate_typos(keywords, dl_distance_threshold=1)
    assert typo_candidates == expected_typo_candidates


def test_typo_singleton_heuristic():
    """Are typos covered by the singleton heuristic detected correctly?"""
    keywords = [
        "FoobarAttr1",
        "FoobarAttrZwo",
        "FoobarAttrDrei",
        "FoobraAttrNrVier",
        "Bar",
    ]
    # NOTE: The keywords above should split into the groups shown below
    # keywords = {
    #     "FoobarAttr": ["FoobarAttr1", "FoobarAttrZwo", "FoobarAttrDrei"],
    #     "FoobraAttrNrVier": ["FoobraAttrNrVier"],
    #     "Bar": "Bar",
    # }

    expected_typo_candidates = [
        (
            {"FoobraAttrNrVier": ["FoobraAttrNrVier"]},
            {"FoobarAttr": ["FoobarAttr1", "FoobarAttrZwo", "FoobarAttrDrei"]},
        )
    ]
    typo_candidates = estimate_typos(keywords, dl_distance_threshold=1)
    assert typo_candidates == expected_typo_candidates


def test_typo_different_distances():
    """Does typo estimation with different DL-distances work as expected??"""
    keywords = [
        "FoobarAttr1",
        "FoobarAttrZwo",
        "FoobarAttrDrei",
        "FXobraAttrNrVier",
        "Bar",
    ]
    # NOTE: The keywords above should split into the groups shown below
    # keywords = {
    #     "FoobarAttr": ["FoobarAttr1", "FoobarAttrZwo", "FoobarAttrDrei"],
    #     # This prefix "FXobraAttrNrVier" has a DL-distance of 2
    #     # (1 replacement X->o and one transposition ra->ar)
    #     # It should not be detected with threshold 1, but with threshold 2.
    #     "FXobraAttrNrVier": ["FXobraAttrNrVier"],
    #     "Bar": "Bar",
    # }

    expected_typo_candidates_distance_1 = []
    typo_candidates_distance_1 = estimate_typos(
        keywords, dl_distance_threshold=1, verbose=True
    )
    assert typo_candidates_distance_1 == expected_typo_candidates_distance_1

    expected_typo_candidates_distance_2 = [
        (
            {"FXobraAttrNrVier": ["FXobraAttrNrVier"]},
            {"FoobarAttr": ["FoobarAttr1", "FoobarAttrZwo", "FoobarAttrDrei"]},
        )
    ]
    typo_candidates_distance_2 = estimate_typos(
        keywords, dl_distance_threshold=2, verbose=True
    )
    assert typo_candidates_distance_2 == expected_typo_candidates_distance_2


def test_placeholder_full_typo_estimation():
    """Placeholder test for more complex detection."""
    # These typos cannot be detected by the singleton heuristic.
    # This test serves as a placeholder for future tests that can
    # and should come up empty until then.
    keywords = [
        "FoobarAttr1",
        "FoobarAttrZwo",
        "FoobraAttrDrei",
        "FoobraAttrNrVier",
        "FoobarAttrBar",
        "FoobarAttrBoo",
        "Bar",
        "Foobar",
        "F0obarAttrEight",
        "F0obarAttrNine",
    ]
    # NOTE: The keywords defined above should split into the groups showm below
    # split_kws = {
    #     "FoobarAttr": ["FoobarAttr1", "FoobarAttrZwo"],
    #     "FoobraAttr": ["FoobraAttrDrei", "FoobraAttrNrVier"],
    #     "FoobarAttrB": ["FoobarAttrBar", "FoobarAttrBoo"],
    #     "Bar": ["Bar"],
    #     "Foobar": ["Foobar"],
    #     "F0obarAttr": ["F0obarAttrEight", "F0obarAttrNine"],
    # }

    expected_typo_candidates = []
    typo_candidates = estimate_typos(keywords, dl_distance_threshold=1)
    assert typo_candidates == expected_typo_candidates
