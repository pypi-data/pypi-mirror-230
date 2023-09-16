import cd2t.types.base
import cd2t.types.ParserDataType
from cd2t.results import DataTypeMismatch, FindingsList
from cd2t.References import ReferenceFinding
from cd2t.schema import SchemaError, Schema
from cd2t.RunTimeEnv import RunTimeEnv


class Multitype(cd2t.types.base.BaseDataType):
    data_type_name = "multitype"
    options = [
        # option_name, required, class
        ("types", True, list, None),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.types = None
        self.type_objects = list()
        self.matching_classes = []
        self.data_type_mismatch_message = "None of the data types matches"

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
        i = 0
        for _type in self.types:
            _path = "%s.types[%d]" % (path, i)
            data_type = cd2t.types.ParserDataType.ParserDataType().build_schema(
                schema=_type, path=_path, RTE=RTE, schema_obj=schema_obj
            )
            if data_type.data_type_name == self.data_type_name:
                raise SchemaError("Multitype in Multitype not supported", _path)
            self.type_objects.append(data_type)
            self.matching_classes.extend(data_type.matching_classes)
            i += 1
        return self

    def build_sub_references(self, data: any, path: str, RTE: RunTimeEnv) -> list:
        for type_object in self.type_objects:
            if type_object.data_matches_type(data):
                type_object.build_references(data=data, path=path, RTE=RTE)

    def autogenerate_data(self, data: any, path: str, RTE: RunTimeEnv):
        FL = FindingsList()
        if data is None:
            return data, FL
        # Try to find ...
        for type_object in self.type_objects:
            if type_object.data_matches_type:
                FL += type_object.autogenerate_data(data=data, path=path, RTE=RTE)
        return data, FL

    def validate_data(self, data: any, path: str, RTE=RunTimeEnv) -> list:
        FL = FindingsList()
        near_finding_found = False
        for type_object in self.type_objects:
            # New data path syntax prevents analysis if finding is comming from sub data type.
            _FL = type_object.validate_data(data=data, path=path, RTE=RTE)
            if not _FL:
                return _FL
            elif not near_finding_found and isinstance(_FL[0], ReferenceFinding):
                FL = _FL
        if not FL:
            FL.append(
                DataTypeMismatch(path=path, message="None of the data types matches")
            )
        return FL
