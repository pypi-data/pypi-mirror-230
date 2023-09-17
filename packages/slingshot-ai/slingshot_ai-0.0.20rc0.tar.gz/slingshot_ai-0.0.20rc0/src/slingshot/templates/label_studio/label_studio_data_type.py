from typing import Literal

from pydantic import BaseModel, field_validator

from slingshot.schemas import LabelStudioFileURL, LabelStudioText

# Define your data type here. Refer to label studio documentation to see how to define your data type
# https://labelstud.io/guide/tasks#Basic-Label-Studio-JSON-format


class LabelStudioImportFields(BaseModel, arbitrary_types_allowed=True):
    # These are the fields that will be accessible to read data in your Label Config XML
    description: LabelStudioText
    image: LabelStudioFileURL

    @field_validator("description", mode="before")
    def validate_text(cls, v):
        return LabelStudioText(v)

    @field_validator("image", mode="before")
    def validate_video_path(cls, v):
        return LabelStudioFileURL(v)


class LabelStudioExportFields(BaseModel):
    # These are the fields label studio will write to, according to your label config XML
    classification: Literal["match", "no_match"]
