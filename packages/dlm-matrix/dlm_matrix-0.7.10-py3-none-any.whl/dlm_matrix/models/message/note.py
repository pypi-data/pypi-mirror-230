from typing import Optional, List
from pydantic import BaseModel, Field


class Folder(BaseModel):
    id: int = Field(..., description="The unique ID of the folder.")
    long_id: str = Field(..., description="The long ID of the folder.")
    name: str = Field(..., description="The name of the folder.")
    parent: Optional[int] = Field(
        None, description="The ID of the parent folder, if any."
    )


class Note(BaseModel):
    id: str = Field(..., description="The unique ID of the note.")
    created: str = Field(..., description="The creation timestamp of the note.")
    updated: str = Field(..., description="The last updated timestamp of the note.")
    folder: Optional[int] = Field(
        None, description="The ID of the folder associated with the note, if any."
    )
    title: str = Field(..., description="The title of the note.")
    body: str = Field(..., description="The content of the note.")


class Annotations(BaseModel):
    folders: List[Folder]
    notes: List[Note]

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "folders": [
                    {
                        "id": 1,
                        "long_id": "folder_1",
                        "name": "Folder 1",
                        "parent": None,
                    },
                    {
                        "id": 2,
                        "long_id": "folder_2",
                        "name": "Folder 2",
                        "parent": None,
                    },
                ],
                "notes": [
                    {
                        "id": "note_1",
                        "created": "2023-07-29T17:35:32",
                        "updated": "2023-07-29T17:35:33",
                        "folder": 1,
                        "title": "Note 1",
                        "body": "This is the content of Note 1.",
                    },
                    {
                        "id": "note_2",
                        "created": "2023-07-30T09:12:45",
                        "updated": "2023-07-30T09:12:48",
                        "folder": 1,
                        "title": "Note 2",
                        "body": "This is the content of Note 2.",
                    },
                ],
            }
        }
