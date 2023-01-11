from __future__ import annotations

__all__ = ["Annotation", "Attribute"]

import abc
from typing import Any, Dict, List, Set, Optional

from medkit.core.id import generate_id


class Annotation(abc.ABC):
    def __init__(
        self,
        label: str,
        keys: Optional[Set[str]] = None,
        attrs: Optional[List[Attribute]] = None,
        uid: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Provide common initialization for annotation instances

        Parameters
        ----------
        label: str
            The annotation label
        keys: Set[str], Optional
            The set of pipeline output keys which annotation belongs to
        attrs:
            The attributes of the annotation
        uid: str, Optional
            The annotation identifier
        metadata: dict
            The dictionary containing the annotation metadata
        """
        if uid is None:
            uid = generate_id()
        if attrs is None:
            attrs = []
        if metadata is None:
            metadata = {}

        self.uid: str = uid
        self.label: str = label
        self.keys: Set[str] = keys if keys is not None else set()
        self.metadata: Dict[str, Any] = metadata

        self._attrs_by_id: Dict[str, Attribute] = {}
        self._attr_ids_by_label: Dict[str, List[str]] = {}
        for attr in attrs:
            self.add_attr(attr)

    def add_attr(self, attr: Attribute):
        """
        Attach an attribute to the annotation.

        Parameters
        ----------
        attr:
            Attribute to add.

        Raises
        ------
        ValueError
            If the attribute is already attached to the annotation
            (based on `attr.uid`).
        """
        uid = attr.uid
        if attr.uid in self._attrs_by_id:
            raise ValueError(f"Attribute with uid {uid} already attached to annotation")

        # TODO: we should probably store attributes in a Store,
        # the same way annotations in a document are stored in a Store because:
        # - ProvBuilder already adds attributes to the store
        # - an attribute can be shared among several annotations
        self._attrs_by_id[uid] = attr

        label = attr.label
        if label not in self._attr_ids_by_label:
            self._attr_ids_by_label[label] = []
        self._attr_ids_by_label[label].append(uid)

    def get_attrs(self) -> List[Attribute]:
        """
        Return the attributes of the annotation.

        Returns
        -------
        List[Attribute]
            List of all the attributes attached to the annotation.
        """
        return list(self._attrs_by_id.values())

    def get_attrs_by_label(self, label: str) -> List[Attribute]:
        """
        Return the attributes of the annotation having a specific label.

        Returns
        -------
        List[Attribute]
            List of all the attributes attached to the annotation
            with labels equal to `label`.
        """

        return [
            self._attrs_by_id[uid] for uid in self._attr_ids_by_label.get(label, [])
        ]

    def add_key(self, key: str):
        self.keys.add(key)

    def keep_keys(self, keys):
        self.keys.intersection_update(keys)

    def to_dict(self) -> Dict[str, Any]:
        attrs = [a.to_dict() for a in self._attrs_by_id.values()]
        return dict(
            uid=self.uid,
            keys=list(self.keys),
            label=self.label,
            attrs=attrs,
            metadata=self.metadata,
            class_name=self.__class__.__name__,
        )

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, annotation_dict: Dict[str, Any]) -> Annotation:
        raise NotImplementedError

    def __repr__(self):
        return str(self.to_dict())


class Attribute:
    def __init__(
        self,
        label: str,
        value: Optional[Any] = None,
        uid: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a medkit attribute, to be added to an annotation

        Parameters
        ----------
        label: str
            The attribute label
        value: str, Optional
            The value of the attribute
        uid: str, Optional
            The identifier of the attribute (if existing)
        metadata: Dict[str, Any], Optional
            The metadata of the attribute
        """
        if uid is None:
            uid = generate_id()
        if metadata is None:
            metadata = {}

        self.uid: str = uid
        self.label: str = label
        self.value: Optional[Any] = value
        self.metadata: Dict[str, Any] = metadata

    def to_dict(self) -> Dict[str, Any]:
        return dict(
            uid=self.uid,
            label=self.label,
            value=self.value,
            metadata=self.metadata,
        )

    @classmethod
    def from_dict(cls, attribute_dict: Dict[str, Any]) -> Attribute:
        """
        Creates an Attribute from a dict

        Parameters
        ----------
        attribute_dict: dict
            A dictionary from a serialized Attribute as generated by to_dict()
        """
        return cls(
            uid=attribute_dict["uid"],
            label=attribute_dict["label"],
            value=attribute_dict["value"],
            metadata=attribute_dict["metadata"],
        )

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__} : uid={self.uid!r}, label={self.label!r},"
            f" value={self.value}"
        )
