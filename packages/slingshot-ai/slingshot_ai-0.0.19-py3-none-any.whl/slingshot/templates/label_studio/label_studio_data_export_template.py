import os

import label_studio_sdk
from label_studio_data_type import LabelStudioExportFields, LabelStudioImportFields

from slingshot.schemas import ExampleResult, Result

ANNOTATIONS_MOUNT_PATH = '/mnt/annotations'


# This is an example annotation object from Label Studio where the task type is classification and
# the classification result is stored in the `classification` field. You should modify this class
# to match the annotation object that you are exporting from your own use case.
class LabelStudioResult(LabelStudioImportFields, LabelStudioExportFields):
    example_id: str
    annotator: int
    annotation_id: int
    created_at: str
    updated_at: str
    lead_time: float


def convert_label_studio_annotations_to_annotations(ls_annotations: list[LabelStudioResult]) -> list[ExampleResult]:
    """Convert Label Studio annotations to the Slingshot ExampleResult schema."""
    example_results: list[ExampleResult] = []
    for ls_annotation in ls_annotations:
        data = LabelStudioResult.model_validate(ls_annotation.model_dump())
        result = Result.model_validate(data)
        annotation = ExampleResult(exampleId=data.example_id, result=result)
        example_results.append(annotation)
    return example_results


def get_label_studio_annotations(ls_client: label_studio_sdk.Client) -> list[ExampleResult]:
    """Get all annotations from Label Studio and convert them to the Slingshot ExampleResult schema."""
    project = ls_client.get_project(id=1)

    # TODO: try using 'JSON' to get the full JSON object to avoid having to process fields manually
    res = project.export_tasks(export_type='JSON-MIN')
    ls_annotations = [LabelStudioResult.model_validate(annotation_obj) for annotation_obj in res]
    examples = convert_label_studio_annotations_to_annotations(ls_annotations)
    print(f"Found {len(examples)} annotated examples on Label Studio")
    return examples


def write_annotations_to_file(slingshot_annotations: list[ExampleResult], filename: str = 'annotations.jsonl') -> None:
    """Write annotations to annotations.jsonl file"""
    with open(os.path.join(ANNOTATIONS_MOUNT_PATH, filename), 'w') as f:
        for annotation in slingshot_annotations:
            f.write(str(annotation.model_dump()) + '\n')
    print(f"Saved all annotations to '{filename}'")


def main() -> None:
    """Export all annotations from Label Studio and write them to the annotations.jsonl file."""
    assert "LABEL_STUDIO_API_KEY" in os.environ, "Please create a Slingshot Secret for 'LABEL_STUDIO_API_KEY'"
    assert "LABEL_STUDIO_URL" in os.environ, "Please create a Slingshot Secret for 'LABEL_STUDIO_URL'"
    ls_client = label_studio_sdk.Client(api_key=os.environ['LABEL_STUDIO_API_KEY'], url=os.environ['LABEL_STUDIO_URL'])
    all_annotations = get_label_studio_annotations(ls_client)
    write_annotations_to_file(all_annotations)


if __name__ == "__main__":
    main()
