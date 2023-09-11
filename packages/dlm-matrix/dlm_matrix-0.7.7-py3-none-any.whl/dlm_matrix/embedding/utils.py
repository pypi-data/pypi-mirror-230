from typing import List, Tuple, Optional, Any, Dict, Union
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from hdbscan import HDBSCAN
from scipy.spatial.distance import cosine
from dlm_matrix.utils import log_handler
from sklearn.preprocessing import normalize
import os
import warnings
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

os.environ["TOKENIZERS_PARALLELISM"] = "false"

with warnings.catch_warnings():
    from numba.core.errors import NumbaWarning

    warnings.simplefilter("ignore", category=NumbaWarning)
    from umap import UMAP


def apply_umap(
    combined_features: np.ndarray,
    n_neighbors: int,
    n_components: int,
):
    # Check if n_neighbors is larger than the dataset size
    if n_neighbors > len(combined_features):
        # You can either set n_neighbors to the dataset size or another sensible value
        n_neighbors = len(combined_features)
        # You might want to log or print a warning here
        print(
            f"Warning: n_neighbors was larger than the dataset size; truncating to {n_neighbors}"
        )

    umap_embedding = UMAP(
        n_neighbors=int(n_neighbors),
        n_components=n_components,
        n_epochs=6000,
        min_dist=1,
        low_memory=False,
        learning_rate=0.5,
        verbose=True,
        metric="cosine",
    ).fit_transform(combined_features)

    return umap_embedding


def apply_hdbscan(
    embeddings: np.ndarray,
    min_samples: int = 5,
    cluster_selection_epsilon: float = 0.1,
    min_cluster_size: int = 20,
):
    cluster = HDBSCAN(
        metric="euclidean",
        min_samples=min_samples,
        min_cluster_size=min_cluster_size,
        core_dist_n_jobs=1,
        cluster_selection_epsilon=cluster_selection_epsilon,
        cluster_selection_method="leaf",
        leaf_size=40,
        algorithm="best",
    ).fit(embeddings)

    return cluster


def apply_hdbscan_umap(
    combined_features: np.ndarray,
    n_neighbors: int,
    n_components: int,
    min_samples: int = 5,
    cluster_selection_epsilon: float = 0.1,
    min_cluster_size: int = 70,
):
    umap_embedding = apply_umap(
        combined_features=combined_features,
        n_neighbors=n_neighbors,
        n_components=n_components,
    )

    cluster = apply_hdbscan(
        embeddings=umap_embedding,
        min_samples=min_samples,
        cluster_selection_epsilon=cluster_selection_epsilon,
        min_cluster_size=min_cluster_size,
    )

    return cluster


def calculate_similarity(embeddings1: List[float], embeddings2: List[float]) -> float:
    """
    Calculate semantic similarity between two sets of embeddings using cosine similarity.

    Args:
        embeddings1 (List[float]): Embeddings of the first message.
        embeddings2 (List[float]): Embeddings of the second message.

    Returns:
        float: Semantic similarity score between the two sets of embeddings.
    """
    # Convert the embeddings lists to numpy arrays
    embeddings1_array = np.array(embeddings1).reshape(1, -1)
    embeddings2_array = np.array(embeddings2).reshape(1, -1)

    # Calculate cosine similarity between the embeddings
    similarity_matrix = cosine_similarity(embeddings1_array, embeddings2_array)

    # The similarity score is the value in the similarity matrix
    similarity_score = similarity_matrix[0][0]

    return similarity_score


def compute_similar_keywords_global(
    keywords: List[str],
    embeddings: List[List[float]],
    use_argmax: bool,
    num_keywords: int,
) -> List[Tuple[str, float]]:
    """
    Compute similarity scores for keywords against a global embedding.

    Args:
        keywords (List[str]): List of keywords to compute similarity for.
        embeddings (List[List[float]]): List of embeddings for the keywords.
        use_argmax (bool): Whether to use argmax for similarity scores.
        num_keywords (int): Number of similar keywords to return.

    Returns:
        List[Tuple[str, float]]: List of tuples containing keyword and similarity score.
    """
    similarity_scores = cosine_similarity(embeddings, embeddings)
    similarity_scores = np.triu(similarity_scores, k=1)
    similarity_scores = similarity_scores.flatten()
    similarity_scores = similarity_scores[similarity_scores != 0]
    similarity_scores = np.sort(similarity_scores)[::-1]

    if use_argmax:
        similarity_scores = similarity_scores[:num_keywords]
    else:
        similarity_scores = similarity_scores[: num_keywords * len(keywords)]

    similarity_scores = similarity_scores.reshape(len(keywords), num_keywords)

    similar_keywords = []

    for i, keyword in enumerate(keywords):
        keyword_scores = similarity_scores[i]
        similar_keywords.append(
            [keywords[j] for j in np.argsort(keyword_scores)[::-1][:num_keywords]]
        )

    return similar_keywords


def compute_similar_keywords_query(
    keywords: List[str],
    query_vector: List[float],
    use_argmax: bool,
    query: str,
    model=None,
) -> List[Tuple[str, float]]:
    """
    Compute similarity scores for keywords against a query vector.

    Args:
        keywords (List[str]): List of keywords to compute similarity for.
        query_vector (List[float]): Vector representing the query.
        use_argmax (bool): Whether to use argmax for similarity scores.

    Returns:
        List[Tuple[str, float]]: List of tuples containing keyword and similarity score.
    """
    # Remove the query keyword from the list of keywords
    keywords = [
        keyword.strip()
        for keyword in keywords
        if keyword.strip().lower() != query.strip().lower()
    ]

    similarity_scores = []

    for keyword in keywords:
        keyword_vector = model.encode(keyword)
        similarity = cosine_similarity([query_vector], [keyword_vector])[0][0]
        similarity_scores.append((keyword, similarity))

    if use_argmax:
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        similarity_scores = similarity_scores[:1]
    else:
        similarity_scores = sorted(similarity_scores, key=lambda x: x[0])

    return similarity_scores


def compute_similar_keywords_per_keyword(
    keywords: List[str], embeddings: List[List[float]], num_keywords: int
) -> List[List[str]]:
    similarity_scores_list = [
        cosine_similarity([vector], embeddings)[0] for vector in embeddings
    ]
    similar_keywords_list = [
        [keywords[i] for i in np.argsort(similarity_scores)[::-1][:num_keywords]]
        for similarity_scores in similarity_scores_list
    ]

    return similar_keywords_list


def semantic_search(
    query: Union[str, None],
    corpus: Union[List[str], np.ndarray, None],
    num_results: int = 10,
    model=None,
    verbose: bool = False,
) -> List[Tuple[Union[str, None], float]]:
    """
    Perform semantic search against a corpus of text using the query keyword.

    Args:
        query (Union[str, None]): Query keyword.
        corpus (Union[List[str], None]): List of text documents to search against.
        num_results (int, optional): Number of search results to return. Defaults to 10.
        verbose (bool, optional): Whether to log verbose messages. Defaults to False.

    Returns:
        List[Tuple[Union[str, None], float]]: List of tuples containing search results and their similarity scores.
    """

    if model is None:
        model = SentenceTransformer("all-mpnet-base-v2")

    if query is None:
        query = []

    if corpus is None:
        corpus = []

    if verbose:
        log_handler("Performing semantic search.", level="info")

    query_vector = np.array(model.fit([query])[0]).flatten() if query else np.array([])
    corpus_vectors = np.array(model.fit(corpus)) if corpus else np.array([])

    if verbose:
        log_handler(
            "Computing cosine similarity between the query and corpus.", level="info"
        )

    query_dim = query_vector.shape[0]
    corpus_dim = corpus_vectors.shape[1] if corpus_vectors.ndim == 2 else 0

    max_dim = max(query_dim, corpus_dim)

    if query_dim < max_dim:
        query_vector = np.pad(query_vector, (0, max_dim - query_dim), "constant")

    if corpus_dim < max_dim:
        pad_width = (
            ((0, 0), (0, max_dim - corpus_dim))
            if corpus_vectors.ndim == 2
            else (0, max_dim)
        )
        corpus_vectors = np.pad(corpus_vectors, pad_width, "constant")

    if verbose:
        log_handler(
            "Computing cosine similarity between the query and corpus.", level="info"
        )

    query_vector = normalize(query_vector[:, np.newaxis], axis=0).ravel()
    corpus_vectors = normalize(corpus_vectors, axis=1)

    if verbose:
        log_handler(
            "Computing cosine similarity between the query and corpus.", level="info"
        )

    similarity_scores = (
        cosine_similarity([query_vector], corpus_vectors)[0] if corpus else []
    )
    results_with_scores = [
        (corpus[i], score) for i, score in enumerate(similarity_scores)
    ]
    sorted_results = sorted(results_with_scores, key=lambda x: x[1], reverse=True)

    return sorted_results[:num_results]


def group_terms(
    terms: List[Tuple[str, List[float]]], use_argmax: bool = True
) -> Dict[Tuple[int], List[Tuple[str, List[float]]]]:
    """
    Group a list of terms by their semantic similarity using a specified language model.
    If 'use_argmax' is True, return the most similar term for each term in 'terms'.
    If 'use_argmax' is False, return the most similar terms for each term in 'terms'.
    """
    try:
        # Compute similarity scores
        similarities = cosine_similarity(
            [vector for _, vector in terms], [vector for _, vector in terms]
        )
        similarity_scores = np.argsort(similarities, axis=1)

        # Group terms
        clusters = {}
        for i, term in enumerate(terms):
            if use_argmax:
                cluster_id = tuple([similarity_scores[i][-2]])
            else:
                cluster_id = tuple(similarity_scores[i][-2:-11:-1])
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(term)

        return clusters

    except ValueError as e:
        log_handler(message=f"Error in group_terms: {e}", level="error")
        return {}


def normalize_scores(scores: List[float]) -> List[float]:
    """
    Normalize a list of scores to the range [0, 1].

    Args:
        scores (List[float]): A list of scores to normalize.

    Returns:
        List[float]: A list of normalized scores.
    """
    scores = np.array(scores)

    # Handle empty scores
    if scores.size == 0:
        return []

    # Calculate min and max scores
    min_score, max_score = np.min(scores), np.max(scores)

    # Check for division by zero
    if max_score == min_score:
        return [1.0] * len(scores)  # All scores are the same, normalize to 1

    # Perform normalization
    normalized_scores = (scores - min_score) / (max_score - min_score)

    return list(normalized_scores)


def should_connect_semantic(
    node1: Tuple[Any, ...], node2: Tuple[Any, ...], model
) -> bool:
    sentence1 = node1[0]
    sentence2 = node2[0]
    cosine_similarity_threshold = 0.8

    cosine_sim = semantic_similarity_cosine(sentence1, sentence2, model)

    if cosine_sim > cosine_similarity_threshold:
        return True
    else:
        return False


def semantic_similarity_cosine(
    sentence1: str,
    sentence2: str,
    model: Optional[nn.Module] = None,
    tokenizer: Optional[Any] = None,
    return_adjusted_cosine_sim: bool = True,
) -> Union[float, Tuple[float, float]]:
    if not torch:
        raise ImportError("PyTorch is not available. Please install it to proceed.")

    if model is None:
        model = SentenceTransformer("all-mpnet-base-v2")

    try:
        if tokenizer:
            input1 = tokenizer(
                sentence1, return_tensors="pt", truncation=True, max_length=512
            )
            input2 = tokenizer(
                sentence2, return_tensors="pt", truncation=True, max_length=512
            )
            embedding1 = model(**input1).last_hidden_state.mean(dim=1)
            embedding2 = model(**input2).last_hidden_state.mean(dim=1)
        else:
            embedding1 = model.encode(
                sentence1,
                convert_to_tensor=True,
                show_progress_bar=False,
            )
            embedding2 = model.encode(
                sentence2,
                convert_to_tensor=True,
                show_progress_bar=False,
            )
    except Exception as e:
        raise RuntimeError(f"Error during encoding: {e}")

    prob_dist1 = F.softmax(embedding1, dim=0)
    prob_dist2 = F.softmax(embedding2, dim=0)

    cross_entropy_loss = F.kl_div(
        F.log_softmax(prob_dist1, dim=0), prob_dist2, reduction="sum"
    ).item()

    cosine_sim = 1 - cosine(
        embedding1.detach().cpu().numpy(), embedding2.detach().cpu().numpy()
    )
    cosine_sim = max(0, min(cosine_sim, 1))

    if return_adjusted_cosine_sim:
        adjusted_cosine_sim = cosine_sim / (1 + abs(cross_entropy_loss))
        return adjusted_cosine_sim

    return cross_entropy_loss, cosine_sim
