from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, Any


class DocumentEmbeddings(BaseModel):
    message_id: Optional[str] = Field(
        None, description="The unique identifier of the message."
    )

    umap_embeddings: Optional[Any] = Field(
        default=None,
        description="UMAP embeddings of the document for visualization or dimension reduction.",
    )
    embedding: Optional[Any] = Field(
        default=None, description="Embedding of the document for similarity search."
    )
    cluster_label: Optional[int] = Field(
        default=None,
        description="Cluster label for cluster-based analysis or navigation.",
    )
    n_neighbors: Optional[int] = Field(
        default=None, description="Number of nearest neighbors for graph construction."
    )
