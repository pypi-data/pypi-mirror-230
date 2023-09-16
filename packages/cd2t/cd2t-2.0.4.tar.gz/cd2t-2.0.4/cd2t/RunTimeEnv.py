from cd2t.types.datatype import DataType
from cd2t.References import References
from cd2t.schema import SchemaError


class RunTimeEnv:
    """Stores all information during loading schemas and data validations."""

    def __init__(
        self, namespace: str = None, version: int = 1, allow_shortcuts: bool = False
    ) -> None:
        """
        Args:
            namespace: string - Initial namespace

            data_types: dictionary
                with data type name as key and data type class as value

            allow_shortcuts: bool - Allow data type shortcuts in schemas
        """
        self.allow_shortcuts = allow_shortcuts
        self.references = References()
        self.namespace = ""
        if namespace is not None:
            self.change_namespace(namespace)
        self.data_types = dict()
        self.subschemas = dict()
        self.subschema_path = []
        self.templates = dict()
        self.templates_merge_recursive = True
        self.templates_list_merge = "append_rp"
        self.template_hash_stack = list()
        self.version = version
        try:
            from ruamel.yaml import CommentedMap, CommentedSeq

            self.ruamel_yaml_available = True
            self.CommentedMap = CommentedMap
            self.CommentedSeq = CommentedSeq
        except ImportError:
            self.ruamel_yaml_available = False

    def change_namespace(self, namespace: str) -> None:
        """
        Args:
            namespace: string - New namespace
        """
        if not isinstance(namespace, str):
            raise ValueError("namespace has to be a string")
        self.references.change_namespace(namespace)
        self.namespace = namespace
