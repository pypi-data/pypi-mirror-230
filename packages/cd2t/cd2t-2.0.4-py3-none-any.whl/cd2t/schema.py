from cd2t.types.datatype import DataType


class Schema(dict):
    def __init__(
        self, root_data_type: DataType = None, version: int = 1, description: str = ""
    ) -> None:
        super().__init__()
        self.root_data_type = root_data_type
        self.version = version
        self.description = description
        self.custom_data_types = dict()
        self.subschemas = dict()
        if root_data_type is not None:
            self._check_rdt(root_data_type)

    @staticmethod
    def _check_rdt(rdt: DataType):
        if not issubclass(type(rdt), DataType):
            raise ValueError(
                "Parameter 'root_data_type' is not a subclass to '%s'" % DataType
            )

    def set_root_data_type(self, root_data_type):
        self._check_rdt(root_data_type)
        self.root_data_type = root_data_type


class SchemaError(ValueError):
    def __init__(self, message: str, path="") -> None:
        super().__init__()
        self.path = path
        self.message = message

    def __str__(self):
        if self.path:
            return "%s: %s" % (self.path, self.message)
        return self.message
