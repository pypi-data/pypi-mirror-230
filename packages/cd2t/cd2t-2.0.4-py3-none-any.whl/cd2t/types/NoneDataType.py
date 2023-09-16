from cd2t.types.base import BaseDataType
from cd2t.RunTimeEnv import RunTimeEnv


class NoneDataType(BaseDataType):
    customizable = True
    data_type_name = "none"

    def __init__(self) -> None:
        super().__init__()
        self.matching_classes.append(type(None))
