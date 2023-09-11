from typing import List, Tuple, Dict, Any, Callable, Optional
import numpy as np
import tiktoken
import os
import uuid
from dlm_matrix.models import Document, DocumentChunk, DocumentChunkMetadata
from dlm_matrix.embedding.base import get_embeddings

tokenizer = tiktoken.get_encoding(
    "cl100k_base"
)  # The encoding scheme to use for tokenization

# Constants
CHUNK_SIZE = 200  # The target size of each text chunk in tokens
MIN_CHUNK_SIZE_CHARS = 350  # The minimum size of each text chunk in characters
MIN_CHUNK_LENGTH_TO_EMBED = 5  # Discard chunks shorter than this
EMBEDDINGS_BATCH_SIZE = int(
    os.environ.get("OPENAI_EMBEDDING_BATCH_SIZE", 128)
)  # The number of embeddings to request at a time
MAX_NUM_CHUNKS = 10000  # The maximum number of chunks to generate from a text


def process_message_dict(message_dict: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Extract the message text and ID from the message dictionary.
    """
    message_texts = []
    message_ids = []
    for message_id, message in message_dict.items():
        if isinstance(message, str):
            message_texts.append(message)
            message_ids.append(message_id)
        elif message.message and message.message.author.role != "system":
            message_texts.append(message.message.content.parts[0])
            message_ids.append(message.id)
    return message_texts, message_ids


def generate_message_to_embedding_dict(
    message_ids: List[str], embeddings: List[np.array]
) -> Dict[str, np.array]:
    """
    Generate a dictionary mapping message IDs to embeddings.
    """
    return {message_ids[i]: embeddings[i] for i in range(len(message_ids))}


def compute_neighbors(estimator, message_dict: Dict[str, Any]) -> Dict[str, int]:
    """
    For each message, determine the number of neighbors.
    """
    n_neighbors_dict = {}
    for message_id in message_dict:
        n_neighbors_dict[message_id] = estimator.determine_n_neighbors(message_id)
    return n_neighbors_dict


def update_message_dict_with_embeddings(
    message_dict: Dict[str, Any],
    embeddings: Any,
) -> None:
    """
    Update the 'embedding' or 'umap_embedding' fields of each Message object
    in the provided message_dict based on the embedding_type.

    Parameters:
        message_dict: A dictionary containing Message objects.
        embeddings: A dictionary mapping message IDs to their embeddings.

    Returns:
        None
    """
    for message_id, embedding in embeddings.items():
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()

        if message_id in message_dict:
            message_dict[message_id].message.embedding = embedding
        else:
            raise ValueError(
                f"Message ID {message_id} not found in message_dict. "
                f"Please check that the message_dict contains the correct message IDs."
            )


def generate_reduced_embeddings(
    embeddings: Dict[str, np.array], options: dict, umap_embed: Callable
) -> Dict[str, np.array]:
    """
    Generate reduced embeddings for the messages in the conversation tree using UMAP.
    """
    # Extract the embeddings and message IDs from the message dictionary
    message_ids = list(embeddings.keys())
    embeddings = list(embeddings.values())

    # Generate the reduced embeddings
    reduced_embeddings = umap_embed(embeddings, options)

    # Create a dictionary mapping message IDs to reduced embeddings
    message_embeddings = generate_message_to_embedding_dict(
        message_ids, reduced_embeddings
    )
    return message_embeddings


def get_text_chunks(
    text: str,
    n_chunks: Optional[int] = None,
    chunk_token_size: Optional[int] = None,
    use_advanced_tokenization: bool = True,
    split_by_line: bool = False,
) -> List[str]:
    """
    Splits the text into chunks, either by simple splitting or tokenization.

    Args:
        text: The text to split into chunks.
        n_chunks: The number of chunks to split the text into (used only if use_advanced_tokenization is False).
        chunk_token_size: The target size of each chunk in tokens (used only if use_advanced_tokenization is True).
        use_advanced_tokenization: Whether to use advanced tokenization or simple splitting.
        split_by_line: Whether to split by line if the number of paragraphs is less than n_chunks.

    Returns:
        A list of text chunks.
    """

    if not use_advanced_tokenization:
        text_chunks = text.split("\n\n")

        if split_by_line:
            if n_chunks is not None and len(text_chunks) < n_chunks:
                text_chunks = text.split("\n")
        else:
            if n_chunks is not None:
                text_chunks = text_chunks[:n_chunks]

        return text_chunks

    else:
        # Perform advanced tokenization
        if not text or text.isspace():
            return []

        tokens = tokenizer.encode(text, disallowed_special=())
        chunks = []
        chunk_size = chunk_token_size or CHUNK_SIZE
        num_chunks = 0

        while tokens and num_chunks < MAX_NUM_CHUNKS:
            chunk = tokens[:chunk_size]
            chunk_text = tokenizer.decode(chunk)

            if not chunk_text or chunk_text.isspace():
                tokens = tokens[len(chunk) :]
                continue

            last_punctuation = max(
                chunk_text.rfind("."),
                chunk_text.rfind("?"),
                chunk_text.rfind("!"),
                chunk_text.rfind("\n"),
            )

            if last_punctuation != -1 and last_punctuation > MIN_CHUNK_SIZE_CHARS:
                chunk_text = chunk_text[: last_punctuation + 1]

            chunk_text_to_append = chunk_text.replace("\n", " ").strip()

            if len(chunk_text_to_append) > MIN_CHUNK_LENGTH_TO_EMBED:
                chunks.append(chunk_text_to_append)

            tokens = tokens[len(tokenizer.encode(chunk_text, disallowed_special=())) :]

            num_chunks += 1

        if tokens:
            remaining_text = tokenizer.decode(tokens).replace("\n", " ").strip()
            if len(remaining_text) > MIN_CHUNK_LENGTH_TO_EMBED:
                chunks.append(remaining_text)

        return chunks


def create_document_chunks(
    doc: Document, chunk_token_size: Optional[int]
) -> Tuple[List[DocumentChunk], str]:
    """
    Create a list of document chunks from a document object and return the document id.

    Args:
        doc: The document object to create chunks from. It should have a text attribute and optionally an id and a metadata attribute.
        chunk_token_size: The target size of each chunk in tokens, or None to use the default CHUNK_SIZE.

    Returns:
        A tuple of (doc_chunks, doc_id), where doc_chunks is a list of document chunks, each of which is a DocumentChunk object with an id, a document_id, a text, and a metadata attribute,
        and doc_id is the id of the document object, generated if not provided. The id of each chunk is generated from the document id and a sequential number, and the metadata is copied from the document object.
    """
    # Check if the document text is empty or whitespace
    if not doc.text or doc.text.isspace():
        return [], doc.id or str(uuid.uuid4())

    # Generate a document id if not provided
    doc_id = doc.id or str(uuid.uuid4())

    # Split the document text into chunks
    text_chunks = get_text_chunks(doc.text, chunk_token_size)

    metadata = (
        DocumentChunkMetadata(**doc.metadata.__dict__)
        if doc.metadata is not None
        else DocumentChunkMetadata()
    )

    metadata.document_id = doc_id

    # Initialize an empty list of chunks for this document
    doc_chunks = []

    # Assign each chunk a sequential number and create a DocumentChunk object
    for i, text_chunk in enumerate(text_chunks):
        chunk_id = f"{doc_id}_{i}"
        doc_chunk = DocumentChunk(
            id=chunk_id,
            text=text_chunk,
            metadata=metadata,
        )
        # Append the chunk object to the list of chunks for this document
        doc_chunks.append(doc_chunk)

    # Return the list of chunks and the document id
    return doc_chunks, doc_id


def get_document_chunks(
    documents: List[Document], chunk_token_size: Optional[int]
) -> Dict[str, List[DocumentChunk]]:
    """
    Convert a list of documents into a dictionary from document id to list of document chunks.

    Args:
        documents: The list of documents to convert.
        chunk_token_size: The target size of each chunk in tokens, or None to use the default CHUNK_SIZE.

    Returns:
        A dictionary mapping each document id to a list of document chunks, each of which is a DocumentChunk object
        with text, metadata, and embedding attributes.
    """
    # Initialize an empty dictionary of lists of chunks
    chunks: Dict[str, List[DocumentChunk]] = {}

    # Initialize an empty list of all chunks
    all_chunks: List[DocumentChunk] = []

    # Loop over each document and create chunks
    for doc in documents:
        doc_chunks, doc_id = create_document_chunks(doc, chunk_token_size)

        # Append the chunks for this document to the list of all chunks
        all_chunks.extend(doc_chunks)

        # Add the list of chunks for this document to the dictionary with the document id as the key
        chunks[doc_id] = doc_chunks

    # Check if there are no chunks
    if not all_chunks:
        return {}

    # Get all the embeddings for the document chunks in batches, using get_embeddings
    embeddings: List[List[float]] = []
    for i in range(0, len(all_chunks), EMBEDDINGS_BATCH_SIZE):
        # Get the text of the chunks in the current batch
        batch_texts = [
            chunk.text for chunk in all_chunks[i : i + EMBEDDINGS_BATCH_SIZE]
        ]

        # Get the embeddings for the batch texts
        batch_embeddings = get_embeddings(batch_texts)

        # Append the batch embeddings to the embeddings list
        embeddings.extend(batch_embeddings)

    # Update the document chunk objects with the embeddings
    for i, chunk in enumerate(all_chunks):
        # Assign the embedding from the embeddings list to the chunk object
        chunk.embedding = embeddings[i]

    return chunks
