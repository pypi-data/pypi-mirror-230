import cd2t.types.ParserDataType
from cd2t.types.base import BaseDataType
from cd2t.results import FindingsList, ValidationFinding, WrongValueFinding
from cd2t.RunTimeEnv import RunTimeEnv
from cd2t.schema import Schema
import copy


class List(BaseDataType):
    data_type_name = "list"
    matching_classes = [list]
    options = [
        # option_name, required, class
        ("minimum", False, int, None),
        ("maximum", False, int, None),
        ("allow_duplicates", False, bool, True),
        ("elements", True, [dict, str], dict()),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.minimum = None
        self.maximum = None
        self.allow_duplicates = True
        self.elements = dict()
        self.element_data_type = None

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
        self.element_data_type = (
            cd2t.types.ParserDataType.ParserDataType().build_schema(
                schema=self.elements,
                path=path + ".elements",
                RTE=RTE,
                schema_obj=schema_obj,
            )
        )
        return self

    def build_sub_references(self, data: any, path: str, RTE: RunTimeEnv):
        i = 0
        for element in data:
            self.element_data_type.build_references(element, "%s[%d]" % (path, i), RTE)
            i += 1

    def autogenerate_data(self, data: any, path: str, RTE: RunTimeEnv):
        FL = FindingsList()
        if not self.data_matches_type(data):
            return data, FL
        for i in range(len(data)):
            _data, _FL = self.element_data_type.autogenerate_data(
                data[i], "%s[%d]" % (path, i), RTE
            )
            data[i] = _data
            FL += _FL
        return data, FL

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        if self.minimum and len(data) < self.minimum:
            FL.append(
                WrongValueFinding(
                    path=path, message="Length of list is lower than %d" % self.minimum
                )
            )
        elif self.maximum and len(data) > self.maximum:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Length of list is greater than %d" % self.maximum,
                )
            )
        i = 0
        for element in data:
            FL += self.element_data_type.validate_data(
                element, "%s[%d]" % (path, i), RTE
            )
            i += 1

        if not self.allow_duplicates:
            remaining_data = copy.copy(data)
            i = 0
            for element in data:
                remaining_data = remaining_data[1:]
                if element in remaining_data:
                    relative_position = remaining_data.index(element) + 1
                    FL.append(
                        ValidationFinding(
                            path="%s[%d]" % (path, i),
                            message="Element is same as on position %d"
                            % (i + relative_position),
                        )
                    )
                i += 1
        return FL
