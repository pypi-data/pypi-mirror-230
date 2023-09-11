from typing import List, Tuple, Union, Dict, Optional, Callable
from dlm_matrix.services.utility.helper import DataHelper
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from collections import Counter
from dlm_matrix.embedding import SpatialSimilarity
from dlm_matrix.embedding.utils import (
    compute_similar_keywords_query,
    compute_similar_keywords_per_keyword,
    compute_similar_keywords_global,
)
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import pandas as pd
import numpy as np
import logging
import re
import ast


class DataRetriever:
    def __init__(self, data_helper: DataHelper):
        """Initializes the DataRetriever with a given DataHelper."""
        self.data = data_helper.finalize()
        self.prompt_col = data_helper.prompt_col
        self.response_col = data_helper.response_col
        self.model = SpatialSimilarity()
        self._validate_columns()

    def _validate_columns(self) -> None:
        """Validates if the specified columns exist in the dataset."""
        for col in [self.prompt_col, self.response_col]:
            if col not in self.data.columns:
                logging.error(f"Column '{col}' not found in data.")
                raise ValueError(f"Column '{col}' not found in data.")

    def _validate_pair_type(self, pair_type: str) -> None:
        """Validates if the provided pair_type is valid."""
        valid_pair_types = ["both", self.prompt_col, self.response_col]
        if pair_type not in valid_pair_types:
            logging.error(
                f"Invalid pair_type. Choose from {', '.join(valid_pair_types)}"
            )
            raise ValueError(
                f"Invalid pair_type. Choose from {', '.join(valid_pair_types)}"
            )

    def _get_data_by_pair_type(
        self, data_subset: pd.DataFrame, pair_type: str
    ) -> Union[List[str], List[Tuple[str, str]]]:
        """Returns data based on the pair_type from a given data subset."""
        self._validate_pair_type(pair_type)

        if pair_type == "both":
            return list(
                zip(
                    data_subset[self.prompt_col].tolist(),
                    data_subset[self.response_col].tolist(),
                )
            )
        return data_subset[pair_type].tolist()

    def get_examples(
        self, pair_type: str = "both"
    ) -> Union[List[str], List[Tuple[str, str]]]:
        """Gets examples of the specified type from the data."""
        return self._get_data_by_pair_type(self.data, pair_type)

    def get_random_examples(
        self, n: int, pair_type: str = "both"
    ) -> Union[List[str], List[Tuple[str, str]]]:
        """Gets n random examples of the specified type from the data."""
        return self._get_data_by_pair_type(self.data.sample(n), pair_type)

    def get_first_n_examples(
        self, n: int, pair_type: str = "both"
    ) -> Union[List[str], List[Tuple[str, str]]]:
        """Gets the first n examples of the specified type from the data."""
        return self._get_data_by_pair_type(self.data.head(n), pair_type)

    def search_examples(
        self, keywords: Union[str, List[str]], pair_type: str = "both"
    ) -> Union[List[str], List[Tuple[str, str]]]:
        """Searches examples containing the keyword(s) of the specified type from the data."""
        if isinstance(keywords, str):
            keywords = [keywords]

        mask = self.data[self.prompt_col].str.contains(
            "|".join(map(re.escape, keywords))
        ) | self.data[self.response_col].str.contains(
            "|".join(map(re.escape, keywords))
        )

        filtered_data = self.data[mask]
        return self._get_data_by_pair_type(filtered_data, pair_type)

    def count_keyword(
        self, keyword: str, pair_type: str = "both"
    ) -> Union[int, Dict[str, int]]:
        data = self.data  # We get the data directly from the DataHelper instance

        if pair_type == "both":
            return {
                "prompt": data[self.prompt_col]
                .apply(lambda x: x.lower().count(keyword.lower()))
                .sum(),
                "response": data[self.response_col]
                .apply(lambda x: x.lower().count(keyword.lower()))
                .sum(),
            }
        elif pair_type == self.prompt_col:
            return (
                data[self.prompt_col]
                .apply(lambda x: x.lower().count(keyword.lower()))
                .sum()
            )
        elif pair_type == self.response_col:
            return (
                data[self.response_col]
                .apply(lambda x: x.lower().count(keyword.lower()))
                .sum()
            )
        else:
            raise ValueError(
                f"Invalid pair_type. Choose from '{self.prompt_col}', '{self.response_col}', 'both'"
            )

    def create_prompt_matrix(self) -> csr_matrix:
        """Creates a sparse matrix of prompts"""
        vectorizer = TfidfVectorizer()
        return vectorizer.fit_transform(self.data[self.prompt_col].tolist())

    def filter_data(self, word: str, pair_type: str = None) -> List[str]:
        """Returns the data that contain a specific word"""
        if pair_type not in [self.prompt_col, self.response_col]:
            raise ValueError(
                f"Invalid pair_type. Choose from '{self.prompt_col}', '{self.response_col}'"
            )
        data_column = (
            self.prompt_col if pair_type == self.prompt_col else self.response_col
        )
        data = self.data[data_column].tolist()
        return [text for text in data if word in text]

    def count_occurrences(self, word: str, pair_type: str = "prompt") -> int:
        """Counts the number of occurrences of a word in the data"""
        if pair_type not in [self.prompt_col, self.response_col, "both"]:
            raise ValueError(
                f"Invalid pair_type. Choose from '{self.prompt_col}', '{self.response_col}', 'both'"
            )

        text = ""
        if pair_type in [self.prompt_col, "both"]:
            text += " ".join(self.data[self.prompt_col].tolist())

        if pair_type in [self.response_col, "both"]:
            text += " ".join(self.data[self.response_col].tolist())

        return Counter(text.split())[word]

    def compute_similar_keywords(
        self,
        keywords: List[str],
        num_keywords: int = 10,
        use_argmax: bool = True,
        per_keyword: bool = False,
        query: Optional[str] = None,
    ) -> List[str]:
        """
        Compute similar keywords based on embeddings.

        Args:
            keywords (List[str]): List of keywords for which to find similar keywords.
            num_keywords (int, optional): Number of similar keywords to return. Defaults to 10.
            use_argmax (bool, optional): Whether to use argmax for similarity scores. Defaults to True.
            per_keyword (bool, optional): Whether to compute similar keywords per keyword. Defaults to False.
            query (Optional[str], optional): Query keyword for which to find similar keywords. Defaults to None.

        Returns:
            List[str]: List of similar keywords.
        """
        embeddings = self.model.fit(keywords)

        if query is not None:
            query_vector = self.model.fit([query])[0]
            similarity_scores = compute_similar_keywords_query(
                keywords, query_vector, use_argmax, query
            )
        else:
            if per_keyword:
                similarity_scores = compute_similar_keywords_per_keyword(
                    keywords, embeddings, num_keywords
                )
            else:
                similarity_scores = compute_similar_keywords_global(
                    keywords, embeddings, use_argmax, num_keywords
                )

        return similarity_scores

    def time_decay(self, timestamps, current_time, decay_factor=0.9):
        """
        Calculate the time decay factor for a list of timestamps.

        Args:
            timestamps (list): List of timestamps.
            current_time (datetime): The current time.
            decay_factor (float): The decay factor to be used. Defaults to 0.9.

        Returns:
            numpy.array: An array of decay factors corresponding to each timestamp.
        """
        time_deltas = [(current_time - timestamp).days for timestamp in timestamps]
        return np.array([decay_factor**delta for delta in time_deltas])

    def apply_decay(self, scores, timestamps, current_time):
        """
        Apply time decay factors to a list of similarity scores.

        Args:
            scores (numpy.array): Array of similarity scores.
            timestamps (list): List of timestamps.
            current_time (datetime): The current time.

        Returns:
            numpy.array: Decay-applied similarity scores.
        """
        decay_factors = self.time_decay(timestamps, current_time)
        return scores * decay_factors

    def get_embedding_vectors(self, col_name, texts):
        """
        Retrieve or generate embedding vectors for a specified column in the data.

        Args:
            col_name (str): Name of the column.
            texts (list): List of texts to generate embeddings for if not already in the column.

        Returns:
            numpy.array: An array of embeddings.
        """
        if col_name in self.data.columns:
            self.data[col_name] = self.data[col_name].apply(ast.literal_eval)
            vectors = np.array(self.data[col_name].tolist()).reshape(-1, 768)
        else:
            vectors = np.array(self.model.encode_texts(texts))
        return vectors

    def find_similar(
        self,
        text: str,
        top_n: int = 1,
        initial_k: int = 10,
        apply_time_decay: bool = False,
        display_scores: bool = False,
        pair_type: str = "response",
        compute_keywords: bool = False,
    ) -> Union[List[Tuple[str, str, float]], List[Tuple[str, str]]]:
        """
        Finds the most similar texts from a corpus based on the given text.

        Args:
            text (str): The input text to find similar items for.
            top_n (int): The number of most similar items to return. Defaults to 1.
            initial_k (int): Number of top similar entries to consider for further steps. Defaults to 10.
            apply_time_decay (bool): Whether to apply time decay to similarity scores. Defaults to False.
            display_scores (bool): Whether to display similarity scores along with the results. Defaults to False.
            pair_type (str): Which type of pair to consider, can be either 'prompt' or 'response'. Defaults to 'response'.

        Returns:
            Union[List[Tuple[str, str, float]], List[Tuple[str, str]]]: The most similar items along with their scores if `display_scores=True`, otherwise just the items.
        """
        if compute_keywords:
            # Assuming the DataFrame has a 'keyword' column
            keywords_from_df = self.data["keyword"].tolist()

            return self.compute_similar_keywords(
                keywords=keywords_from_df,
                num_keywords=top_n,
                use_argmax=True,
                query=text,  # Pass the 'text' as 'query'
            )
        current_time = datetime.now()
        query_vector = self.model.encode_texts([text])[0]

        target_col = self.response_col if pair_type == "response" else self.prompt_col
        target_embedding_col = f"{pair_type}_embedding"

        target_vectors = self.get_embedding_vectors(
            target_embedding_col, self.data[target_col].tolist()
        )
        similarity_scores = cosine_similarity([query_vector], target_vectors)[0]

        self.data["created_time"] = pd.to_datetime(self.data["created_time"], unit="s")

        if apply_time_decay:
            decayed_scores = self.apply_decay(
                similarity_scores, self.data["created_time"], current_time
            )
        else:
            decayed_scores = similarity_scores

        top_k_indices = decayed_scores.argsort()[-initial_k:][::-1]
        selected_texts = self.data.iloc[top_k_indices][target_col].tolist()

        if display_scores:
            results_with_scores = [
                (selected_texts[i], decayed_scores[top_k_indices[i]])
                for i in range(len(top_k_indices))
            ]
            sorted_results = sorted(
                results_with_scores, key=lambda x: x[1], reverse=True
            )
            return sorted_results[:top_n]
        else:
            return selected_texts[:top_n]
