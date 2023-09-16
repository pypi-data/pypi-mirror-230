from cd2t.types.base import BaseDataType
from cd2t.results import (
    FindingsList,
    WrongValueFinding,
    AutogenerationError,
    AutogenerationInfo,
)
from cd2t.References import OPT, ReferenceElement
from cd2t.schema import SchemaError
from cd2t.RunTimeEnv import RunTimeEnv
import itertools
import random


class Integer(BaseDataType):
    customizable = True
    data_type_name = "integer"
    matching_classes = [int]
    support_reference = True
    options = [
        # option_name, required, class, default value
        ("maximum", False, int, None),
        ("minimum", False, int, None),
        ("not_allowed_values", False, list, list()),
        ("autogenerate", False, bool, False),
        ("autogenerate_default", False, int, None),
        ("autogenerate_maximum", False, int, None),
        ("autogenerate_minimum", False, int, None),
        ("autogenerate_find", False, str, "next_higher"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.minimum = None
        self.maximum = None
        self.not_allowed_values = list()
        self.autogenerate = False
        self.autogenerate_default = None
        self.autogenerate_find = "next_higher"
        self.autogenerate_minimum = None
        self.autogenerate_maximum = None

    def verify_options(self, path: str):
        for integer in self.not_allowed_values:
            if not isinstance(integer, int):
                raise SchemaError(
                    "Non-integer not allowed", path + "not_allowed_values"
                )
        if self.autogenerate_find not in ["next_higher", "next_lower", "random"]:
            raise SchemaError(
                "Must be 'next_higher' or 'next_lower'", path + "autogenerate_find"
            )
        if self.autogenerate:
            if self.autogenerate_default is not None:
                pass
            elif self.autogenerate_find == "next_higher" and not (
                self.autogenerate_minimum or self.minimum
            ):
                raise SchemaError(
                    "'next_higher' needs option 'minimum' or 'autogenerate_minimum'",
                    path + "autogenerate_find",
                )
            elif self.autogenerate_find == "next_lower" and not (
                self.autogenerate_maximum or self.maximum
            ):
                raise SchemaError(
                    "'next_lower' needs option 'maximum' or 'autogenerate_maximum'",
                    path + "autogenerate_find",
                )
            elif self.autogenerate_find == "random" and (
                not (self.autogenerate_minimum or self.minimum)
                or not (self.autogenerate_maximum or self.maximum)
            ):
                raise SchemaError(
                    "'random' needs options 'minimum' or 'autogenerate_minimum'"
                    + " and 'maximum' or 'autogenerate_maximum'",
                    path + "autogenerate_find",
                )
        super().verify_options(path)

    def autogenerate_data(self, data: any, path: str, RTE: RunTimeEnv):
        FL = FindingsList()
        if data is not None or not self.autogenerate:
            return data, FL
        # We need to autogenerate
        if self.autogenerate_default is not None:
            data = self.autogenerate_default

        elif self.autogenerate_find == "next_lower":
            start = (
                self.autogenerate_maximum
                if self.autogenerate_maximum is not None
                else self.maximum
            )
            end = (
                self.autogenerate_minimum
                if self.autogenerate_minimum is not None
                else self.minimum
            )
            if OPT.UNIQUE not in self.ref_OPT:
                data = start
            else:
                all_uniques = RTE.references.get_unique_values_by_ref_key(self.ref_key)
                blocked = all_uniques.union(set(self.not_allowed_values))
                _iter = itertools.filterfalse(
                    blocked.__contains__, itertools.count(start=start, step=-1)
                )
                data = next(_iter)
                if end is not None and data < end:
                    data = None
                else:
                    new_element = ReferenceElement(
                        self.ref_key, path, data, self.ref_OPT
                    )
                    RTE.references.add_element(new_element)

        elif self.autogenerate_find == "next_higher":
            start = (
                self.autogenerate_minimum
                if self.autogenerate_minimum is not None
                else self.minimum
            )
            end = (
                self.autogenerate_maximum
                if self.autogenerate_maximum is not None
                else self.maximum
            )
            if OPT.UNIQUE not in self.ref_OPT:
                data = start
            else:
                all_uniques = RTE.references.get_unique_values_by_ref_key(self.ref_key)
                blocked = all_uniques.union(set(self.not_allowed_values))
                _iter = itertools.filterfalse(
                    blocked.__contains__, itertools.count(start=start, step=1)
                )
                data = next(_iter)
                if end is not None and data > end:
                    data = None
                else:
                    new_element = ReferenceElement(
                        self.ref_key, path, data, self.ref_OPT
                    )
                    RTE.references.add_element(new_element)

        elif self.autogenerate_find == "random":
            start = (
                self.autogenerate_minimum
                if self.autogenerate_minimum is not None
                else self.minimum
            )
            end = (
                self.autogenerate_maximum
                if self.autogenerate_maximum is not None
                else self.maximum
            )
            min_max_values = set(range(start, end + 1))
            allowed_values = min_max_values - set(self.not_allowed_values)
            if allowed_values and OPT.UNIQUE in self.ref_OPT:
                available_values = (
                    allowed_values
                    - RTE.references.get_unique_values_by_ref_key(self.ref_key)
                )
                if available_values:
                    data = list(available_values)[
                        random.randint(0, len(available_values) - 1)
                    ]
                    new_element = ReferenceElement(
                        self.ref_key, path, data, self.ref_OPT
                    )
                    RTE.references.add_element(new_element)
            elif allowed_values:
                data = list(allowed_values)[random.randint(0, len(allowed_values) - 1)]

        if data is None:
            FL.append(AutogenerationError(path=path, message="All values in use!"))
        else:
            FL.append(
                AutogenerationInfo(
                    path=path, message="Autogenerated value is %d" % data
                )
            )
        return data, FL

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        if self.minimum is not None and self.minimum > data:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="%d is lower than minimum %d" % (data, self.minimum),
                )
            )
        elif self.maximum is not None and self.maximum < data:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="%d is higher than maximum %d" % (data, self.maximum),
                )
            )
        elif data in self.not_allowed_values:
            FL.append(WrongValueFinding(path=path, message="%d is not allowed" % data))
        return FL
