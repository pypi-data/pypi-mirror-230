from typing import List, Tuple, Dict, Any, Union, Optional
from sentence_transformers import SentenceTransformer
from dlm_matrix.transformation import Coordinate
from dlm_matrix.embedding.semantic import SemanticSimilarity
from dlm_matrix.embedding.utils import (
    apply_umap,
    apply_hdbscan,
)
from dlm_matrix.embedding.helper import (
    process_message_dict,
    generate_message_to_embedding_dict,
    compute_neighbors,
    update_message_dict_with_embeddings,
    get_text_chunks,
)
import numpy as np
import pandas as pd


class SpatialSimilarity:
    def __init__(
        self,
        reduce_dimensions=True,
        batch_size=128,
        n_components=3,
        weights=None,
        model_name="all-mpnet-base-v2",
        api_key: str = None,
    ):
        if api_key:
            self.semantic_similarity = SemanticSimilarity(
                api_key=api_key, batch_size=batch_size
            )

        """Initialize a SemanticSimilarity."""
        self.api_key = api_key
        self._model_name = model_name
        self.weights = weights if weights is not None else {}
        self._model = SentenceTransformer(self._model_name)  # Initialize model here
        self.default_options = {
            "n_components": n_components,
            "reduce_dimensions": reduce_dimensions,
            "n_neighbors": None,
        }
        self.batch_size = batch_size
        self._semantic_vectors = []
        self.keywords = []

    def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of texts as a list of lists of floats using the SentenceTransformer.
        """
        # Preprocess the texts
        self._model.max_seq_length = 512

        # Get embeddings for preprocessed texts
        embeddings = self._model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        return embeddings

    def generate_embeddings(
        self,
        message_dict: Dict[str, Any],
        n_chunks: Optional[int] = None,
        chunk_token_size: Optional[int] = None,
        use_advanced_tokenization: bool = True,
    ) -> Dict[str, np.array]:
        """
        Generate basic semantic embeddings for the messages.
        """
        # Extract the message text and ID from the message dictionary
        message_texts, message_ids = process_message_dict(message_dict)

        # Split the message_texts into chunks
        message_texts_chunks = [
            get_text_chunks(
                text,
                n_chunks=n_chunks,
                chunk_token_size=chunk_token_size,
                use_advanced_tokenization=use_advanced_tokenization,
            )
            for text in message_texts
        ]

        # Flatten the list of lists into a single list
        message_texts_flattened = [
            chunk for chunks in message_texts_chunks for chunk in chunks
        ]

        if self.api_key:
            # Encode the message texts to obtain their embeddings
            embeddings = self.semantic_similarity._embed_text_batch(
                message_texts_flattened
            )
        else:
            embeddings = self.encode_texts(message_texts_flattened)

        # Create a dictionary mapping message IDs to embeddings
        message_embeddings = generate_message_to_embedding_dict(message_ids, embeddings)

        # Update the message dictionary with the embeddings
        update_message_dict_with_embeddings(message_dict, message_embeddings)

        return embeddings, message_ids, message_embeddings  # Corrected return statement

    def generate_message_embeddings(
        self,
        grid,
        message_dict: Dict[str, Any],
        embeddings: Dict[str, np.array],
        message_ids: List[str],
        message_embeddings: Dict[str, np.array],
        options: dict = None,
    ) -> Dict[str, Union[np.array, Tuple[str, str]]]:
        """
        Generate semantic embeddings for the messages in the conversation tree using a sentence transformer.
        """

        # Update default options with user-specified options
        if options is not None:
            self.default_options.update(options)

        if len(message_dict) > 1:
            n_neighbors_dict = compute_neighbors(grid, message_dict)
            self.default_options["n_neighbors"] = np.mean(
                list(n_neighbors_dict.values())
            )
            reduced_embeddings = self.generate_reduced_embeddings(
                embeddings, self.default_options
            )

            message_embeddings = generate_message_to_embedding_dict(
                message_ids, reduced_embeddings
            )
            clusters = self.cluster_terms(list(message_embeddings.items()))

            # Assign each message id to a cluster label
            clustered_messages = {}
            for cluster_label, terms in clusters.items():
                for term in terms:
                    # Assuming term is a tuple with more than 2 elements, we only take the first one
                    term_id = term[0]
                    clustered_messages[term_id] = (
                        message_embeddings[term_id],
                        cluster_label,
                        embeddings,
                        n_neighbors_dict[
                            term_id
                        ],  # Add the count of neighbors to the dictionary
                    )

            return clustered_messages

    def generate_reduced_embeddings(
        self, embeddings: np.ndarray, options: dict = None
    ) -> np.ndarray:
        """
        Reduce the dimensionality of the embeddings if necessary.
        """
        # convert embeddings dictionary to numpy array
        if isinstance(embeddings, dict):
            embeddings = np.array(list(embeddings.values()))

        # Update default options with user-specified options
        if options is not None:
            self.default_options.update(options)

        if self.default_options["reduce_dimensions"]:
            embeddings = apply_umap(
                embeddings,
                self.default_options["n_neighbors"],
                self.default_options["n_components"],
            )

        return embeddings

    def cluster_terms(
        self, terms: List[Tuple[str, List[float]]]
    ) -> Dict[int, List[Tuple[str, List[float]]]]:
        try:
            if not terms:
                print("No terms provided for grouping")
                return {}

            # Extract the embeddings from the terms
            embeddings = np.array([embedding for _, embedding in terms])

            # Cluster the embeddings
            labels = apply_hdbscan(embeddings)

            # Create a dictionary mapping cluster labels to terms

            clusters = {}
            for i, label in enumerate(labels.labels_):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(terms[i])

            return clusters
        except Exception as e:
            print(f"Failed to cluster terms: {e}")
            return {}

    def get_global_embedding(
        self, main_df: pd.DataFrame, use_embeddings: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, pd.DataFrame]]:
        if use_embeddings:
            # Explicitly convert to a numpy array with a predefined shape, e.g., (-1, <embedding_dim>)
            embeddings = np.array(main_df["embedding"].tolist())
            return embeddings
        else:
            embeddings = self.encode_texts(main_df["text"].tolist())

            # Explicitly convert to a numpy array with a predefined shape, e.g., (-1, <embedding_dim>)
            embeddings = np.array(embeddings)
            return embeddings

    def create_umap_embeddings(
        self, global_embedding: List, mean_n_neighbors: int, n_components: int = 3
    ) -> List:
        return apply_umap(global_embedding, mean_n_neighbors, n_components).tolist()

    def _apply_clustering_common(
        self,
        main_df: pd.DataFrame,
        umap_embeddings: List,
        global_embedding,
        keep_old_columns: bool = False,
    ) -> pd.DataFrame:
        umap_array = np.array(umap_embeddings)

        coord_names = Coordinate.get_coordinate_names()
        main_df[coord_names] = main_df["coordinate"].apply(pd.Series)

        # Store UMAP embeddings and cluster labels in main_df
        main_df["umap_embeddings"] = umap_embeddings
        main_df["x"] = umap_array[:, 0]
        main_df["y"] = umap_array[:, 1]
        main_df["z"] = umap_array[:, 2]

        labels = apply_hdbscan(global_embedding)
        labels = labels.labels_

        # Add cluster labels to main_df
        main_df["cluster_label"] = labels

        # Determine the correct id column: either "doc_id" or "message_id"
        id_column = "doc_id" if "doc_id" in main_df.columns else "id"

        # Update the DataFrame directly with the id_column
        main_df[id_column] = main_df[id_column]

        if not keep_old_columns:
            main_df.drop(["coordinate", "umap_embeddings"], axis=1, inplace=True)

        return main_df

    def compute_message_embeddings(
        self,
        neighbors,
        main_df: pd.DataFrame,
        use_embeddings: bool = True,
    ) -> None:
        global_embedding = self.get_global_embedding(main_df, use_embeddings)

        umap_embeddings = self.create_umap_embeddings(global_embedding, neighbors)
        result3d = self._apply_clustering_common(
            main_df, umap_embeddings, global_embedding
        )

        return result3d
