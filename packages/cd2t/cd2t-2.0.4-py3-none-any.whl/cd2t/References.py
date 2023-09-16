import enum
from cd2t.results import ValidationFinding, Finding


class OPT(enum.IntFlag):
    NONE = 1
    UNIQUE = 2
    UNIQUE_GLOBAL = 4
    PRODUCER = 8
    PRODUCER_GLOBAL = 16
    CONSUMER = 32
    CONSUMER_GLOBAL = 64
    ALLOW_ORPHAN_PRODUCER = 128


INIT_OPTIONS = OPT.UNIQUE | OPT.UNIQUE_GLOBAL | OPT.PRODUCER | OPT.PRODUCER_GLOBAL


class ReferenceError(Exception):
    pass


class ReferenceElement:
    """ReferenceElement stores all information regarding a reference value analyzed in data"""

    def __init__(
        self,
        reference_key: str = "",
        path: str = "",
        value: any = None,
        options: OPT = INIT_OPTIONS,
        namespace: str = "",
        credits=None,
    ) -> None:
        """
        Args:
            reference_key: string - Reference key from schema definition

            path: string - Value's path in data structure

            value: any - Value data

            options: OPT object - indicator for reference options (mode, scope, ...)

            namespace: string - active namepsace during reference creation

        Raises:
            ValueError: If arg's data type is wrong.
        """
        if not isinstance(namespace, str):
            raise ValueError("'namespace' not a string")
        self.namespace = namespace
        if not isinstance(reference_key, str):
            raise ValueError("'reference' not a string")
        self.reference_key = reference_key
        if not isinstance(path, str):
            raise ValueError("'path' not a string")
        self.path = path
        if not isinstance(options, OPT):
            raise ValueError("'options' not a OPT object")
        self.options = options
        self.value = value
        self.credits = credits
        self.consumes_from = list()
        self.provides_to = list()


class ConsumerElement(ReferenceElement):
    """
    Sub-class to ReferenceElement
    Specialized for Condumer References
    """

    def __init__(
        self,
        reference_key: str = "",
        path: str = "",
        value: any = None,
        options: OPT = INIT_OPTIONS,
        namespace: str = "",
        credits=1,
        provider_namespace: str = "",
    ) -> None:
        """
        Args:
            < ReferenceElement's arguements >

            provider_namespace: string - namespace where to search for providers (namespace lookup feature)

        Raises:
            ValueError: If arg's data type is wrong.
        """
        super().__init__(
            reference_key=reference_key,
            path=path,
            value=value,
            options=options,
            namespace=namespace,
            credits=credits,
        )
        if not isinstance(provider_namespace, str):
            raise ValueError("'provider_namespace' not a string")
        self.provider_namespace = provider_namespace


class ReferenceFinding(Finding):
    """
    Sub-class to Finding
    ReferenceFinding stores all information to a reference issue and
    provides a method to present all information as a string (makes it easy for user interfaces)
    """

    def __init__(
        self, message: str, path: str = "", reference: ReferenceElement = None
    ) -> None:
        super().__init__(message=message, path=path)
        self.reference = reference

    def __str__(self):
        ns_lookup = False
        if (
            self.reference
            and isinstance(self.reference, ConsumerElement)
            and self.reference.provider_namespace
        ):
            ns_lookup = True
            namespace = self.reference.namespace + " > "
        elif self.reference.namespace:
            namespace = self.reference.namespace + " > "
        elif self.namespace:
            namespace = self.namespace + " > "
        else:
            namespace = ""
        path = self.path + ": " if self.path else ""
        message = (
            f"{self.message} in '{self.reference.provider_namespace}'"
            if ns_lookup
            else self.message
        )
        return namespace + path + message


class GlobalSpace:
    """
    GlobalSpace is a space where to register references in global scope.
    Adding References will stored according to the mode and
    links (consumer<>producer) to other refererences will be created.
    """

    uOPT = OPT.UNIQUE_GLOBAL
    pOPT = OPT.PRODUCER_GLOBAL
    cOPT = OPT.CONSUMER_GLOBAL

    def __init__(self) -> None:
        self.references = dict()

    def get_uniques_by_value(self, value: any, ref_key: str) -> list[ReferenceElement]:
        return self._get_elements_by_value(value, ref_key, "uniques")

    def get_producers_by_value(
        self, value: any, ref_key: str
    ) -> list[ReferenceElement]:
        return self._get_elements_by_value(value, ref_key, "producers")

    def get_consumers_by_value(
        self, value: any, ref_key: str
    ) -> list[ReferenceElement]:
        return self._get_elements_by_value(value, ref_key, "consumers")

    def _get_elements_by_value(
        self, value: any, ref_key: str, _list: str
    ) -> list[ReferenceElement]:
        if ref_key not in self.references.keys():
            return list()
        return [e for e in self.references[ref_key][_list] if e.value == value]

    def get_uniques_by_ref_key(self, ref_key: str) -> list[ReferenceElement]:
        return self.references.get(ref_key, dict()).get("uniques", list())

    def get_producers_by_ref_key(self, ref_key: str) -> list[ReferenceElement]:
        return self.references.get(ref_key, dict()).get("producers", list())

    def get_consumers_by_ref_key(self, ref_key: str) -> list[ReferenceElement]:
        return self.references.get(ref_key, dict()).get("consumers", list())

    def get_unique_values_by_ref_key(self, reference_key: str) -> set:
        """
        Returns:
            list - with all 'unique' values with the same reference key
        """
        unique_values = set()
        for e in self.get_uniques_by_ref_key(reference_key):
            unique_values.add(e.value)
        return unique_values

    def _add_ref_key(self, reference_key: str):
        """
        If reference key is new to this space,
        creates all required lists (unique,producers and consumers) for key 'ref_key' in references.

        Args:
            ref_key: string - reference key from schema definition
        """
        if reference_key in self.references.keys():
            return
        self.references[reference_key] = dict(
            uniques=list(),
            producers=list(),
            consumers=list(),
            producer_credits=dict(),
            consumer_credits=dict(),
        )

    def add_element(self, new_RE: ReferenceElement) -> list[ReferenceElement]:
        """
        Add a new reference to the space, if reference options matches the class scope:
        - stores reference according to mode in corresponding lists under the reference key
        - create all links (consumer<>producer) to other references in this space

        Args:
            new_RE: ReferenceElement object - New reference for this space

        Returns:
            list of ReferenceElements - which were linked to the new reference

        Raises:
            ReferenceError: If reference already in this space
        """
        linked_elements = list()
        self._add_ref_key(new_RE.reference_key)
        if self.uOPT in new_RE.options:
            if self.get_uniques_by_value(new_RE.value, new_RE.reference_key):
                raise ReferenceError("Reference already defined")
            self.references[new_RE.reference_key]["uniques"].append(new_RE)
        if self.pOPT in new_RE.options:
            self.references[new_RE.reference_key]["producers"].append(new_RE)
            linked_elements = self._link_to_consumers(new_RE)
            if new_RE.credits is None:
                try:
                    self.references[new_RE.reference_key]["producer_credits"][
                        new_RE.value
                    ] = None
                except TypeError:
                    self.references[new_RE.reference_key]["producer_credits"][
                        str(new_RE.value)
                    ] = None
            else:
                dict_entry = new_RE.value
                try:
                    if (
                        dict_entry
                        in self.references[new_RE.reference_key]["producer_credits"]
                    ):
                        pass
                except TypeError:
                    dict_entry = str(new_RE.value)
                if (
                    dict_entry
                    in self.references[new_RE.reference_key]["producer_credits"]
                ):
                    old_credits = self.references[new_RE.reference_key][
                        "producer_credits"
                    ][dict_entry]
                else:
                    old_credits = 0
                if old_credits is not None:
                    self.references[new_RE.reference_key]["producer_credits"][
                        dict_entry
                    ] = (old_credits + new_RE.credits)
        if self.cOPT in new_RE.options:
            self.references[new_RE.reference_key]["consumers"].append(new_RE)
            linked_elements = self._link_to_producers(new_RE)
            dict_entry = new_RE.value
            new_credits = new_RE.credits
            if new_credits is None:
                new_credits = 1
            try:
                if (
                    dict_entry
                    in self.references[new_RE.reference_key]["consumer_credits"]
                ):
                    pass
            except TypeError:
                dict_entry = str(new_RE.value)
            if dict_entry in self.references[new_RE.reference_key]["consumer_credits"]:
                old_credits = self.references[new_RE.reference_key]["consumer_credits"][
                    dict_entry
                ]
            else:
                old_credits = 0
            if old_credits is not None:
                self.references[new_RE.reference_key]["consumer_credits"][
                    dict_entry
                ] = (old_credits + new_credits)
        return linked_elements

    def _link_to_producers(self, consumer: ReferenceElement) -> list[ReferenceElement]:
        producer_list = list()
        for producer in self.references[consumer.reference_key]["producers"]:
            if (
                consumer.value == producer.value
                and producer not in consumer.consumes_from
            ):
                # Maybe linking already from another NS or in Global
                consumer.consumes_from.append(producer)
                producer.provides_to.append(consumer)
                producer_list.append(producer)
        return producer_list

    def _link_to_consumers(self, producer: ReferenceElement) -> list[ReferenceElement]:
        consumer_list = list()
        for consumer in self.references[producer.reference_key]["consumers"]:
            if (
                producer.value == consumer.value
                and consumer not in producer.provides_to
            ):
                # Maybe linking already from another NS or in Global
                producer.provides_to.append(consumer)
                consumer.consumes_from.append(producer)
                consumer_list.append(consumer)
        return consumer_list

    def get_producer_consumer_issues(self) -> list[ReferenceFinding]:
        """
        Collects and returns
        - all consumer references without a linked provider and
        - all provider references without a linked consumer, if orphan procuders are not allowed,
        as a list of ReferenceFindings

        Returns:
            list of ReferenceFindings
        """
        results = list()
        for ref_key, ref_lists in self.references.items():
            for consumer in ref_lists["consumers"]:
                if len(consumer.consumes_from) == 0:
                    # No producer found during analysis!
                    results.append(
                        ReferenceFinding(
                            path=consumer.path,
                            message="No producer found",
                            reference=consumer,
                        )
                    )
            for producer in ref_lists["producers"]:
                if (
                    OPT.ALLOW_ORPHAN_PRODUCER not in producer.options
                    and len(producer.provides_to) == 0
                ):
                    # Producer has no consumer!
                    results.append(
                        ReferenceFinding(
                            path=producer.path,
                            message="Producer has no consumer",
                            reference=producer,
                        )
                    )
        return results

    def get_credit_issues(self) -> list[ReferenceFinding]:
        """
        Checks if consumer credits exceeds provider credits.

        Returns:
            list of ReferenceFindings
        """
        results = list()
        for ref_key, ref_lists in self.references.items():
            for producer_value, producer_credits in ref_lists[
                "producer_credits"
            ].items():
                if producer_credits is not None:
                    consumer_credits = ref_lists["consumer_credits"].get(
                        producer_value, None
                    )
                    if (
                        consumer_credits is not None
                        and consumer_credits > producer_credits
                    ):
                        results.append(
                            ReferenceFinding(
                                path="n.a.",
                                message="reference key '%s': Consumer credits exceeds producer credits for value '%s'"
                                % (ref_key, str(producer_value)),
                                reference=ReferenceElement(),
                            )
                        )
        return results


class NameSpace(GlobalSpace):
    """
    Sub-class to GlobalSpace
    Namespace is a space in namespace scope
    """

    uOPT = OPT.UNIQUE
    pOPT = OPT.PRODUCER
    cOPT = OPT.CONSUMER


class References:
    """
    References stores all references according to the current active namespace and
    according to the reference options (mode, scope, ...)
    """

    def __init__(self, namespace: str = "") -> None:
        self.namespace = namespace
        self.globalspace_obj = GlobalSpace()
        self.ns_obj_store = dict()
        self._create_namespace(namespace)
        self.namespace_obj = self.ns_obj_store[namespace]

    def change_namespace(self, namespace: str) -> None:
        self._create_namespace(namespace)
        self.namespace_obj = self.ns_obj_store[namespace]
        self.namespace = namespace

    def _create_namespace(self, namespace: str) -> None:
        if namespace not in self.ns_obj_store.keys():
            self.ns_obj_store[namespace] = NameSpace()

    def add_element(self, reference: ReferenceElement) -> list[ReferenceElement]:
        """
        Add a new reference to the reference store, if reference options matches the class scope:
        - add the reference to global space and
        - if mode is consumer and provider namespace is given (namespace lookup),
          add the reference to provider namespace,
          else add the reference to the current active namespace

        Args:
            reference: ReferenceElement object - New reference for this store

        Returns:
            list of ReferenceElements - which were linked to the new reference

        Raises:
            ReferenceError: If reference already in this store
        """
        reference.namespace = self.namespace
        linked_elements = self.globalspace_obj.add_element(reference)

        if isinstance(reference, ConsumerElement) and reference.provider_namespace:
            self._create_namespace(reference.provider_namespace)
            linked_elements += self.ns_obj_store[
                reference.provider_namespace
            ].add_element(reference)
        else:
            linked_elements += self.namespace_obj.add_element(reference)
        return linked_elements

    def get_producer_consumer_issues(self):
        """
        Collects and returns
        - all consumer references without a linked provider and
        - all provider references without a linked consumer, if orphan procuders are not allowed,
        from all namespaces as a list of ReferenceFindings.
        Note: As each reference in global space is also in a namespace, globalspace is skipped.

        Returns:
            list of ReferenceFindings
        """
        credit_results = self.globalspace_obj.get_credit_issues()
        for finding in credit_results:
            finding.message = "Global " + finding.message
        results = credit_results

        for namespace, ns_obj in self.ns_obj_store.items():
            results += ns_obj.get_producer_consumer_issues()
            credit_results = ns_obj.get_credit_issues()
            for finding in credit_results:
                finding.message = "Namespace '%s' %s" % (namespace, finding.message)
            results += credit_results

        return results

    def same_unique(self, reference: ReferenceElement) -> list[ReferenceElement]:
        """
        Returns first found 'unique' references with the same reference key and value as given reference.

        Args:
            reference: ReferenceElement

        Returns:
            list of ReferenceElements
        """
        others = self.namespace_obj.get_uniques_by_value(
            reference.value, reference.reference_key
        )
        if OPT.UNIQUE_GLOBAL in reference.options:
            others += self.globalspace_obj.get_uniques_by_value(
                reference.value, reference.reference_key
            )
        if others:
            return others[0]
        return None

    def get_unique_values_by_ref_key(self, reference_key: str) -> set:
        """
        Returns all found 'unique' values with the same reference key.

        Args:
            reference_key: string

        Returns:
            list of values
        """
        ns_uniques = set(self.namespace_obj.get_unique_values_by_ref_key(reference_key))
        global_unique = set(
            self.globalspace_obj.get_unique_values_by_ref_key(reference_key)
        )
        return ns_uniques.union(global_unique)
