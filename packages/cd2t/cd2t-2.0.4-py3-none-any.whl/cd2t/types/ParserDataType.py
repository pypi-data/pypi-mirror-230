import cd2t.types.datatype
import cd2t.types.base
import cd2t.types.bool
import cd2t.types.enum
import cd2t.types.float
import cd2t.types.fqdn
import cd2t.types.hostname
import cd2t.types.idlist
import cd2t.types.integer
import cd2t.types.ip
import cd2t.types.List
import cd2t.types.multitype
import cd2t.types.NoneDataType
import cd2t.types.object
import cd2t.types.schema
import cd2t.types.string
import cd2t.RunTimeEnv
from typing import Union
from cd2t.schema import Schema, SchemaError
from cd2t.utils import merge_dictionaries
from hashlib import sha1

BUILTIN_DATA_TYPES = {
    1: dict(
        any=cd2t.types.base.BaseDataType,
        bool=cd2t.types.bool.Bool,
        enum=cd2t.types.enum.Enum,
        float=cd2t.types.float.Float,
        idlist=cd2t.types.idlist.IDList_V1,
        integer=cd2t.types.integer.Integer,
        list=cd2t.types.List.List,
        multitype=cd2t.types.multitype.Multitype,
        none=cd2t.types.NoneDataType.NoneDataType,
        object=cd2t.types.object.Object_V1,
        schema=cd2t.types.schema.SchemaDataType,
        string=cd2t.types.string.String,
    ),
    2: dict(
        any=cd2t.types.base.BaseDataType,
        bool=cd2t.types.bool.Bool,
        enum=cd2t.types.enum.Enum,
        float=cd2t.types.float.Float,
        fqdn=cd2t.types.fqdn.FQDN,
        hostname=cd2t.types.hostname.Hostname,
        idlist=cd2t.types.idlist.IDList_V2,
        integer=cd2t.types.integer.Integer,
        ip=cd2t.types.ip.IP,
        ip_address=cd2t.types.ip.IP_Address,
        ip_network=cd2t.types.ip.IP_Network,
        ip_interface=cd2t.types.ip.IP_Interface,
        list=cd2t.types.List.List,
        multitype=cd2t.types.multitype.Multitype,
        none=cd2t.types.NoneDataType.NoneDataType,
        object=cd2t.types.object.Object_V2,
        string=cd2t.types.string.String,
    ),
}


class ParserDataType:
    def __init__(self) -> None:
        self.DATA_TYPE_VERSION = BUILTIN_DATA_TYPES

    def build_schema(
        self,
        schema: Union[dict, str],
        path: int,
        RTE: cd2t.RunTimeEnv.RunTimeEnv,
        schema_obj: Schema = Schema(),
    ) -> cd2t.types.datatype.DataType:
        template = None
        if isinstance(schema, dict):
            schema = schema.copy()
            if len(schema) == 0:
                return self.DATA_TYPE_VERSION[RTE.version]["any"]()
            if schema_obj.version == 2:
                template = schema.pop("template", None)
                if template:
                    if template not in RTE.templates.keys():
                        raise SchemaError(
                            path=path, message="Template '%s' not found" % template
                        )
                    template_merge_options = schema.pop(
                        "template_merge_options", dict()
                    )
                    recursive = template_merge_options.get(
                        "recursive", RTE.templates_merge_recursive
                    )
                    list_merge = template_merge_options.get(
                        "list_merge", RTE.templates_list_merge
                    )
                    schema = merge_dictionaries(
                        left=RTE.templates[template],
                        right=schema,
                        recursive=recursive,
                        list_merge=list_merge,
                    )
                    hash = sha1()
                    hash.update(str(schema).encode())
                    schema_hash = hash.hexdigest()
                    if schema_hash in RTE.template_hash_stack:
                        raise SchemaError(path=path, message="Template looping")
                    RTE.template_hash_stack.append(schema_hash)
            data_type_name = schema.pop("type", None)
            if data_type_name is None:
                raise SchemaError("Needs to have a key 'type'", path)
        elif RTE.allow_shortcuts and isinstance(schema, str):
            data_type_name = schema
            schema = dict()
        else:
            raise SchemaError("Wrong value type", path)

        if data_type_name in schema_obj.custom_data_types.keys():
            schema_copy = schema
            schema = schema_obj.custom_data_types[data_type_name].copy()
            schema.update(schema_copy)
            data_type_name = schema.pop("type", None)

        data_type_class = self.DATA_TYPE_VERSION[RTE.version].get(data_type_name, None)
        if data_type_class is None:
            raise SchemaError("Data type '%s' not found" % data_type_name, path)

        data_type_obj = data_type_class().build_schema(
            schema=schema,
            path=path,
            RTE=RTE,
            schema_obj=schema_obj,
        )

        if template:
            RTE.template_hash_stack.pop()

        return data_type_obj
