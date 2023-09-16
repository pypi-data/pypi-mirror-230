import cd2t.types.base
import cd2t.types.ParserDataType
from cd2t.types.string import String
from cd2t.types.integer import Integer
from cd2t.types.datatype import DataType
from cd2t.References import ReferenceElement, OPT
from cd2t.results import WrongValueFinding, UniqueErrorFinding, FindingsList
from cd2t.schema import SchemaError, Schema
from cd2t.RunTimeEnv import RunTimeEnv
import re


class IDList(cd2t.types.base.BaseDataType):
    data_type_name = "idlist"
    matching_classes = [dict]
    support_reference = True
    options = [
        # option_name, required, class
        ("minimum", False, int, None),
        ("maximum", False, int, None),
        ("elements", True, [dict, str], None),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.minimum = None
        self.maximum = None
        self.elements = None
        self.element_type = None
        self.id_data_type = String()

    def build_schema(
        self,
        schema: dict,
        path: str,
        RTE: RunTimeEnv,
        schema_obj: Schema,
    ) -> DataType:
        super().build_schema(
            schema=schema,
            path=path,
            RTE=RTE,
            schema_obj=schema_obj,
        )

        self.element_type = cd2t.types.ParserDataType.ParserDataType().build_schema(
            schema=self.elements,
            path=path + ".elements",
            RTE=RTE,
            schema_obj=schema_obj,
        )
        return self

    def build_sub_references(self, data: any, path: str, RTE: RunTimeEnv):
        i = 0
        for id, element in data.items():
            self.element_type.build_references(
                data=element, path="%s[%d]" % (path, i), RTE=RTE
            )
            i += 1

    def autogenerate_data(self, data: any, path: str, RTE: RunTimeEnv):
        FL = FindingsList()
        if not self.data_matches_type(data):
            return data, FL
        if path:
            path = path + "."
        for id, element in data.items():
            new_path = "%s%s" % (path, id)
            _data, _FL = self.element_type.autogenerate_data(
                data=element, path=new_path, RTE=RTE
            )
            data[id] = _data
            FL += _FL
        return data, FL


class IDList_V1(IDList):
    V1_options = [
        # option_name, required, class
        ("id_type", False, str, "string"),
        ("id_minimum", False, int, None),
        ("id_maximum", False, int, None),
        ("allowed_ids", False, list, None),
        ("not_allowed_ids", False, list, list()),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.options.extend(self.V1_options)
        self.id_type = "string"
        self.id_minimum = None
        self.id_maximum = None
        self.allowed_ids = None
        self.not_allowed_ids = list()

    def build_schema(
        self,
        schema: dict,
        path: str,
        RTE: RunTimeEnv,
        schema_obj: Schema,
    ) -> DataType:
        super().build_schema(
            schema=schema,
            path=path,
            RTE=RTE,
            schema_obj=schema_obj,
        )
        id_type_schema = dict()
        if self.id_minimum:
            id_type_schema["minimum"] = self.id_minimum
        if self.id_maximum:
            id_type_schema["maximum"] = self.id_maximum
        if self.not_allowed_ids:
            id_type_schema["not_allowed_values"] = self.not_allowed_ids
        if self.id_type == "string":
            if self.allowed_ids:
                id_type_schema["allowed_values"] = self.allowed_ids
            id_type_schema["regex_mode"] = True
        self.id_data_type = self.id_data_type.build_schema(
            schema=id_type_schema,
            path=path,
            RTE=RTE,
            schema_obj=schema_obj,
        )
        return self

    def verify_options(self, path: str) -> None:
        if self.id_type not in ["string", "integer"]:
            raise SchemaError("Must be 'string' or 'integer'", path + "id_type")
        if self.id_type == "integer":
            self.id_data_type = Integer()
        super().verify_options(path)

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        if self.minimum and len(data) < self.minimum:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Attribute count is lower than minimum %d" % self.minimum,
                )
            )
        elif self.maximum is not None and len(data) > self.maximum:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Attribute count is greater than maximum %d" % self.maximum,
                )
            )

        if path:
            path = path + "."
        for id, element in data.items():
            _FL = FindingsList()
            id_path = "%s%s" % (path, id)
            _FL += self.id_data_type.validate_data(data=id, path=id_path, RTE=RTE)
            if (
                self.id_type == "integer"
                and self.allowed_ids
                and id not in self.allowed_ids
            ):
                _FL.append(
                    WrongValueFinding(
                        path=id_path, message="Attribute is not an allowed value"
                    )
                )
            if not _FL:
                FL += self.element_type.validate_data(
                    data=element, path=id_path, RTE=RTE
                )
            else:
                FL += _FL
        return FL

    def verify_reference(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        if not self.data_matches_type(data) or OPT.NONE in self.ref_OPT:
            return []
        if path:
            path = path + "."
        results = list()
        for id in data.keys():
            id_path = "%s%s" % (path, id)
            element = ReferenceElement(self.ref_key, id_path, id, self.ref_OPT)
            other = RTE.references.same_unique(element)
            if other is not None:
                if RTE.namespace != other.namespace:
                    _path = "%s > %s" % (other.namespace, other.path)
                else:
                    _path = other.path
                results.append(
                    UniqueErrorFinding(
                        path=id_path, message="ID already used at '%s'" % _path
                    )
                )
            else:
                RTE.references.add_element(element)
        return results


class IDList_V2(IDList):
    V1_options = [
        # option_name, required, class
        ("id", False, (dict, str), "string"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.options.extend(self.V1_options)
        self.id = "string"
        self.id_data_type = String()

    def build_schema(
        self,
        schema: dict,
        path: str,
        RTE: RunTimeEnv,
        schema_obj: Schema,
    ) -> DataType:
        super().build_schema(
            schema=schema,
            path=path,
            RTE=RTE,
            schema_obj=schema_obj,
        )
        self.id_data_type = cd2t.types.ParserDataType.ParserDataType().build_schema(
            schema=self.id,
            path=path + ".id",
            RTE=RTE,
            schema_obj=schema_obj,
        )
        return self

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        if self.minimum and len(data) < self.minimum:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Attribute count is lower than minimum %d" % self.minimum,
                )
            )
        elif self.maximum is not None and len(data) > self.maximum:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Attribute count is greater than maximum %d" % self.maximum,
                )
            )

        if path:
            path = path + "."
        for id, element in data.items():
            _FL = FindingsList()
            id_path = "%s%s" % (path, id)
            _FL += self.id_data_type.validate_data(data=id, path=id_path, RTE=RTE)
            if not _FL:
                FL += self.element_type.validate_data(
                    data=element, path=id_path, RTE=RTE
                )
            else:
                FL += _FL
        return FL
