"""This moudle contains custom datatypes used to create the internal YAML-like
structure used for metadata block lints. MOst importantly these types allow to
track line and column numbers for input data to enable more helpful user feedback.
"""
# from ruamel.yaml.scalarstring import LiteralScalarString, FoldedScalarString, DoubleQuotedScalarString, SingleQuotedScalarString, PlainScalarString
# from ruamel.yaml.scalarint import ScalarInt
# from ruamel.yaml.scalarbool import ScalarBoolean

# TODO: Implement custom constructor for ruamel yaml
# to get line and colum numbers for leafs in the yaml file
# https://stackoverflow.com/a/45717104


class MDBlockList(list):
    __slots__ = ("line", "column")

    def __init__(self, iterable=None, line=None, column=None):
        """Create a new MDBlock list that behaves like a normal list
        but tracks line an column number in object slots.
        """
        self.line = line
        self.column = column

        # Delegate initialization to the list constructore
        if iterable is None:
            super().__init__()
        else:
            super().__init__(iterable)

    @classmethod
    def from_ruamel(cls, ruamel_list):
        """Create a MDBlock list from an existing list read by the
        ruamel.yaml round trip parser.
        """
        return cls(ruamel_list, line=ruamel_list.lc.line, column=ruamel_list.lc.col)


class MDBlockDict(dict):
    __slots__ = ("line", "column")

    def __init__(self, mapping=None, /, line=None, column=None, **kwargs):
        """Create a new MDBlock Dictionary that behaves like a normal dictionary
        but tracks line an column number in object slots.
        """
        self.line = line
        self.column = column

        # Ensure an inner dict exists
        if mapping is None:
            mapping = dict()

        # Remain compatible with pythons regular dict constructor by
        # allowing kwargs to extend the passed mapping
        mapping.update(kwargs)

        super().__init__(mapping)

    @classmethod
    def from_ruamel(cls, ruamel_dict):
        """Create a MDBlock dict from an existing dict read by the
        ruamel.yaml round trip parser.
        """
        return cls(ruamel_dict, line=ruamel_dict.lc.line, column=ruamel_dict.lc.col)


class MDBlockNode:
    __slots__ = ("line", "column", "value")

    def __init__(self, value, line=None, column=None):
        self.line = line
        self.column = column
        self.value = value

    def __repr__(self):
        return f"({self.line}, {self.column}) {self.value}"
