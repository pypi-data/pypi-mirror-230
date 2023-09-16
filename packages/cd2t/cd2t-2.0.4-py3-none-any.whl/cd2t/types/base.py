from cd2t.types.datatype import DataType
from cd2t.utils import *
from cd2t.results import *
from cd2t.schema import *
from cd2t.References import ReferenceFinding, OPT, ReferenceElement
from cd2t.RunTimeEnv import RunTimeEnv


class BaseDataType(DataType):
    customizable = False
    data_type_name = "any"
    matching_classes = []
    options = [
        # option_name, required?, class, init_value
        ("description", False, str, "")
    ]
    support_reference = False

    def __init__(self) -> None:
        self.description = ""
        self.ref_OPT = OPT.NONE
        self.ref_credits = None
        self.ref_key = ""
        self.data_type_mismatch_message = "Value is not '%s'" % self.data_type_name
        return

    def data_matches_type(self, data: any) -> bool:
        if self.data_type_name == "any":
            return True
        for cls in self.matching_classes:
            if isinstance(data, cls):
                return True
        return False

    def build_schema(
        self,
        schema: dict,
        path: str,
        RTE: RunTimeEnv,
        schema_obj: Schema,
    ) -> DataType:
        schema = schema.copy()

        # Parse BaseDataType reference options
        reference_options = dict()
        if self.support_reference and "reference" in schema.keys():
            reference_options = schema.pop("reference", dict())
            _ref_path = path + ".reference"
            if not isinstance(reference_options, dict):
                raise SchemaError("Must be a dictionary.", _ref_path)

            _ref_dic_path = _ref_path + "."
            _key = "key"
            if _key not in reference_options.keys():
                raise SchemaError("Key missing", _ref_dic_path + _key)
            self.ref_key = reference_options.pop(_key)
            if not isinstance(self.ref_key, str):
                raise SchemaError("Must be a string", _ref_dic_path + _key)

            mode = reference_options.pop("mode", "unique")
            u_scope = reference_options.pop("unique_scope", "global")
            p_scope = reference_options.pop("producer_scope", "global")
            c_scope = reference_options.pop("consumer_scope", "global")
            orphan = reference_options.pop("allow_orphan_producer", True)
            credits = reference_options.pop("credits", None)
            if mode == "unique":
                self.ref_OPT = OPT.UNIQUE | OPT.PRODUCER
            elif mode == "producer":
                self.ref_OPT = OPT.PRODUCER
            elif mode == "consumer":
                self.ref_OPT = OPT.CONSUMER
            else:
                raise SchemaError("Unsupported mode", _ref_dic_path + "mode")
            if OPT.UNIQUE in self.ref_OPT:
                if u_scope == "global":
                    self.ref_OPT = self.ref_OPT | OPT.UNIQUE_GLOBAL
                elif u_scope != "namespace":
                    raise SchemaError(
                        "Must be either 'global' or 'namespace'",
                        _ref_dic_path + "unique_scope",
                    )
                if credits is None or credits >= 0:
                    self.ref_credits = credits
                else:
                    raise SchemaError(
                        "Must be >=0",
                        _ref_dic_path + "credits",
                    )
            if OPT.PRODUCER in self.ref_OPT:
                if p_scope == "global":
                    self.ref_OPT = self.ref_OPT | OPT.PRODUCER_GLOBAL
                elif p_scope != "namespace":
                    raise SchemaError(
                        "Must be either 'global' or 'namespace'",
                        _ref_dic_path + "producer_scope",
                    )
                if orphan:
                    self.ref_OPT = self.ref_OPT | OPT.ALLOW_ORPHAN_PRODUCER
                if credits is None or credits >= 0:
                    self.ref_credits = credits
                else:
                    raise SchemaError(
                        "Must be >=0",
                        _ref_dic_path + "credits",
                    )
            if OPT.CONSUMER in self.ref_OPT:
                if c_scope == "global":
                    self.ref_OPT = self.ref_OPT | OPT.CONSUMER_GLOBAL
                elif c_scope != "namespace":
                    raise SchemaError(
                        "Must be either 'global' or 'namespace'",
                        _ref_dic_path + "consumer_scope",
                    )
                if credits is None:
                    self.ref_credits = 1
                elif credits > 0:
                    self.ref_credits = credits
                else:
                    raise SchemaError(
                        "Must be >0",
                        _ref_dic_path + "credits",
                    )

            if not isinstance(orphan, bool):
                raise SchemaError(
                    "Must be bool", _ref_dic_path + "allow_orphan_producer"
                )
            if len(reference_options):
                raise SchemaError(
                    "Unknown option keys '%s'" % ",".join(reference_options.keys()),
                    _ref_path + "reference",
                )

        # Parse BaseDataType options
        _path = path + "."
        for option, required, cls, init_value in self.options:
            if option in schema.keys():
                value = schema[option]
                if isinstance(cls, list):
                    found = False
                    for _cls in cls:
                        if isinstance(value, _cls):
                            found = True
                            break
                    if not found:
                        raise SchemaError("Wrong value type", _path + option)
                elif not isinstance(value, cls):
                    raise SchemaError("Wrong value type", _path + option)
                exec("self." + option + " = value")
                schema.pop(option, None)
            elif required:
                raise SchemaError("Option missing", _path + option)
        if len(schema):
            raise SchemaError("Unknown option", _path + list(schema.keys())[0])

        self.verify_options(path=_path)

        return self

    def verify_options(self, path: str) -> None:
        return

    def validate_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        if not self.data_matches_type(data):
            FL.append(
                DataTypeMismatch(path=path, message=self.data_type_mismatch_message)
            )
            return FL
        FL += self.verify_reference(data, path, RTE)
        FL += self.verify_data(data, path, RTE)
        return FL

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        return FindingsList()

    def build_sub_references(self, data: any, path: str, RTE: RunTimeEnv) -> None:
        return

    def build_references(self, data: any, path: str, RTE: RunTimeEnv) -> None:
        if self.data_matches_type(data):
            self.verify_reference(data=data, path=path, RTE=RTE)
            self.build_sub_references(data=data, path=path, RTE=RTE)

    def autogenerate_data(self, data: any, path: str, RTE: RunTimeEnv):
        return data, FindingsList()

    def get_reference_data(self, data: any, path: str) -> any:
        return data, FindingsList()

    def get_reference_element(self, path: str, ref_data: any) -> any:
        return ReferenceElement(
            reference_key=self.ref_key,
            path=path,
            value=ref_data,
            options=self.ref_OPT,
            credits=self.ref_credits,
        )

    def verify_reference(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        if not self.support_reference or OPT.NONE in self.ref_OPT:
            return FL
        ref_data, _FL = self.get_reference_data(data, path)
        FL += _FL
        ref_element = self.get_reference_element(path, ref_data)
        if OPT.UNIQUE in self.ref_OPT:
            other = RTE.references.same_unique(ref_element)
            if other is not None:
                if other.namespace != RTE.references.namespace:
                    _path = "%s > %s" % (other.namespace, other.path)
                else:
                    _path = other.path
                FL.append(
                    ReferenceFinding(
                        path=path,
                        message="Unique value already used at '%s'" % _path,
                        reference=ref_element,
                    )
                )
                return FL
        # If unique or just for producer/consumer mapping, add element to references
        RTE.references.add_element(ref_element)
        return FL
