from cd2t.types.base import BaseDataType
from cd2t.types.hostname import Hostname
from cd2t.utils import string_matches_regex_list
from cd2t.schema import SchemaError
from cd2t.results import FindingsList, WrongValueFinding
from cd2t.RunTimeEnv import RunTimeEnv
import re


class FQDN(BaseDataType):
    customizable = True
    data_type_name = "fqdn"
    matching_classes = [str]
    support_reference = True
    options = [
        # option_name, required, class, default_value
        ("maximum", False, int, 255),
        ("minimum", False, int, 1),
        ("minimum_labels", False, int, 2),
        ("maximum_labels", False, int, None),
        ("allowed_values", False, list, None),
        ("not_allowed_values", False, list, list()),
        ("strict_lower", False, bool, True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.minimum = 4
        self.maximum = 255
        self.minimum_labels = 2
        self.maximum_labels = None
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
            try:
                re.compile(string)
            except re.error:
                raise SchemaError(
                    "'%s' is not a valid regex string" % string,
                    "%snot_allowed_values[%d]" % (path, i),
                )
            i += 1
        if self.allowed_values is not None:
            i = 0
            for string in self.allowed_values:
                if not isinstance(string, str):
                    raise SchemaError(
                        "Must be string", "%sallowed_values[%d]" % (path, i)
                    )
                try:
                    re.compile(string)
                except re.error:
                    raise SchemaError(
                        "'%s' is not a valid regex string" % string,
                        "%sallowed_values[%d]" % (path, i),
                    )
                i += 1
        if not 4 <= self.minimum <= 255:
            raise SchemaError("Must be >=4 and <=255", "%sminimum" % path)
        if not self.minimum <= self.maximum <= 255:
            raise SchemaError("Must be >='minimum' and <=255", "%smaximum" % path)
        if not 2 <= self.minimum_labels:
            raise SchemaError("Must be >=2", "%sminimum_labels" % path)
        if (
            self.maximum_labels is not None
            and self.minimum_labels > self.maximum_labels
        ):
            raise SchemaError("Must be >='minimum_labels'", "%smaximum_labels" % path)

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()

        # Check min and max length
        if self.minimum > len(data):
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="FQDN length is lower than minimum %d" % self.minimum,
                )
            )
        elif self.maximum < len(data):
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="FQDN length is greater than maximum %d" % self.maximum,
                )
            )

        # Split hostname and labels and verify label count
        labels = data.split(".")
        if len(labels) < 2:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="'%s' is not a valid FQDN" % data,
                )
            )
            return FL

        label_count = len(labels)
        hostname = labels[0]
        domain_labels = labels[1:]

        if label_count < self.minimum_labels:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="'%s' label count of %d is lower than minimum %d"
                    % (data, label_count, self.minimum_labels),
                )
            )
        elif self.maximum_labels is not None and label_count > self.maximum_labels:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="'%s' label count of %d is higher than maximum %d"
                    % (data, label_count, self.maximum_labels),
                )
            )

        # Verify hostname part
        h_obj = Hostname()
        h_obj.strict_lower = self.strict_lower
        FL += h_obj.validate_data(data=hostname, path=path, RTE=RTE)

        # Check each domain label:
        position = len(hostname) + 2  # starting at first char behind first 'dot'
        for label in domain_labels:
            first_char = 0
            last_char = len(label) - 1
            for i in range(len(label)):
                char = label[i]
                if self.strict_lower and char.isupper():
                    FL.append(
                        WrongValueFinding(
                            path=path,
                            message="FQDN '%s' contains upper case at position %d"
                            % (data, position + i),
                        )
                    )
                if i == first_char and not char.isalpha():
                    FL.append(
                        WrongValueFinding(
                            path=path,
                            message="FQDN '%s' domain labels must start with an alphabetic character"
                            % data,
                        )
                    )
                elif i == last_char and not char.isalnum():
                    FL.append(
                        WrongValueFinding(
                            path=path,
                            message="FQDN '%s' domain labels must end with an alphanumeric character"
                            % data,
                        )
                    )
                elif not char.isalnum() and char != "-":
                    FL.append(
                        WrongValueFinding(
                            path=path,
                            message="FQDN '%s' contains illegal character at position %d"
                            % (data, position + i),
                        )
                    )
            position += len(label) + 1

        # Check regex values
        matches = string_matches_regex_list(data, self.not_allowed_values)
        if matches:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="FQDN '%s' matches not allowed regex '%s'"
                    % (data, matches),
                )
            )
        elif self.allowed_values is not None:
            if not string_matches_regex_list(data, self.allowed_values):
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="FQDN '%s' does not match any allowed regex strings"
                        % data,
                    )
                )

        return FL
