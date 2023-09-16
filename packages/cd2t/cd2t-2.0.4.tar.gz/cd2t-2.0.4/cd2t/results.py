import re


class Finding:
    def __init__(self, message: str, path="") -> None:
        self.path = path
        self.message = message
        self.namespace = ""

    def __str__(self) -> str:
        _str = self.message
        if self.path:
            _str = self.path + ": " + _str
        if self.namespace:
            _str = self.namespace + " > " + _str
        return _str

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return str(self) > str(other)

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        return str(self) < str(other)

    def __le__(self, other):
        return self < other or self == other


class ValidationFinding(Finding):
    pass


class DataTypeMismatch(ValidationFinding):
    pass


class WrongValueFinding(ValidationFinding):
    pass


class UniqueErrorFinding(ValidationFinding):
    pass


class FindingsList(list):
    def __str__(self):
        __str_list = list()
        for finding in self:
            __str_list.append(str(finding))
        return "\n".join(__str_list)

    def set_namespace(self, namespace: str):
        for finding in self:
            finding.namespace = namespace


class AutogenerationInfo(Finding):
    pass


class AutogenerationError(AutogenerationInfo):
    pass
