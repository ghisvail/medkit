from __future__ import annotations

__all__ = ["Collection", "Document"]

from typing import Any, Dict, Generic, List, Optional, Set, TypeVar, cast

from medkit.core.id import generate_id
from medkit.core.annotation import Annotation
from medkit.core.store import Store, DictStore

AnnotationType = TypeVar("AnnotationType", bound=Annotation)


class Document(Generic[AnnotationType]):
    """Document holding annotations

    Annotations must be subclasses of `Annotation`."""

    def __init__(
        self,
        doc_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        store: Optional[Store] = None,
    ):
        """
        Parameters
        ----------
        doc_id:
            Id of the document in UUID format. Auto-generated if none provided
        metadata:
            Metadata of the document
        store:
            Optional shared store to hold the document annotations. If none provided,
            an internal store will be used.
        """
        if doc_id is None:
            doc_id = generate_id()
        if metadata is None:
            metadata = {}
        if store is None:
            store = DictStore()
            has_shared_store = False
        else:
            has_shared_store = True

        self.id: str = doc_id
        self.store: Store = store
        self.has_shared_store = has_shared_store
        self.annotation_ids: Set[str] = set()
        self.annotation_ids_by_label: Dict[str, List[str]] = {}
        self.annotation_ids_by_key: Dict[str, List[str]] = {}
        self.metadata: Dict[str, Any] = metadata  # TODO: what is metadata format ?

    def add_annotation(self, annotation: AnnotationType):
        """
        Add the annotation to this document

        Parameters
        ----------
        annotation:
            Annotation to add.

        Raises
        ------
        ValueError
            If `annotation.id` is already in Document.annotations.
        """
        id = annotation.id
        if id in self.annotation_ids:
            raise ValueError(
                f"Impossible to add this annotation.The id {id} already"
                " exists in the document"
            )

        self.annotation_ids.add(id)
        self.store.store_data_item(annotation)

        label = annotation.label
        if label not in self.annotation_ids_by_label:
            self.annotation_ids_by_label[label] = []
        self.annotation_ids_by_label[label].append(id)

        for key in annotation.keys:
            if key not in self.annotation_ids_by_key:
                self.annotation_ids_by_key[key] = []
            self.annotation_ids_by_key[key].append(id)

    def get_annotation_by_id(self, annotation_id) -> Optional[AnnotationType]:
        """Returns the annotation corresponding to `annotation_id`."""

        if annotation_id not in self.annotation_ids:
            return None
        else:
            ann = self.store.get_data_item(annotation_id)
            return cast(AnnotationType, ann)

    def get_annotations(self) -> List[AnnotationType]:
        """Returns the list of annotations of the document"""
        anns = [self.store.get_data_item(id) for id in self.annotation_ids]
        return cast(List[AnnotationType], anns)

    def get_annotations_by_key(self, key) -> List[AnnotationType]:
        """Returns the list of annotations of the document using the processing key"""
        anns = [
            self.store.get_data_item(id)
            for id in self.annotation_ids_by_key.get(key, [])
        ]
        return cast(List[AnnotationType], anns)

    def get_annotations_by_label(self, label) -> List[AnnotationType]:
        """Returns the list of annotations of the document using the label"""
        anns = [
            self.store.get_data_item(id)
            for id in self.annotation_ids_by_label.get(label, [])
        ]
        return cast(List[AnnotationType], anns)

    def to_dict(self) -> Dict[str, Any]:
        annotations = [
            cast(AnnotationType, self.store.get_data_item(id)).to_dict()
            for id in self.annotation_ids
        ]
        return dict(id=self.id, annotations=annotations, metadata=self.metadata)


class Collection:
    """Collection of documents"""

    def __init__(self, documents: List[Document]):
        self.documents = documents

    def to_dict(self) -> Dict[str, Any]:
        documents = [d.to_dict() for d in self.documents]
        return dict(documents=documents)
