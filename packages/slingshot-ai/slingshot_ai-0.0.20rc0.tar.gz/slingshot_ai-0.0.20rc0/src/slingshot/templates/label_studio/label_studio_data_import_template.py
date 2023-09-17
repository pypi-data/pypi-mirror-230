import os
from typing import TypeVar

import label_studio_sdk
from pydantic import BaseModel

from slingshot.schemas import Example, ExampleResult

DATASET_MOUNT_PATH = '/mnt/data'
ANNOTATIONS_MOUNT_PATH = '/mnt/annotations'

T = TypeVar("T", Example, ExampleResult)


def read_slingshot_examples(path: str) -> list[str]:
    """Read examples from a file as a list of raw JSON strings."""
    if not os.path.exists(path):
        return []

    examples = []
    with open(path, 'r') as f:
        for line in f:
            if not (line := line.strip()):
                examples.append(line)
    return examples


def import_label_studio_tasks(
    ls_client: label_studio_sdk.Client, examples: list[Example], annotations: list[ExampleResult]
) -> None:
    """Import examples to Label Studio as tasks."""
    tasks = []

    print(f"Importing {len(examples)} examples as tasks")
    for example in examples:
        data = example.data
        if isinstance(data, BaseModel):
            data = data.model_dump()
        tasks.append({"data": data})

    project = ls_client.get_project(id=1)
    task_ids: list[int] = project.import_tasks(tasks=tasks)

    print(f"Importing {len(annotations)} existing annotations")
    example_ids_to_task_id = {example.example_id: task_id for example, task_id in zip(examples, task_ids)}
    for annotation in annotations:
        task_id = example_ids_to_task_id[annotation.example_id]
        project.create_annotation(task_id=task_id, result=annotation.result.model_dump())


def main():
    """
    Import the dataset from the mounted path to Label Studio.

    NOTE: To change your import schema, edit the models defined in 'label_studio_data_type.py'.
    """
    assert "LABEL_STUDIO_API_KEY" in os.environ, "Please create a Slingshot Secret for 'LABEL_STUDIO_API_KEY'"
    assert "LABEL_STUDIO_URL" in os.environ, "Please create a Slingshot Secret for 'LABEL_STUDIO_URL'"

    # Load all examples and annotations from the mounted paths
    example_json_strings = read_slingshot_examples(os.path.join(DATASET_MOUNT_PATH, 'dataset.jsonl'))
    annotation_json_strings = read_slingshot_examples(os.path.join(ANNOTATIONS_MOUNT_PATH, 'annotations.jsonl'))

    examples = [Example.model_validate_json(example) for example in example_json_strings]
    annotations = [ExampleResult.model_validate_json(annotation) for annotation in annotation_json_strings]

    ls_client = label_studio_sdk.Client(api_key=os.environ["LABEL_STUDIO_API_KEY"], url=os.environ["LABEL_STUDIO_URL"])
    import_label_studio_tasks(ls_client, examples, annotations)


if __name__ == "__main__":
    main()
