from cd2t.types.base import BaseDataType
from cd2t.utils import string_matches_regex_list
from cd2t.schema import SchemaError, Schema
from cd2t.results import FindingsList, WrongValueFinding
from cd2t.References import OPT, ReferenceElement, ConsumerElement
from cd2t.RunTimeEnv import RunTimeEnv


class String(BaseDataType):
    customizable = True
    data_type_name = "string"
    matching_classes = [str]
    support_reference = True
    options = [
        # option_name, required, class
        ("maximum", False, int, None),
        ("minimum", False, int, None),
        ("allowed_values", False, list, None),
        ("not_allowed_values", False, list, list()),
        ("regex_mode", False, bool, False),
        ("regex_multiline", False, bool, False),
        ("regex_fullmatch", False, bool, True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.minimum = None
        self.maximum = None
        self.allowed_values = None
        self.not_allowed_values = list()
        self.regex_mode = False
        self.regex_multiline = False
        self.regex_fullmatch = True
        self.allow_namespace_lookups = False
        self.namespace_separator_char = None

    def build_schema(
        self,
        schema: dict,
        path: str,
        RTE: RunTimeEnv,
        schema_obj: Schema,
    ):
        schema = schema.copy()
        if self.support_reference and "reference" in schema.keys():
            reference_options = schema.get("reference", None)
            if isinstance(reference_options, dict):
                _path = path + ".reference"
                self.allow_namespace_lookups = reference_options.pop(
                    "allow_namespace_lookups", False
                )
                if not isinstance(self.allow_namespace_lookups, bool):
                    raise SchemaError(
                        "Must be boolean", _path + "allow_namespace_lookups"
                    )
                self.namespace_separator_char = reference_options.pop(
                    "namespace_separator_char", None
                )
                if self.namespace_separator_char is not None and not isinstance(
                    self.namespace_separator_char, str
                ):
                    raise SchemaError(
                        "Must be string", _path + "namespace_separator_char"
                    )

        return super().build_schema(schema, path, RTE, schema_obj)

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
        if self.allow_namespace_lookups:
            path = path + "reference."
            if OPT.CONSUMER not in self.ref_OPT:
                raise SchemaError(
                    "Needs mode = 'consumer'", path + "allow_namespace_lookups"
                )
            if self.namespace_separator_char is None:
                raise SchemaError(
                    "Needs option 'namespace_separator_char'",
                    path + "allow_namespace_lookups",
                )
            if not self.namespace_separator_char:
                raise SchemaError(
                    "Mustn't be empty string", path + "namespace_separator_char"
                )

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        if self.minimum is not None and self.minimum > len(data):
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="String length is lower than minimum %d" % self.minimum,
                )
            )
        elif self.maximum is not None and self.maximum < len(data):
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="String length is greater than maximum %d" % self.maximum,
                )
            )
        if self.regex_mode:
            matches = string_matches_regex_list(
                data,
                self.not_allowed_values,
                self.regex_multiline,
                self.regex_fullmatch,
            )
            if matches:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="String matches not allowed regex '%s'" % matches,
                    )
                )
            elif self.allowed_values:
                if not string_matches_regex_list(
                    data,
                    self.allowed_values,
                    self.regex_multiline,
                    self.regex_fullmatch,
                ):
                    FL.append(
                        WrongValueFinding(
                            path=path,
                            message="String does not match any allowed regex strings",
                        )
                    )
        else:
            if self.not_allowed_values and data in self.not_allowed_values:
                FL.append(WrongValueFinding(path=path, message="String is not allowed"))
            if self.allowed_values and data not in self.allowed_values:
                FL.append(WrongValueFinding(path=path, message="String is not allowed"))
        return FL

    def get_reference_element(self, path: str, ref_data: any) -> any:
        if OPT.CONSUMER in self.ref_OPT and self.allow_namespace_lookups:
            if self.namespace_separator_char in ref_data:
                provider_ns, value = ref_data.split(self.namespace_separator_char, 1)
                return ConsumerElement(
                    reference_key=self.ref_key,
                    path=path,
                    value=value,
                    options=self.ref_OPT,
                    credits=self.ref_credits,
                    provider_namespace=provider_ns,
                )
        return ReferenceElement(
            reference_key=self.ref_key,
            path=path,
            value=ref_data,
            options=self.ref_OPT,
            credits=self.ref_credits,
        )
