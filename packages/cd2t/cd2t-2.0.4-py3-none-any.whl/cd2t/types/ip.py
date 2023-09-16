from cd2t.types.base import BaseDataType
from cd2t.schema import SchemaError, Schema
from cd2t.results import FindingsList, WrongValueFinding
from cd2t.References import OPT, ReferenceElement, ConsumerElement
from cd2t.RunTimeEnv import RunTimeEnv
import ipaddress


class IP(BaseDataType):
    customizable = True
    data_type_name = "ip"
    matching_classes = [str]
    support_reference = True
    options = [
        # option_name, required, class, default_value
        ("loopback", False, bool, None),
        ("version", False, int, None),
        ("link_local", False, bool, None),
        ("private", False, bool, None),
        ("public", False, bool, None),
        ("multicast", False, bool, None),
        ("allowed_values", False, list, None),
        ("not_allowed_values", False, list, list()),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.loopback = None
        self.version = None
        self.link_local = None
        self.private = None
        self.public = None
        self.multicast = None
        self.allowed_values = None
        self.not_allowed_values = list()

    def verify_options(self, path: str):
        super().verify_options(path)
        if self.version is not None and self.version not in [4, 6]:
            raise SchemaError(
                path=path + "version", message="Version must either 4 or 6"
            )
        i = 0
        for string in self.not_allowed_values:
            if isinstance(string, str):
                try:
                    _ip = ipaddress.ip_interface(string)
                except ValueError:
                    raise SchemaError(
                        "Must be an IP object", "%snot_allowed_values[%d]" % (path, i)
                    )
            else:
                raise SchemaError(
                    "Must be an IP object", "%snot_allowed_values[%d]" % (path, i)
                )
            if self.version is not None and _ip.version != self.version:
                raise SchemaError(
                    path="%snot_allowed_values[%d]" % (path, i),
                    message="Must be an object of IP version %d" % self.version,
                )
            i += 1
        if self.allowed_values is not None:
            i = 0
            for string in self.allowed_values:
                if isinstance(string, str):
                    try:
                        _ip = ipaddress.ip_interface(string)
                    except ValueError:
                        raise SchemaError(
                            "Must be an IP object", "%sallowed_values[%d]" % (path, i)
                        )
                else:
                    raise SchemaError(
                        "Must be an IP object", "%sallowed_values[%d]" % (path, i)
                    )
                if self.version is not None and _ip.version != self.version:
                    raise SchemaError(
                        path="%snot_allowed_values[%d]" % (path, i),
                        message="Must be an object of IP version %d" % self.version,
                    )
                i += 1

    def verify_ip_object_type(self, data: any, path: str):
        FL = FindingsList()
        ip_obj = None
        try:
            ip_obj = ipaddress.ip_address(data)
        except ValueError:
            pass
        try:
            ip_obj = ipaddress.ip_network(data)
        except ValueError:
            pass
        try:
            ip_obj = ipaddress.ip_interface(data)
        except ValueError:
            pass
        if ip_obj is None:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Data not an IP object",
                )
            )
        return FL, ip_obj

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL, ip_obj = self.verify_ip_object_type(data=data, path=path)
        if ip_obj is None:
            return FL

        if self.version is not None and ip_obj.version != self.version:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="%s is not IP version %d" % (data, self.version),
                )
            )

        if self.loopback is not None:
            if self.loopback and not ip_obj.is_loopback:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="%s is not a loopback" % data,
                    )
                )
            if not self.loopback and ip_obj.is_loopback:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="%s mustn't be a loopback" % data,
                    )
                )

        if self.link_local is not None:
            if self.link_local and not ip_obj.is_link_local:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="%s is not link local" % data,
                    )
                )
            if not self.link_local and ip_obj.is_link_local:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="%s mustn't be link local" % data,
                    )
                )

        if self.private is not None:
            if self.private and not ip_obj.is_private:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="%s is not private" % data,
                    )
                )
            if not self.private and ip_obj.is_private:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="%s mustn't be private" % data,
                    )
                )

        if self.public is not None:
            if self.public and not ip_obj.is_global:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="%s is not public" % data,
                    )
                )
            if not self.public and ip_obj.is_global:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="%s mustn't be public" % data,
                    )
                )

        if self.multicast is not None:
            if self.multicast and not ip_obj.is_multicast:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="%s is not multicast" % data,
                    )
                )
            if not self.multicast and ip_obj.is_multicast:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="%s mustn't be multicast" % data,
                    )
                )

        if data in self.not_allowed_values:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="IP object matches not allowed IP object '%s'" % data,
                )
            )
        if self.allowed_values and data not in self.allowed_values:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="IP object '%s' matches none of the allowed IP objects"
                    % data,
                )
            )

        return FL


class __IP_Specialized(IP):
    options_special = [
        # option_name, required, class, default_value
        ("allowed_subnets", False, list, None),
        ("not_allowed_subnets", False, list, list()),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.allowed_subnets = None
        self.not_allowed_subnets = list()
        self.options = self.options + self.options_special

    def verify_options(self, path: str):
        super().verify_options(path)
        i = 0
        for string in self.not_allowed_subnets:
            if isinstance(string, str):
                try:
                    _ip = ipaddress.ip_network(string)
                except ValueError:
                    raise SchemaError(
                        "Must be an IP subnet", "%snot_allowed_subnets[%d]" % (path, i)
                    )
            else:
                raise SchemaError(
                    "Must be an IP subnet", "%snot_allowed_subnets[%d]" % (path, i)
                )
            if self.version is not None and _ip.version != self.version:
                raise SchemaError(
                    path="%snot_allowed_subnets[%d]" % (path, i),
                    message="Must be an IP version %d subnet" % self.version,
                )
            i += 1
        if self.allowed_subnets is not None:
            i = 0
            for string in self.allowed_subnets:
                if isinstance(string, str):
                    try:
                        _ip = ipaddress.ip_network(string)
                    except ValueError:
                        raise SchemaError(
                            "Must be an IP subnet", "%sallowed_subnets[%d]" % (path, i)
                        )
                else:
                    raise SchemaError(
                        "Must be an IP subnet", "%sallowed_subnets[%d]" % (path, i)
                    )
                if self.version is not None and _ip.version != self.version:
                    raise SchemaError(
                        path="%snot_allowed_subnets[%d]" % (path, i),
                        message="Must be an IP version %d subnet" % self.version,
                    )
                i += 1

    def verify_ip_object_type(self, data: any, path: str):
        return FindingsList(), None

    def verify_subnets(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        return FindingsList()

    def verify_with_special_type_options(
        self, data: any, path: str, RTE: RunTimeEnv
    ) -> FindingsList:
        return FindingsList()

    def verify_data(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = super().verify_data(data=data, path=path, RTE=RTE)
        if not FL:
            FL = self.verify_subnets(data=data, path=path, RTE=RTE)
            FL += self.verify_with_special_type_options(data=data, path=path, RTE=RTE)
        return FL


class IP_Address(__IP_Specialized):
    data_type_name = "ip_address"

    def verify_ip_object_type(self, data: any, path: str):
        FL = FindingsList()
        ip_obj = None
        try:
            ip_obj = ipaddress.ip_address(data)
        except ValueError:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Data not an IP address",
                )
            )
        return FL, ip_obj

    def verify_subnets(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        ip_obj = ipaddress.ip_address(data)

        for subnet in self.not_allowed_subnets:
            subnet_obj = ipaddress.ip_network(subnet)
            if ip_obj in subnet_obj:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="IP address '%s' within not allowed IP subnet '%s'"
                        % (data, subnet),
                    )
                )
        if self.allowed_subnets is not None:
            match = False
            for subnet in self.allowed_subnets:
                subnet_obj = ipaddress.ip_network(subnet)
                if ip_obj in subnet_obj:
                    match = True
                    break
            if not match:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="IP address '%s' matches none of the allowed IP subnets"
                        % data,
                    )
                )

        return FL


class IP_Network(__IP_Specialized):
    data_type_name = "ip_network"
    options_network = [
        # option_name, required, class, default_value
        ("minimum_prefix_length", False, int, 0),
        ("maximum_prefix_length", False, int, None),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.minimum_prefix_length = 0
        self.maximum_prefix_length = None
        self.options = self.options + self.options_network

    def verify_options(self, path: str):
        super().verify_options(path)
        if self.version == 4:
            if self.minimum_prefix_length > 32:
                raise SchemaError(
                    "Must be <= 32 for IP version 4", "%sminimum_prefix_length" % path
                )
            if self.maximum_prefix_length is not None:
                if self.minimum_prefix_length > self.maximum_prefix_length:
                    raise SchemaError(
                        "Must be >= 'minimum_prefix_length'",
                        "%smaximum_prefix_length" % path,
                    )
                if self.maximum_prefix_length > 32:
                    raise SchemaError(
                        "Must be <= 32 for IP version 4",
                        "%smaximum_prefix_length" % path,
                    )

        else:
            if self.minimum_prefix_length > 128:
                raise SchemaError("Must be <= 128", "%sminimum_prefix_length" % path)
            if self.maximum_prefix_length is not None:
                if self.minimum_prefix_length > self.maximum_prefix_length:
                    raise SchemaError(
                        "Must be >= 'minimum_prefix_length'",
                        "%smaximum_prefix_length" % path,
                    )
                if self.maximum_prefix_length > 128:
                    raise SchemaError(
                        "Must be <= 128", "%smaximum_prefix_length" % path
                    )

    def verify_ip_object_type(self, data: any, path: str):
        FL = FindingsList()
        ip_obj = None
        try:
            ip_obj = ipaddress.ip_network(data)
        except ValueError:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Data not an IP network",
                )
            )
        return FL, ip_obj

    def verify_subnets(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        ip_obj = ipaddress.ip_network(data)

        for subnet in self.not_allowed_subnets:
            subnet_obj = ipaddress.ip_network(subnet)
            if ip_obj.version == subnet_obj.version and ip_obj.subnet_of(subnet_obj):
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="IP network '%s' within not allowed IP subnet '%s'"
                        % (data, subnet),
                    )
                )
        if self.allowed_subnets is not None:
            match = False
            for subnet in self.allowed_subnets:
                subnet_obj = ipaddress.ip_network(subnet)
                if ip_obj.version == subnet_obj.version and ip_obj.subnet_of(
                    subnet_obj
                ):
                    match = True
                    break
            if not match:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="IP network '%s' matches none of the allowed IP subnets"
                        % data,
                    )
                )

        return FL

    def verify_with_special_type_options(
        self, data: any, path: str, RTE: RunTimeEnv
    ) -> FindingsList:
        FL = FindingsList()
        ip_obj = ipaddress.ip_network(data)
        if ip_obj.prefixlen < self.minimum_prefix_length:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="IP network '%s' prefix length is lower than minimum %d"
                    % (data, self.minimum_prefix_length),
                )
            )
        elif (
            self.maximum_prefix_length is not None
            and ip_obj.prefixlen > self.maximum_prefix_length
        ):
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="IP network '%s' prefix length is higher than maximum %d"
                    % (data, self.maximum_prefix_length),
                )
            )
        return FL


class IP_Interface(IP_Address):
    data_type_name = "ip_interface"

    def verify_ip_object_type(self, data: any, path: str):
        FL = FindingsList()
        ip_obj = None
        try:
            ip_obj = ipaddress.ip_interface(data)
        except ValueError:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="Data not an IP interface",
                )
            )
        if "/" not in data:
            FL.append(
                WrongValueFinding(
                    path=path,
                    message="IP address '%s' not an IP interface" % data,
                )
            )
        return FL, ip_obj

    def verify_subnets(self, data: any, path: str, RTE: RunTimeEnv) -> FindingsList:
        FL = FindingsList()
        ip_obj = ipaddress.ip_interface(data)

        for subnet in self.not_allowed_subnets:
            subnet_obj = ipaddress.ip_network(subnet)
            if ip_obj in subnet_obj:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="IP interface '%s' within not allowed IP subnet '%s'"
                        % (data, subnet),
                    )
                )
        if self.allowed_subnets is not None:
            match = False
            for subnet in self.allowed_subnets:
                subnet_obj = ipaddress.ip_network(subnet)
                if ip_obj in subnet_obj:
                    match = True
                    break
            if not match:
                FL.append(
                    WrongValueFinding(
                        path=path,
                        message="IP interface '%s' matches none of the allowed IP subnets"
                        % data,
                    )
                )

        return FL
