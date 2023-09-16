import cd2t.types.ParserDataType
from cd2t.schema import Schema, SchemaError
from cd2t.results import FindingsList
from cd2t.References import ReferenceFinding
from cd2t.RunTimeEnv import RunTimeEnv
import copy


class DataParser:
    """Mother class for all data processing classes"""

    def __init__(self, namespace: str = "") -> None:
        self.RTE = RunTimeEnv(namespace=namespace)
        self.current_schema = None

    @property
    def namespace(self):
        return self.RTE.namespace

    def change_namespace(self, namespace: str) -> None:
        self.RTE.change_namespace(namespace=namespace)

    def _get_schema_object(self, schema: Schema) -> Schema:
        """Return a schema object. Either given schema if valid or last loaded schema

        Args:
            schema: Schema object

        Return:
            A valid Schema object

        Raises:
            SchemaError:
                - If given schema is not a Schema object
                - If given schema object is not valid and no schema has been loaded before
        """
        if not isinstance(schema, Schema):
            raise SchemaError("Given schema is not a valid schema object")
        if schema.root_data_type is None:
            if self.current_schema is None:
                raise SchemaError(
                    "need a schema or " + "Validator object loads a schema first"
                )
            return self.current_schema
        return schema

    def load_schema(self, schema: dict) -> Schema:
        """Verify schema definition, converts it to a Schema object and stores it.

        Args:
            schema: dictionary - containing schema definition

        Return:
            A valid Schema object

        Raises:
            SchemaError: If given schema is not a dictionary or not a valid schema definition
        """
        schema = copy.deepcopy(schema)

        version = schema.get("version", 1)
        if not isinstance(version, int):
            raise SchemaError("Schema version must be 'integer'")
        if version not in [1, 2]:
            raise SchemaError("Schema version %d not support." % version)
        schema_obj = Schema(version=version, description=schema.get("description", ""))

        self.RTE.version = version
        self.RTE.allow_shortcuts = schema.get("allow_data_type_shortcuts", version > 1)

        if schema_obj.version == 2:
            if "subschemas" in schema.keys():
                raise SchemaError("Subschemas not supported in version 2")
            self.RTE.templates = schema.get("templates", dict())
            template_merge_options = schema.get("template_merge_options", dict())
            self.RTE.templates_merge_recursive = template_merge_options.get(
                "recursive", True
            )
            self.RTE.templates_list_merge = template_merge_options.get(
                "list_merge", "append_rp"
            )
            # Validate, build and store custom data types
            for cdt_name, cdt_schema in schema.get("custom_data_types", dict()).items():
                _path = "custom_data_types.%s" % cdt_name
                if not isinstance(cdt_schema, dict):
                    raise SchemaError(
                        message="Custom data type definition must be a dictionary",
                        path=_path,
                    )
                data_type = cd2t.types.ParserDataType.ParserDataType().build_schema(
                    schema=cdt_schema,
                    path=_path,
                    RTE=self.RTE,
                    schema_obj=schema_obj,
                )
                if data_type.customizable:
                    if (
                        cdt_name
                        not in cd2t.types.ParserDataType.BUILTIN_DATA_TYPES[
                            schema_obj.version
                        ]
                    ):
                        schema_obj.custom_data_types[cdt_name] = cdt_schema
                    else:
                        raise SchemaError(
                            message="Custom data type name is a built-in data type name",
                            path=_path,
                        )
                else:
                    raise SchemaError(
                        message="Data type %s is not customizable" % cdt_schema["type"],
                        path=_path,
                    )

        elif schema_obj.version == 1:
            self.RTE.subschemas = schema.get("subschemas", dict())
            if self.RTE.subschemas:
                if not isinstance(self.RTE.subschemas, dict):
                    raise SchemaError("Schema subschemas is no dictionary")
                for sub_name, sub_schema in self.RTE.subschemas.items():
                    _path = "<" + sub_name + ">"
                    if isinstance(sub_schema, Schema):
                        # This subschema was already verified/translated (recursively)
                        continue
                    sub_type_schema = sub_schema.get("root", None)
                    if sub_type_schema is None:
                        raise SchemaError(message="key 'root' missing", path=_path)
                    _path = _path + "root"
                    self.RTE.subschema_path.append(sub_name)
                    sub_type = cd2t.types.ParserDataType.ParserDataType().build_schema(
                        schema=sub_type_schema,
                        path=_path,
                        RTE=self.RTE,
                        schema_obj=schema_obj,
                    )
                    self.RTE.subschema_path.pop()
                    sub_schema_obj = Schema()
                    sub_schema_obj.set_root_data_type(sub_type)

        root_type_schema = schema.get("root", None)
        if root_type_schema is None:
            raise SchemaError(message="key 'root' missing")
        _path = "root"
        root_type = cd2t.types.ParserDataType.ParserDataType().build_schema(
            schema=root_type_schema,
            path=_path,
            RTE=self.RTE,
            schema_obj=schema_obj,
        )
        schema_obj.set_root_data_type(root_type)
        self.current_schema = schema_obj

        # Clean RTE
        self.RTE.templates = dict()
        self.RTE.subschemas = dict()
        return schema_obj

    def get_reference_findings(self) -> list[ReferenceFinding]:
        """Get references findings after data validation(s)

        Returns:
            list - containing all findings as ReferenceFinding objects
        """
        return self.RTE.references.get_producer_consumer_issues()


class Autogenerator(DataParser):
    """
    Autogenerator can:
    - load/verify schema definitions
    - build references on multiple data sets
    - autogenerate data in data sets according to schema definition(s) and references
    """

    def build_references(self, data: any, schema=Schema()) -> None:
        """Build/Populate references from data with schema definitions

        Args:
            data: any - Any data from which references should be analyzed

            schema: Schema object
                If not given or Schema object is not valid, last loaded schema is used
        """
        schema = self._get_schema_object(schema)
        root_data_type = schema.root_data_type
        root_data_type.build_references(data=data, path="", RTE=self.RTE)

    def autogenerate_data(self, data: any, schema=Schema()) -> any:
        """Autogenerate missing data according to schema and references

        Args:
            data: any - Any data where missing data should be added

            schema: Schema object
                If not given or Schema object is not valid, last loaded schema is used

        Returns:
            tuple:
                - any - Given 'data' with autogerenated data added
                - FindingsList object - containing all findings as Finding objects
        """
        schema = self._get_schema_object(schema)
        self.RTE.version = schema.version
        self.RTE.allow_shortcuts = schema.version > 1
        root_data_type = schema.root_data_type
        new_data, FL = root_data_type.autogenerate_data(
            data=data, path="", RTE=self.RTE
        )
        FL.set_namespace(self.RTE.namespace)
        return new_data, FL


class Validator(DataParser):
    """
    Validator can:
    - load/verify schema definitions
    - validate data according to schema definition(s) and analyzed references
    """

    def validate_data(self, data: any, schema=Schema()) -> FindingsList:
        """Validate data according to schema and references

        Args:
            data: any - Any data which should be validated

            schema: Schema object
                If not given or Schema object is not valid, last loaded schema is used

        Returns:
            FindingsList object - containing all findings as Finding objects
        """
        schema = self._get_schema_object(schema)
        root_data_type = schema.root_data_type
        FL = root_data_type.validate_data(data=data, path="", RTE=self.RTE)
        FL.set_namespace(self.RTE.namespace)
        return FL
