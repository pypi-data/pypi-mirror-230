import cd2t.types.base
import cd2t.types.ParserDataType
from cd2t.schema import SchemaError, Schema
from cd2t.RunTimeEnv import RunTimeEnv
import copy


class SchemaDataType(cd2t.types.base.BaseDataType):
    data_type_name = "schema"
    options = [
        # option_name, required, class
        ("subschema", True, str, ""),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.subschema = ""
        self.sub_root_schema = None

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
        _sub_schema = RTE.subschemas.get(self.subschema, None)
        if _sub_schema is None:
            raise SchemaError("Could not found subschema '%s'" % self.subschema, path)
        new_path = path + "<" + self.subschema + ">"
        if self.subschema in RTE.subschema_path:
            raise SchemaError(
                "Subschema loop detected %s"
                % " -> ".join(RTE.subschema_path + [self.subschema]),
                new_path,
            )

        if isinstance(_sub_schema, Schema):
            # Subschema was already build.
            return _sub_schema.root_data_type

        RTE.subschema_path.append(self.subschema)
        new_path = new_path + "root"
        self.sub_root_schema = _sub_schema.get("root", None)
        if self.sub_root_schema is None:
            raise SchemaError("Key missing", new_path)
        sub_data_obj = cd2t.types.ParserDataType.ParserDataType().build_schema(
            schema=self.sub_root_schema,
            path=new_path,
            RTE=RTE,
        )
        sub_schema_obj = Schema()
        sub_schema_obj.set_root_data_type(sub_data_obj)
        RTE.subschemas[self.subschema] = sub_schema_obj

        # Clean subschema_path
        RTE.subschema_path.pop()

        return sub_data_obj
