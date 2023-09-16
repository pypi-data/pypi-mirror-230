from cd2t.types.base import BaseDataType
from cd2t.utils import string_matches_regex_list
from cd2t.schema import SchemaError, Schema
from cd2t.results import FindingsList, WrongValueFinding
from cd2t.References import OPT, ReferenceElement, ConsumerElement
from cd2t.RunTimeEnv import RunTimeEnv


class Hostname(BaseDataType):
    customizable = True
    data_type_name = "hostname"
    matching_classes = [str]
    support_reference = True
    options = [
        # option_name, required, class, default_value
        ("maximum", False, int, 63),
        ("minimum", False, int, 1),
        ("allowed_values", False, list, None),
        ("not_allowed_values", False, list, list()),
        ("strict_lower", False, bool, True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.minimum = 1
        self.maximum = 63
        self.allowed_values = None
        self.not_allowed_values = list()
        self.strict_lower = True

    def verify_options(self, path: str):
        super().verify_options(path)
        i = 0
        for string in self.not_allowed_values:
            if not isinstance(string, str):
                raise SchemaError(
                    "Must be string", "%snot_allowed_values[%d]" % (path, i)
                )
            i += 1
        if self.allowed_values is not None:
            i = 0
            for string in self.allowed_values:
                if not isinstance(string, str):
                    raise SchemaError(
                        "Must be string", "%sallowed_values[%d]" % (path, i)
                    )
                i += 1
        if not 0 < self.minimum < 64:
            raise SchemaError("Must be >0 and <64", "%sminimum" % path)
        if not self.minimum < self.maximum < 64:
            raise SchemaError("Must be >'minimum' and <64", "%smaximum" % path)

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()

        # Check for invalid characters
        hostname_len = len(data)
        first_char = 0
        last_char = hostname_len - 1
        for i in range(hostname_len):
            char = data[i]
            if self.strict_lower and char.isupper():
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="Hostname '%s' contains upper case at position %d"
                        % (data, i + 1),
                    )
                )
            if i == first_char and not char.isalnum():
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="Hostname must start with alphanumeric character"
                        % (char, i + 1),
                    )
                )
            elif i == last_char and not char.isalnum():
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="Hostname must end with alphanumeric character"
                        % (char, i + 1),
                    )
                )
            elif not char.isalnum() and char != "-":
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="Hostname '%s' contains illegal character at position %d"
                        % (data, i + 1),
                    )
                )

        # Check min and max length
        if self.minimum is not None and self.minimum > len(data):
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Hostname length is lower than minimum %d" % self.minimum,
                )
            )
        elif self.maximum is not None and self.maximum < len(data):
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Hostname length is greater than maximum %d" % self.maximum,
                )
            )

        # Check regex values
        matches = string_matches_regex_list(data, self.not_allowed_values)
        if matches:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Hostname matches not allowed regex '%s'" % matches,
                )
            )
        elif self.allowed_values is not None:
            if not string_matches_regex_list(data, self.allowed_values):
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="String does not match any allowed regex strings",
                    )
                )
        return FL
