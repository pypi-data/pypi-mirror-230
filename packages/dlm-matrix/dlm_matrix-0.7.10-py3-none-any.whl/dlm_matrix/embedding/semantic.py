from typing import List, Tuple, Optional, Union
from sklearn.metrics.pairwise import cosine_similarity
from dlm_matrix.embedding.utils import group_terms
from dlm_matrix.embedding.base import BaseEmbedding
import logging


class SemanticSimilarity(BaseEmbedding):
    """
    A class for computing semantic similarity between text queries and keywords.
    """

    def __init__(self, api_key: str = None, batch_size: int = 128):
        super().__init__(api_key=api_key, batch_size=batch_size)

    def compute_similarity_scores(
        self,
        query: Union[str, List[str]],
        keywords: List[str],
        batches: bool = False,
        top_k: int = None,
    ) -> Union[List[Tuple[str, float]], List[List[Tuple[str, float]]]]:
        """
        Compute similarity scores between a query and a list of keywords.

        Parameters:
            query (Union[str, List[str]]): The query or list of queries for which similarity scores need to be computed.
            keywords (List[str]): A list of keywords to compare similarity with the query.
            batches (bool, optional): A flag to specify if the function is being used in a batch processing context.
                Defaults to False.
            top_k (int, optional): The number of top similar keywords to return. If None, all will be returned.

        Returns:
            Union[List[Tuple[str, float]], List[List[Tuple[str, float]]]]: A list of tuples if single query, or a list of list of tuples if batch queries.
        """

        if batches:
            query_vectors = self._embed_text_batch(query)
            similarities = cosine_similarity(
                query_vectors, self._embed_keywords(keywords)
            )

            similarity_scores = []
            for sim_array in similarities:
                scores = [
                    (keyword, float(similarity))
                    for keyword, similarity in zip(keywords, sim_array)
                ]
                scores.sort(key=lambda x: x[1], reverse=True)
                if top_k is not None:
                    scores = scores[:top_k]

                similarity_scores.append(scores)

            return similarity_scores

        else:
            query_vector = self._create_embedding
            similarities = cosine_similarity(
                [query_vector], self._embed_keywords(keywords)
            )[0]

            similarity_scores = [
                (keyword, float(similarity))
                for keyword, similarity in zip(keywords, similarities)
            ]

            similarity_scores.sort(key=lambda x: x[1], reverse=True)

            if top_k is not None:
                similarity_scores = similarity_scores[:top_k]

            return similarity_scores

    def compute_similar_keywords(
        self,
        keywords: List[str],
        num_keywords: int = 10,
        top_k: int = 1,
        use_argmax: bool = False,
        per_keyword: bool = False,
        query: Optional[str] = None,
    ) -> List[str]:
        """
        Compute a list of similar keywords using a specified language model.

        Parameters:
            keywords (List[str]): A list of keywords for which similarity needs to be computed.
            num_keywords (int, optional): The maximum number of similar keywords to return. Defaults to 10.
            use_argmax (bool, optional): Determines the grouping approach. If True, uses argmax approach.
                If False, uses a broader approach selecting multiple similar keywords per group.
                Defaults to True.
            per_keyword (bool, optional): If True, returns a list of similar keywords for each keyword.
                If False, returns a flattened list of top similar keywords across all keywords.
                Defaults to True.
            query (str, optional): If provided, computes similarity scores between the query and each keyword.

        Returns:
            List[str]: A list of similar keywords or similarity scores, based on the provided parameters.

        Note:
            When `per_keyword` is True, the returned list of similar keywords will be in the format:
                - If query is None: [[sim_keyword_1, sim_keyword_2, ...], [sim_keyword_1, sim_keyword_2, ...], ...]
                - If query is provided: [(sim_keyword, similarity_score), ...]

            When `per_keyword` is False, the returned list will be a flattened list of top similar keywords.
        """
        try:
            # Compute semantic vectors
            semantic_vectors = self._compute_semantic_vectors(keywords)
            embeddings = self._embed_keywords(keywords)

            # Compute similarity scores
            if query is not None:
                similarity_scores = self.compute_similarity_scores(
                    query=query, keywords=keywords, top_k=top_k
                )

            # Compute similar keywords
            else:
                if per_keyword:
                    similarity_scores = [
                        [
                            keywords[i]
                            for i in similarity_scores.argsort()[::-1][:num_keywords]
                        ]
                        for _, similarity_scores in [
                            cosine_similarity([vector], embeddings)
                            for term, vector in semantic_vectors
                        ]
                    ]
                else:
                    clusters = group_terms(semantic_vectors, use_argmax=use_argmax)
                    sorted_clusters = sorted(clusters.values(), key=len, reverse=True)[
                        :num_keywords
                    ]
                    similarity_scores = [
                        term for cluster in sorted_clusters for term, _ in cluster
                    ]

            return similarity_scores

        except ValueError as e:
            logging.error(f"An error occurred while computing similar keywords: {e}")
            return []

    def predict_semantic_similarity(
        self, query: str, keywords: List[str], threshold: float = 0.5, top_k: int = None
    ) -> List[str]:
        """
        This method takes a single query and a list of keywords, and returns a list of keywords that are semantically similar
        to the query based on a given threshold. Essentially, it predicts which keywords are relevant to a given query
        by comparing their semantic meanings.

        Parameters:
        - query (str): A single text query for which we want to find semantically similar keywords.
        - keywords (List[str]): A list of keywords to compare with the query for semantic similarity.
        - threshold (float, optional): The threshold for semantic similarity score. Keywords that have a similarity score
        above or equal to this threshold are considered similar. Default is 0.5.

        Returns:
        - List[str]: A list containing keywords that are predicted to be semantically similar to the query.

        Exceptions:
        - Logs a ValueError and returns an empty list if an error occurs during processing.

        Example:
        >>> predict_semantic_similarity("apple", ["fruit", "company", "color"])
        ["fruit"]
        """
        try:
            # Compute similarity scores using the compute_similarity_scores method
            similarity_scores = self.compute_similarity_scores(
                query=query, keywords=keywords, top_k=top_k
            )
            # Create a list of predicted keywords based on the similarity threshold
            predicted_keywords = [
                keyword
                for keyword, similarity in similarity_scores
                if similarity >= threshold
            ]

            return predicted_keywords

        except ValueError as e:
            logging.error(
                f"An error occurred while predicting semantic similarity: {e}"
            )
            return []

    def predict_semantic_similarity_batch(
        self,
        queries: List[str],
        keywords: List[str],
        threshold: float = 0.5,
        top_k: int = None,
    ) -> List[List[str]]:
        """
        This method takes a list of queries and a list of keywords, and for each query, it returns a list of keywords
        that are semantically similar based on a given threshold.

        Parameters:
        - queries (List[str]): A list of text queries for which we want to find semantically similar keywords.
        - keywords (List[str]): A list of keywords to compare with each query for semantic similarity.
        - threshold (float, optional): The threshold for semantic similarity score. Keywords that have a similarity
          score above or equal to this threshold are considered similar. Default is 0.5.

        Returns:
        - List[List[str]]: A list of lists where each inner list contains keywords that are predicted to be semantically
          similar to the corresponding query in the 'queries' input list.

        Exceptions:
        - Logs a ValueError and returns an empty list if an error occurs during processing.

        Example:
        >>> predict_semantic_similarity_batch(["apple", "orange"], ["fruit", "company", "color"])
        [["fruit"], ["fruit", "color"]]

        """
        try:
            # Compute similarity scores using the modified compute_similarity_scores
            similarity_scores = self.compute_similarity_scores(
                query=queries, keywords=keywords, batches=True, top_k=top_k
            )

            # Create a list of predicted keywords for each query based on the similarity threshold
            predicted_keywords = [
                [
                    keyword
                    for keyword, similarity in similarity_score
                    if similarity >= threshold
                ]
                for similarity_score in similarity_scores
            ]

            return predicted_keywords

        except ValueError as e:
            logging.error(
                f"An error occurred while predicting semantic similarity: {e}"
            )
            return []

    def compute_semantic_similarity_batch(
        self, queries: List[str], keywords: List[str], top_k: int = None
    ) -> List[List[Tuple[str, float]]]:
        """
        This method takes a list of queries and a list of keywords, and computes the semantic similarity scores between
        each query and each keyword. The method returns these scores in a structured format.

        Parameters:
        - queries (List[str]): A list of text queries for which we want to compute semantic similarity scores with the keywords.
        - keywords (List[str]): A list of keywords to compare for semantic similarity with each query.

        Returns:
        - List[List[Tuple[str, float]]]: A list of lists where each inner list contains tuples. Each tuple contains a
          keyword and its corresponding semantic similarity score with the query.

        Example:
        >>> compute_semantic_similarity_batch(["apple", "orange"], ["fruit", "company", "color"])
        [[("fruit", 0.8), ("company", 0.2), ("color", 0.1)], [("fruit", 0.9), ("company", 0.1), ("color", 0.7)]]

        """
        try:
            # Compute similarity scores using the modified compute_similarity_scores
            similarity_scores = self.compute_similarity_scores(
                query=queries, keywords=keywords, batches=True, top_k=top_k
            )

            return similarity_scores

        except ValueError as e:
            logging.error(f"An error occurred while computing semantic similarity: {e}")
            return []

    def semantic_similarity_interface(
        self,
        query: Union[str, List[str]] = None,
        keywords: List[str] = None,
        top_k: int = 1,
        threshold: float = 0.5,
        num_keywords: int = 10,
        use_argmax: bool = False,
        per_keyword: bool = False,
    ) -> Union[List[str], List[List[str]], List[List[Tuple[str, float]]]]:
        """
        An interface for various semantic similarity methods.

        Parameters:
        - query (Union[str, List[str]]): A single query or a list of queries to compare with the keywords.
        - keywords (List[str]): A list of keywords to compare with the query/queries for similarity.
        - threshold (float, optional): The similarity threshold for predicting semantically similar keywords. Defaults to 0.5.
        - top_k (int, optional): The top K similarity scores to consider when predicting or computing. Defaults to 1.
        - num_keywords (int, optional): The maximum number of similar keywords to return when using the compute_similar_keywords method. Defaults to 10.
        - use_argmax (bool, optional): Determines the grouping approach for compute_similar_keywords. Defaults to False.
        - per_keyword (bool, optional): If True, returns a list of similar keywords for each keyword when using compute_similar_keywords. Defaults to False.

        Returns:
        - Union[List[str], List[List[str]], List[List[Tuple[str, float]]]]:
            - When predicting, returns a list of keywords similar to the query or a list of lists for each query when in batch mode.
            - When computing, returns a list of tuples where each tuple contains a keyword and its similarity score with the query.

        Example:
        - Single query, predicting similar keywords:
        >>> semantic_similarity_interface("apple", ["fruit", "company", "color"], threshold=0.5)
        ["fruit"]

        - Batch of queries, predicting similar keywords:
        >>> semantic_similarity_interface(["apple", "orange"], ["fruit", "company", "color"], threshold=0.5)
        [["fruit"], ["fruit"]]

        - Single query, computing similarity scores (assumes compute_similarity_scores function exists):
        >>> semantic_similarity_interface("apple", ["fruit", "company", "color"], threshold=0.5, top_k=2)
        [("fruit", 0.8), ("company", 0.2)]

        - Batch of queries, computing similarity scores (assumes compute_similarity_scores function exists):
        >>> semantic_similarity_interface(["apple", "orange"], ["fruit", "company", "color"], threshold=0.5, top_k=2)
        [[("fruit", 0.8), ("company", 0.2)], [("fruit", 0.9), ("color", 0.7)]]

        - Compute similar keywords based on given list of keywords (assumes compute_similar_keywords function exists):
        >>> semantic_similarity_interface(None, ["fruit", "company"], num_keywords=2, use_argmax=True, per_keyword=True)
        [["fruit", "company"], ["company", "fruit"]]

        """

        try:
            is_batch = isinstance(query, list)  # Determine if it's a batch operation

            # If keywords are provided, then compute semantic similarity, otherwise use compute_similar_keywords
            compute_similar_kw = bool(keywords)

            if is_batch:
                # Handle batch operations
                if compute_similar_kw:
                    return self.predict_semantic_similarity_batch(
                        query, keywords, threshold, top_k=top_k
                    )
                else:
                    # Batch operation using compute_similarity_scores
                    return self.compute_similarity_scores(
                        query, keywords, batches=True, top_k=top_k
                    )
            else:
                # Handle single query operations
                if compute_similar_kw:
                    if query:  # make sure query is not None or empty
                        return self.predict_semantic_similarity(
                            query, keywords, threshold, top_k=top_k
                        )
                    else:
                        # Here, query is None or empty, so we fall back to compute_similar_keywords
                        return self.compute_similar_keywords(
                            keywords,
                            num_keywords=num_keywords,
                            top_k=top_k,
                            use_argmax=use_argmax,
                            per_keyword=per_keyword,
                            query=query,
                        )
                elif (
                    num_keywords and use_argmax is not None and per_keyword is not None
                ):
                    # Single query using compute_similar_keywords
                    return self.compute_similar_keywords(
                        keywords,
                        num_keywords=num_keywords,
                        top_k=top_k,
                        use_argmax=use_argmax,
                        per_keyword=per_keyword,
                        query=query,
                    )
                else:
                    # Single query using compute_similarity_scores
                    return self.compute_similarity_scores(query, keywords, top_k=top_k)

        except ValueError as e:
            logging.error(f"An error occurred while computing semantic similarity: {e}")
            return []
