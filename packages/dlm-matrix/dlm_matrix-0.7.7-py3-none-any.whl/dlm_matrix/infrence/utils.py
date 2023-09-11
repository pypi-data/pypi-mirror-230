import time
import uuid
import json
import os
from typing import List, Optional
from dlm_matrix.models import (
    Chain,
    Content,
    Metadata,
)
from dlm_matrix.type import RoleType


def create_system_message() -> Chain:
    """
    Create a System message.

    Returns:
        Message: The System message object.
    """
    content_data = {
        "content_type": "text",
        "parts": [],
    }
    system = RoleType.SYSTEM
    return Chain(
        id=str(uuid.uuid4()),
        create_time=time.time(),
        content=Content(**content_data),
        author=system,
    )


def create_user_message(
    message_id: str,
    text: str,
    metadata: Optional[Metadata] = None,
    user_embeddings: List[float] = None,
) -> Chain:
    """
    Create a User message.

    Args:
        message_id (str): The unique identifier for the User message.
        text (str): The content of the User message.
        metadata (Optional[Metadata]): The metadata associated with the User message. Defaults to None.

    Returns:
        Message: The User message object.
    """
    content_data = {
        "content_type": "text",
        "parts": [text],
        "embedding": user_embeddings,
    }

    user = RoleType.USER
    return Chain(
        id=message_id,
        create_time=time.time(),
        content=Content(**content_data),
        author=user,
        metadata=metadata,
    )


def create_assistant_message(
    text: str, assistant_embeddings: List[float] = None
) -> Chain:
    """
    Create an Assistant message.

    Args:
        text (str): The generated content for the Assistant message.

    Returns:
        Message: The Assistant message object.
    """
    assistant = RoleType.ASSISTANT
    return Chain(
        id=str(uuid.uuid4()),
        create_time=time.time(),
        content=Content(
            content_type="text",
            parts=[text],
            embedding=assistant_embeddings,
        ),
        author=assistant,
        end_turn=True,
    )


def save_message_to_json(message_data, json_file_path: str):
    # Create the folder if it doesn't exist
    if not os.path.exists("message"):
        os.mkdir("message")

    # Construct the final path
    json_file_path = os.path.join("message", json_file_path)

    # Load existing messages if the file exists
    existing_messages = []
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            existing_messages = json.load(file)

    # Append new message data
    existing_messages.append(message_data)

    # Save all messages back to the file
    with open(json_file_path, "w") as file:
        json.dump(existing_messages, file, indent=4)
