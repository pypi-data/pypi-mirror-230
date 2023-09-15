from collections import Counter
from typing import Any, List

from mlflow.store.artifact.models_artifact_repo import ModelsArtifactRepository
from mlflow.store.artifact.runs_artifact_repo import RunsArtifactRepository


def is_artifact_uri(uri):
    """
    Checks the artifact URI is associated with a MLflow model or run.
    The actual URI can be a model URI, model URI + subdirectory, or model URI + path to artifact file.
    """
    return ModelsArtifactRepository.is_models_uri(
        uri
    ) or RunsArtifactRepository.is_runs_uri(uri)


def get_duplicates(elements: List[Any]) -> List[Any]:
    """
    Returns duplicate elements in the order they first appear.
    """
    element_counts = Counter(elements)
    duplicates = []
    for e in element_counts.keys():
        if element_counts[e] > 1:
            duplicates.append(e)
    return duplicates


def validate_strings_unique(strings: List[str], error_template: str):
    """
    Validates all strings are unique, otherwise raise ValueError with the error template and duplicates.
    Passes single-quoted, comma delimited duplicates to the error template.
    """
    duplicate_strings = get_duplicates(strings)
    if duplicate_strings:
        duplicates_formatted = ", ".join([f"'{s}'" for s in duplicate_strings])
        raise ValueError(error_template.format(duplicates_formatted))


def get_unique_list_order(elements: List[Any]) -> List[Any]:
    """
    Returns unique elements in the order they first appear.
    """
    return list(dict.fromkeys(elements))
