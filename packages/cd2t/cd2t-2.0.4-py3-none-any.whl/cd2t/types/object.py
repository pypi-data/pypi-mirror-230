import cd2t.types.base
import cd2t.types.ParserDataType
from cd2t.utils import string_matches_regex_list, regex_matches_in_string_list
from cd2t.results import ValidationFinding, FindingsList
from cd2t.schema import SchemaError, Schema
from cd2t.RunTimeEnv import RunTimeEnv


class Object(cd2t.types.base.BaseDataType):
    data_type_name = "object"
    matching_classes = [dict]
    support_reference = True
    options = [
        # option_name, required, class, init_value
        ("attributes", False, dict, None),
        ("required_attributes", False, list, list),
        ("dependencies", False, dict, dict()),
        ("reference_attributes", False, list, None),
        ("ignore_undefined_attributes", False, bool, False),
        ("allow_regex_attributes", False, bool, False),
        ("autogenerate", False, bool, True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.attributes = None
        self.attributes_objects = dict()
        self.tmp_a_schema = None
        self.required_attributes = list()
        self.dependencies = dict()
        self.reference_attributes = None
        self.ignore_undefined_attributes = False
        self.allow_regex_attributes = False
        self.autogenerate = True
        return

    def build_schema(
        self,
        schema: dict,
        path: str,
        RTE: RunTimeEnv,
        schema_obj: Schema,
    ):
        super().build_schema(
            schema=schema,
            path=path,
            RTE=RTE,
            schema_obj=schema_obj,
        )
        if self.attributes is not None:
            for a_name, a_schema in self.attributes.items():
                a_path = "%s.%s" % (path, a_name)
                self.tmp_a_schema = a_schema
                self.attributes_objects[
                    a_name
                ] = cd2t.types.ParserDataType.ParserDataType().build_schema(
                    self.tmp_a_schema, a_path, RTE, schema_obj
                )
        return self

    def verify_options(self, path: str) -> None:
        super().verify_options(path)
        if self.attributes is None:
            # No other options should be set:
            for option, required, cls, init_value in self.options:
                if exec("self." + option + " != init_value"):
                    raise SchemaError("Option 'attributes' required", path + option)
            return
        i = 0
        for req_attr in self.required_attributes:
            if not self._attribute_in_list(
                req_attr, list(self.attributes.keys()), self.allow_regex_attributes
            ):
                raise SchemaError(
                    "'%s' not in 'attributes'" % req_attr,
                    "%srequired_attributes[%d]" % (path, i),
                )
            i += 1
        if self.reference_attributes is not None:
            i = 0
            for ref_attr in self.reference_attributes:
                if ref_attr not in self.attributes.keys():
                    raise SchemaError(
                        "'%s' not in 'attributes'" % ref_attr,
                        "%sreference_attributes[%d]" % (path, i),
                    )
                i += 1
        path = path + "dependencies."
        for dep_attr, dep_info in self.dependencies.items():
            _path = path + dep_attr
            if dep_attr not in self.attributes.keys():
                raise SchemaError("'%s' not in 'attributes'" % dep_attr, _path)
            if not isinstance(dep_info, dict):
                raise SchemaError("Not a dictionary" % dep_attr, _path)
            i = 0
            for req_attr in dep_info.get("requires", []):
                if not self._attribute_in_list(
                    req_attr, list(self.attributes.keys()), self.allow_regex_attributes
                ):
                    raise SchemaError(
                        "'%s' not in 'attributes'" % req_attr,
                        "%s.requires[%d]" % (_path, i),
                    )
                i += 1
            i = 0
            for ex_attr in dep_info.get("excludes", []):
                if not self._attribute_in_list(
                    ex_attr, list(self.attributes.keys()), self.allow_regex_attributes
                ):
                    raise SchemaError(
                        "'%s' not in 'attributes'" % ex_attr,
                        "%s.excludes[%d]" % (_path, i),
                    )
                i += 1

    def build_references(self, data: any, path: str, RTE: RunTimeEnv):
        for a_name, a_data in data.items():
            data_type = self._get_attribute_object(a_name, self.allow_regex_attributes)
            if data_type is None:
                continue
            a_path = "%s.%s" % (path, a_name)
            data_type.build_references(a_data, a_path, RTE)

    def autogenerate_data(self, data: any, path: str, RTE: RunTimeEnv):
        FL = FindingsList()
        if data is None or not self.data_matches_type(data):
            return data, FL
        if path:
            path = path + "."
        if not self.allow_regex_attributes and self.autogenerate:
            if RTE.ruamel_yaml_available and isinstance(data, RTE.CommentedMap):
                new_data = data
                insert = True
            else:
                new_data = dict()
                insert = False
            i = 0
            for a_name, data_type in self.attributes_objects.items():
                a_path = "%s%s" % (path, a_name)
                _FL = FindingsList()
                if a_name not in data.keys():
                    _data, _FL = data_type.autogenerate_data(
                        data=None, path=a_path, RTE=RTE
                    )
                    if _FL:
                        if insert:
                            new_data.insert(
                                pos=i, key=a_name, value=_data, comment="autogenerated"
                            )
                        else:
                            new_data[a_name] = _data
                        i += 1
                else:
                    _data, _FL = data_type.autogenerate_data(data[a_name], a_path, RTE)
                    new_data[a_name] = _data
                    i += 1
                FL += _FL
            data = new_data
        else:
            for a_name, a_data in data.items():
                data_type = self._get_attribute_object(
                    a_name, self.allow_regex_attributes
                )
                if data_type is None:
                    continue
                a_path = "%s%s" % (path, a_name)
                _data, _FL = data_type.autogenerate_data(a_data, a_path, RTE)
                if _FL:
                    data[a_name] = _data
                    FL += _FL
        return data, FL

    @staticmethod
    def _attribute_in_list(
        attribute: str, attributes: list, regex_allowed=False
    ) -> bool:
        if regex_allowed:
            return regex_matches_in_string_list(attribute, attributes)
        elif attribute in attributes:
            return attribute
        return None

    def _get_attribute_object(self, name: str, regex_allowed=False) -> bool:
        if regex_allowed:
            name = string_matches_regex_list(
                string=name,
                regex_list=list(self.attributes_objects.keys()),
                full_match=True,
            )
        return self.attributes_objects.get(name, None)

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        if self.attributes is None:
            return FL
        if path:
            path = path + "."
        for a_name, a_data in data.items():
            _path = "%s%s" % (path, a_name)
            data_type = self._get_attribute_object(a_name, self.allow_regex_attributes)
            if data_type is None:
                if self.ignore_undefined_attributes:
                    continue
                FL.append(
                    ValidationFinding(path=_path, message="Attribute not allowed")
                )
                continue
            FL += data_type.validate_data(
                data=a_data, path="%s%s" % (path, a_name), RTE=RTE
            )
        for req_attr in self.required_attributes:
            _path = "%s%s" % (path, req_attr)
            found_in_data_keys = False
            if self.allow_regex_attributes:
                if regex_matches_in_string_list(
                    regex=req_attr, strings=list(data.keys()), full_match=True
                ):
                    found_in_data_keys = True
            elif req_attr in data.keys():
                found_in_data_keys = True
            if not found_in_data_keys:
                FL.append(
                    ValidationFinding(path=_path, message="Required attribute missing")
                )
        for attr_name, dep_info in self.dependencies.items():
            attr_path = "%s%s" % (path, attr_name)
            if not attr_name in data.keys():
                continue
            a_path = path + attr_name
            for req_attr in dep_info.get("requires", list()):
                if self.allow_regex_attributes:
                    if not regex_matches_in_string_list(
                        regex=req_attr, strings=list(data.keys()), full_match=True
                    ):
                        FL.append(
                            ValidationFinding(
                                path=attr_path,
                                message="No attribute matches regex requirements",
                            )
                        )
                elif req_attr not in data.keys():
                    FL.append(
                        ValidationFinding(
                            path=attr_path, message="Missing attribute '%s'" % req_attr
                        )
                    )
            for ex_attr in dep_info.get("excludes", list()):
                match = None
                if self.allow_regex_attributes:
                    match = regex_matches_in_string_list(
                        regex=ex_attr, strings=list(data.keys()), full_match=True
                    )
                    if match:
                        found_in_data_keys = True
                elif ex_attr in data.keys():
                    match = ex_attr
                if match is not None:
                    FL.append(
                        ValidationFinding(
                            path=attr_path, message="Excludes attribute '%s'" % match
                        )
                    )
        return FL

    def get_reference_data(self, data: any, path: str) -> any:
        ref_data = list()
        results = list()
        for ref_attr in self.reference_attributes:
            if ref_attr not in data.keys():
                results.append(
                    ValidationFinding(
                        path=path, message="Reference attribute '%s' missing" % ref_attr
                    )
                )
            ref_data.append(data[ref_attr])
        return ref_data, results


class Object_V1(Object):
    def verify_options(self, path: str) -> None:
        super().verify_options(path)
        if self.reference_attributes is None:
            if self.ref_key and self.allow_regex_attributes:
                raise SchemaError(
                    "Must be defined if reference is enabled and regex is allowed",
                    path + "reference_attributes",
                )
            self.reference_attributes = self.attributes
        i = 0


class Object_V2(Object):
    options = [
        # option_name, required, class, init_value
        ("attributes", False, dict, None),
        ("required_attributes", False, list, list),
        ("dependencies", False, dict, dict()),
        ("ignore_undefined_attributes", False, bool, False),
        ("allow_regex_attributes", False, bool, False),
        ("autogenerate", False, bool, True),
    ]

    def build_schema(
        self,
        schema: dict,
        path: str,
        RTE: RunTimeEnv,
        schema_obj: Schema,
    ):
        # Pop reference.attributes if available
        if (
            isinstance(schema, dict)
            and isinstance(schema.get("reference", None), dict)
            and "attributes" in schema["reference"]
        ):
            self.reference_attributes = schema["reference"].pop("attributes")
        super().build_schema(
            schema=schema,
            path=path,
            RTE=RTE,
            schema_obj=schema_obj,
        )
        return self

    def verify_options(self, path: str) -> None:
        super().verify_options(path)
        if self.reference_attributes is not None:
            if not isinstance(self.reference_attributes, list):
                raise SchemaError("Must be a list", path + ".reference.attributes")
            i = 0
            for attr in self.reference_attributes:
                if not isinstance(attr, str):
                    raise SchemaError(
                        "Must be a string", "%s.reference.attributes[%d]" % (path, i)
                    )
                i += 1

    def get_reference_data(self, data: any, path: str) -> any:
        if self.reference_attributes is None:
            return data, list()

        ref_data = list()
        results = list()
        for ref_attr in self.reference_attributes:
            if ref_attr not in data.keys():
                results.append(
                    ValidationFinding(
                        path=path, message="Reference attribute '%s' missing" % ref_attr
                    )
                )
            ref_data.append(data[ref_attr])

        return ref_data, results
