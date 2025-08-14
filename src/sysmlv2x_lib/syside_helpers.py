from typing import Iterable, Sequence
import syside


def _get_document_containing(
    model: syside.Model, element_name: str
) -> syside.SharedMutex[syside.Document]:
    found_document = None
    for document in model.all_docs:
        with document.lock() as locked:
            try:
                _ = locked.root_node[element_name]
                if found_document is not None:
                    raise ValueError(
                        f"Multiple root namespaces define this element: {element_name}"
                    )
                found_document = document
            except KeyError:
                pass
    if found_document is None:
        raise ValueError(f"Element not found in root namespace: {element_name}.")
    return found_document


def _get_node_by_qualified_name(
    node: syside.Namespace, qualified_name: Iterable[str]
) -> syside.Element:
    current_node: syside.Element = node
    for segment in qualified_name:
        assert isinstance(current_node, syside.Namespace)
        current_node = current_node[segment]
    return current_node


def get_node(model: syside.Model, qualified_name: Sequence[str]) -> syside.Element:
    """Get an element by its qualified name.

    Important! According to KerML 8.2.3.5.4 Full Resolution, there can be multiple
    elements with the same qualified name:

        Note. It is possible that there will be more than one Membership in the global
        Namespace that resolves a given simple name. In this case, one of these
        Memberships is chosen for the resolution of the name, but which one is chosen is
        not otherwise determined by this specification.

    To avoid ambiguity, this function explicitly checks that there is only a single
    element with the given ``qualified_name``.

    """
    root_element = qualified_name[0]
    document = _get_document_containing(model, root_element)
    with document.lock() as locked:
        return _get_node_by_qualified_name(locked.root_node, qualified_name)


def set_feature_value(
    model: syside.Model, qualified_name: Sequence[str], value: int
) -> None:
    root_element = qualified_name[0]
    document = _get_document_containing(model, root_element)
    with document.lock() as locked:
        node = _get_node_by_qualified_name(locked.root_node, qualified_name)
        assert isinstance(node, syside.Feature)
        if isinstance(value, int):
            value_node = node.feature_value_member.set_member_element(
                syside.LiteralInteger
            )[1]
            value_node.value = value
        elif isinstance(value, bool):
            value_node = node.feature_value_member.set_member_element(
                syside.LiteralBoolean
            )[1]
            value_node.value = value
        else:
            raise NotImplementedError(f"{type(value)}: {value}")


def pprint_sysml(node: syside.Element) -> str:
    cfg = syside.PrinterConfig(line_width=80, tab_width=2)
    printer = syside.ModelPrinter.sysml()
    return syside.pprint(node, printer, cfg)
