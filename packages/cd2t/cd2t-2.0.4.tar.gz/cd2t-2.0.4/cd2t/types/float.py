from cd2t.types.base import BaseDataType
from cd2t.schema import SchemaError
from cd2t.results import (
    WrongValueFinding,
    AutogenerationError,
    AutogenerationInfo,
    FindingsList,
)
from cd2t.References import ReferenceElement, OPT
from cd2t.RunTimeEnv import RunTimeEnv
import random


class Float(BaseDataType):
    customizable = True
    data_type_name = "float"
    matching_classes = [float]
    support_reference = True
    options = [
        # option_name, required, class
        ("maximum", False, float, None),
        ("minimum", False, float, None),
        ("maximum_decimals", False, int, None),
        ("allowed_values", False, list, list()),
        ("not_allowed_values", False, list, list()),
        ("autogenerate", False, bool, False),
        ("autogenerate_default", False, float, None),
        ("autogenerate_ranges", False, list, list()),
        ("autogenerate_random_tries", False, int, 10),
        ("autogenerate_random_decimals", False, int, 2),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.minimum = None
        self.maximum = None
        self.maximum_decimals = None
        self.allowed_values = list()
        self.allowed_dic = dict(
            discrete=list(),  # of floats
            round=list(),  # of tuples (decimals :int, matches :float)
            ranges=list(),  # of tuples (start :float, end :float)
        )
        self.not_allowed_values = list()
        self.not_allowed_dic = dict(
            discrete=list(),  # of floats
            round=list(),  # of tuples (decimals :int, matches :float)
            ranges=list(),  # of tuples (start :float, end :float)
        )
        self.autogenerate = False
        self.autogenerate_default = None
        self.autogenerate_ranges = list()
        self.autogen_ranges = list()  # of tuples (start :float, end :float)
        self.autogenerate_random_tries = 10
        self.autogenerate_random_decimals = 2

    def verify_options(self, path: str):
        def parse_value_list(values: list, self_dic: dict, option: str) -> None:
            i = 0
            for element in values:
                valid = False
                if isinstance(element, float):
                    self_dic["discrete"].append(element)
                    valid = True
                elif isinstance(element, dict) and len(element) == 2:
                    _round = element.get("round", None)
                    _match = element.get("matches", None)
                    _start = element.get("range_start", None)
                    _end = element.get("range_end", None)
                    if (
                        _round is not None
                        and isinstance(_round, int)
                        and _round > 0
                        and isinstance(_match, float)
                    ):
                        valid = True
                        self_dic["round"].append((_round, _match))
                    elif (
                        _start is not None
                        and isinstance(_start, float)
                        and isinstance(_end, float)
                        and _start <= _end
                    ):
                        valid = True
                        self_dic["ranges"].append((_start, _end))
                if not valid:
                    raise SchemaError(
                        "'%s' contains unsupported directive at position %d"
                        % (option, i),
                        path,
                    )
                i += 1

        if (
            self.maximum is not None
            and self.minimum is not None
            and self.maximum < self.minimum
        ):
            raise SchemaError("'maximum' must be greater or equal to 'minimum'", path)

        if self.maximum_decimals is not None and not 0 <= self.maximum_decimals:
            raise SchemaError("'maximum_decimals' must be greater or equal to 0", path)

        parse_value_list(self.allowed_values, self.allowed_dic, "allowed_values")
        parse_value_list(
            self.not_allowed_values, self.not_allowed_dic, "not_allowed_values"
        )

        if (
            self.autogenerate
            and self.autogenerate_default is None
            and not self.autogenerate_ranges
            and self.maximum is None
            and self.minimum is None
        ):
            raise SchemaError(
                "'autogenerate_default' or 'autogenerate_ranges' or ('maximum' and 'minimum') "
                + "must be set if 'autogenerate' is true",
                path,
            )
        if self.autogenerate_default and OPT.UNIQUE in self.ref_OPT:
            raise SchemaError(
                "'autogenerate_default' and 'reference.mode' == 'unique' is not allowed.",
                path,
            )
        if not 0 < self.autogenerate_random_tries < 50:
            raise SchemaError(
                "'autogenerate_random_tries' must be greater 0 and lower than 50", path
            )
        if not 0 <= self.autogenerate_random_decimals:
            raise SchemaError(
                "'autogenerate_random_decimals' must be greater or equal to 0", path
            )
        i = 0
        min = "minimum"
        max = "maximum"
        for e in self.autogenerate_ranges:
            if (
                isinstance(e, dict)
                and min in e.keys()
                and isinstance(e[min], float)
                and max in e.keys()
                and isinstance(e[max], float)
                and e[min] <= e[max]
            ):
                self.autogen_ranges.append((e[min], e[max]))
            else:
                raise SchemaError(
                    "'autogenerate_ranges' contains unsupported directive at position %d"
                    % i,
                    path,
                )
            i += 1
        super().verify_options(path)

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        def matches_values(value: float, value_dic: dict):
            if value in value_dic["discrete"]:
                return True
            for _round, _match in value_dic["round"]:
                if round(value, _round) == _match:
                    return True
            for _min, _max in value_dic["ranges"]:
                if _min <= value <= _max:
                    return True
            return False

        FL = FindingsList()
        if self.minimum is not None and self.minimum > data:
            FL.append(
                WrongValueFinding(
                    "%s is lower than 'minimum' of %s" % (data, self.minimum), path
                )
            )
        elif self.maximum is not None and self.maximum < data:
            FL.append(
                WrongValueFinding(
                    "%s is higher than 'maximum' of %s" % (data, self.maximum), path
                )
            )
        if (
            self.maximum_decimals is not None
            and round(data, self.maximum_decimals) != data
        ):
            FL.append(
                WrongValueFinding(
                    "%s's decimal places is higher than maximum %d"
                    % (data, self.maximum_decimals),
                    path,
                )
            )
        if matches_values(data, self.not_allowed_dic) or (
            self.allowed_values and not matches_values(data, self.allowed_dic)
        ):
            FL.append(WrongValueFinding(path=path, message="%s is not allowed" % data))
        return FL

    def autogenerate_data(self, data: any, path: str, RTE: RunTimeEnv):
        FL = FindingsList()
        if data is not None or not self.autogenerate:
            return data, FL
        # We need to autogenerate
        new_value = None
        new_element = None
        if self.autogenerate_default:
            new_value = self.autogenerate_default
        else:
            random_float = None
            for i in range(self.autogenerate_random_tries):
                if not self.autogenerate_ranges:
                    min = self.minimum
                    max = self.maximum
                else:
                    random_list_key = round(random.uniform(1, len(self.autogen_ranges)))
                    min, max = self.autogen_ranges[random_list_key - 1]
                random_float = round(
                    random.uniform(min, max), self.autogenerate_random_decimals
                )
                results = self.verify_data(random_float, path, RTE)
                if not len(results):
                    if not OPT.NONE in self.ref_OPT:
                        new_element = ReferenceElement(
                            self.ref_key, path, random_float, self.ref_OPT
                        )
                        if (
                            OPT.UNIQUE in self.ref_OPT
                            and RTE.references.same_unique(new_element) is not None
                        ):
                            continue
                        RTE.references.add_element(new_element)
                    new_value = random_float
                    break
        if new_value is None:
            FL.append(
                AutogenerationError(
                    path=path,
                    message="Failed to find a valid random value after %d tries."
                    % self.autogenerate_random_tries,
                )
            )
        else:
            FL.append(
                AutogenerationInfo(
                    path=path, message="Autogenerated value is %s" % str(new_value)
                )
            )
        return new_value, FL
