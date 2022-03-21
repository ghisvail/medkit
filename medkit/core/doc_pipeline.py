__all__ = ["DocPipeline"]

from typing import Dict, List

from medkit.core.document import Document, Collection
from medkit.core.pipeline import Pipeline, PipelineStep


class DocPipeline:
    """Wrapper around the `Pipeline` class that applies a list of a document or a`collection
    of documents

    Existing annotations, that are not generated by an operation in the pipeline
    but rather that should be retrieved from documents, can be handled by associating
    an annotation label to an input key. Pipeline steps using this input key will then
    receive as input all the existing document annotations having the associated label.

    All annotations generated by each operation in the pipeline will be added to
    the corresponding document.
    """

    def __init__(
        self, steps: List[PipelineStep], labels_by_input_key: Dict[str, List[str]]
    ):
        """Initialize the pipeline

        Params
        ------
        steps:
            List of pipeline steps.

            Steps will be executed in the order in which they were added,
            so make sure to add first the steps generating data used by other steps.

        labels_by_input_key:
            Mapping of input key to document annotation labels.

            This is a way to feed into the pipeline annotations
            that are not the result of a pipeline step, but that
            are pre-attached to the document on which the pipeline
            is running.

            For all pipeline step using `key` as an input key,
            the annotations of the document having the label `label'
            will be used as input.

            It is possible to associate several labels to one key,
            as well as to associate a label to several keys
        """

        input_keys = list(labels_by_input_key.keys())
        pipeline_steps = [
            PipelineStep(s.operation, s.input_keys, s.output_keys) for s in steps
        ]
        self._pipeline: Pipeline = Pipeline(
            steps=pipeline_steps,
            input_keys=input_keys,
            output_keys=[],
        )

        self.labels_by_input_key: Dict[str, List[str]] = labels_by_input_key

    def run_on_doc(self, doc: Document):
        """Run the pipeline on a document.

        Params
        ------
        doc:
            The document on which to run the pipeline.
            Labels to input keys association will be used to retrieve existing
            annotations from this document, and all new annotations will also
            be added to this document.
        """
        all_input_anns = {}
        for input_key, labels in self.labels_by_input_key.items():
            for label in labels:
                if input_key not in all_input_anns:
                    all_input_anns[input_key] = doc.get_annotations_by_label(label)
                else:
                    all_input_anns[input_key] += doc.get_annotations_by_label(label)

        self._pipeline.set_doc(doc)
        self._pipeline.process(*all_input_anns.values())

    def run_on_collection(self, collection: Collection):
        """Run the pipeline on a collection of document.

        Params
        ------
        collection:
            The collection on which to run the pipeline.
            `run_on_doc()` will be called for each document
            in the collection.
        """
        for doc in collection.documents:
            self.run_on_document(doc)
