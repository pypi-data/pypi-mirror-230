from typing import List, Optional, Dict
from dlm_matrix.infrence.utils import (
    create_user_message,
    create_assistant_message,
    create_system_message,
)
from dlm_matrix.embedding import SpatialSimilarity, calculate_similarity
from dlm_matrix.type import ElementType
from dlm_matrix.models import ChainMap, NodeRelationship, ChainTree
from dlm_matrix.type import NodeRelationship
import numpy as np
import pandas as pd
import time
import uuid


class HierarchicalProcessor:
    def __init__(self, prompt_dir: str, key: str):
        """
        Initialize a PromptLoader with a specified directory and a semantic model.
        """
        self.prompt_dir = prompt_dir
        self.key = key
        self.semantic_model = SpatialSimilarity()
        self.embedding_size = 768

    def create_hierarchy(
        self, df: pd.DataFrame, element_type: ElementType
    ) -> List[ChainTree]:
        """
        Create a hierarchy with the prefix as the parent and the element index as the count of children.

        Args:
            df (pd.DataFrame): The DataFrame containing the elements and their embeddings.
            element_type (ElementType): The type of the elements (e.g., ElementType.STEP, ElementType.CHAPTER, ElementType.PAGE).

        Returns:
            List[ChainTree]: A list of ChainTree objects representing the hierarchy.
        """
        conversations = []

        for i, row in df.iterrows():  # Use i as the index for the element
            prefix_text = row[
                element_type.value + " 0"
            ]  # Use the element_type for column selection
            prefix_id = str(uuid.uuid4())
            prefix_embeddings = row[
                element_type.value + " 0 embedding"
            ]  # Use the element_type for column selection
            # Create the System message
            system_message = create_system_message()

            # Create the User message for the prefix
            prefix_user_message = create_user_message(
                message_id=prefix_id,
                text=prefix_text,
                user_embeddings=prefix_embeddings.tolist(),
            )

            # Create the ChainMap for the prefix
            prefix_chain_map = ChainMap(
                id=prefix_id,
                message=prefix_user_message,
                parent=system_message.id,
                children=[],
                references=[],
                relationships={
                    NodeRelationship.SOURCE: system_message.id,
                },
            )

            # Append the prefix chain map to the list of conversations
            conversations.append(
                ChainTree(
                    title=f"{i}",  # Use i as the title
                    create_time=time.time(),
                    update_time=time.time(),
                    mapping={
                        system_message.id: ChainMap(
                            id=system_message.id,
                            message=system_message,
                            children=[prefix_user_message.id],
                        ),
                        prefix_user_message.id: prefix_chain_map,
                    },
                    current_node=prefix_user_message.id,
                )
            )

            # Initialize the ID of the previous assistant message to the prefix
            previous_assistant_message_id = prefix_user_message.id

            # Add the element chain maps as children to the prefix chain map
            for j in range(1, len(df.columns)):
                element_col = f"{element_type.value} {j}"
                element_text = row.get(
                    element_col, ""
                )  # Use get method to safely access the column
                if not element_text:
                    continue

                element_id = str(uuid.uuid4())  # Generate a new UUID for each element
                element_embeddings = row.get(
                    f"{element_col} embedding"
                )  # Use get method for embeddings

                # Create the Assistant message for the element
                element_assistant_message = create_assistant_message(
                    text=element_text,
                    assistant_embeddings=element_embeddings
                    if isinstance(element_embeddings, list)
                    else element_embeddings.tolist(),
                )

                # Create the ChainMap for the element
                element_chain_map = ChainMap(
                    id=element_id,
                    message=element_assistant_message,
                    parent=prefix_id,
                    children=[],
                    references=[],
                    relationships={
                        NodeRelationship.PARENT: prefix_id,
                        NodeRelationship.PREVIOUS: previous_assistant_message_id,  # Add the previous assistant message's ID
                    },
                )

                # Append the element chain map to the prefix chain map's children
                prefix_chain_map.children.append(element_chain_map.id)

                # Add the element chain map to the mapping of the same ChainTree
                conversations[-1].mapping[
                    element_assistant_message.id
                ] = element_chain_map

                # Update the ID of the previous assistant message to the current element's assistant message ID
                previous_assistant_message_id = element_assistant_message.id

        return conversations

    def group_similar_terms_from_dict(
        self, embedding_dict: Dict[str, np.ndarray], similarity_threshold: float = 0.9
    ) -> List[str]:
        """
        Group similar terms based on their embeddings.
        Return the resulting list of grouped terms.

        Args:
            embedding_dict (Dict[str, np.ndarray]): The dictionary containing the terms and their embeddings.
            similarity_threshold (float, optional): The similarity threshold for grouping similar terms.
                Defaults to 0.9.

        Returns:
            List[str]: The list of grouped terms.
        """
        try:
            # Group similar terms based on their embeddings
            grouped_terms = []
            for term in embedding_dict.keys():
                if term not in grouped_terms:
                    grouped_terms.append(term)
                    for other_term in embedding_dict.keys():
                        if (
                            other_term not in grouped_terms
                            and calculate_similarity(
                                embedding_dict[term], embedding_dict[other_term]
                            )
                            >= similarity_threshold
                        ):
                            grouped_terms.append(other_term)

            return grouped_terms

        except Exception as e:
            print(f"Error grouping similar terms: {e}")
            return []

    def get_top_n_similar_terms(
        self,
        df: pd.DataFrame,
        element_type: ElementType,
        embedding_column: str,
        term: str,
        n: int = 5,
    ) -> pd.DataFrame:
        """
        Get the top n similar terms for a given term based on their embeddings.
        Return the resulting DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the elements and their embeddings.
            element_type (ElementType): The type of the elements (e.g., ElementType.STEP, ElementType.CHAPTER, ElementType.PAGE).
            embedding_column (str): The name of the column containing the embeddings.
            term (str): The term for which to find similar terms.
            n (int, optional): The number of similar terms to return. Defaults to 5.

        Returns:
            pd.DataFrame: The DataFrame with the top n similar terms.
        """
        try:
            # Get the embeddings for the given term
            term_embeddings = df[df[element_type.value] == term][embedding_column]

            # Calculate the similarity between the term and all other terms
            df_copy = (
                df.copy()
            )  # Create a copy of the DataFrame to avoid potential warnings
            df_copy["Similarity"] = df_copy[embedding_column].apply(
                lambda x: calculate_similarity(term_embeddings, x)
            )

            # Sort the DataFrame by similarity and return the top n similar terms
            return df_copy.sort_values(by="Similarity", ascending=False).head(n)

        except Exception as e:
            print(f"Error getting top n similar terms: {e}")
            return pd.DataFrame()

    def group_similar_terms(
        self,
        df: pd.DataFrame,
        element_type: ElementType,
        embedding_column: str,
        similarity_threshold: float = 0.9,
    ) -> pd.DataFrame:
        """
        Group similar terms in the DataFrame based on their embeddings.
        Return the resulting DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the elements and their embeddings.
            element_type (ElementType): The type of the elements (e.g., ElementType.STEP, ElementType.CHAPTER, ElementType.PAGE).
            embedding_column (str): The name of the column containing the embeddings.
            similarity_threshold (float, optional): The similarity threshold for grouping similar terms.
                Defaults to 0.9.

        Returns:
            pd.DataFrame: The DataFrame with grouped similar terms.
        """
        try:
            # Group similar terms based on their embeddings
            df_copy = (
                df.copy()
            )  # Create a copy of the DataFrame to avoid potential warnings
            embedding_dict = dict(
                zip(df_copy[element_type.value], df_copy[embedding_column])
            )
            grouped_terms = self.group_similar_terms_from_dict(
                embedding_dict, similarity_threshold
            )

            # Add the grouped terms to the DataFrame
            df_copy[element_type.value] = grouped_terms

            return df_copy

        except Exception as e:
            print(f"Error grouping similar terms: {e}")
            return pd.DataFrame()

    def build_hierarchy(
        self,
        conversations: List[List[ChainTree]],
        similarity_threshold: float = 0.8,
    ) -> ChainTree:
        """
        Build a hierarchy from a list of conversations.

        Args:
            conversations (List[List[ChainTree]]): A list of conversations.
            similarity_threshold (float): The threshold for considering messages as similar.

        Returns:
            ChainTree: The hierarchy.
        """
        # Merge the conversations into a single hierarchy
        merged_hierarchy = self.combined_hierarchy(conversations)

        # Build another layer of hierarchy based on assistant messages' similarity
        new_hierarchy = self.build_assistant_hierarchy(
            merged_hierarchy, similarity_threshold
        )

        return new_hierarchy

    def is_similar(
        self,
        chain_map: ChainMap,
        other_chain_map: ChainMap,
        similarity_threshold: float,
    ) -> bool:
        """
        Check if two ChainMaps are similar.

        Args:
            chain_map (ChainMap): The ChainMap to compare.
            other_chain_map (ChainMap): The other ChainMap to compare.
            similarity_threshold (float): The threshold for considering messages as similar.

        Returns:
            bool: True if the ChainMaps are similar, False otherwise.
        """
        # Check if the ChainMaps have the same author
        if chain_map.message.author.id == other_chain_map.message.author.id:
            # Check if the ChainMaps have the same parent
            if chain_map.parent == other_chain_map.parent:
                # Check if the ChainMaps have the same message
                if chain_map.message.content == other_chain_map.message.content:
                    return True

                # Check if the ChainMaps have similar messages
                similarity_score = calculate_similarity(
                    chain_map.message.embedding, other_chain_map.message.embedding
                )
                if similarity_score >= similarity_threshold:
                    return True

        return False

    def create_new_chain_map(
        self,
        chain_map: ChainMap,
        similar_messages: List[ChainMap],
        hierarchy: ChainTree,
    ) -> ChainMap:
        """
        Create a new ChainMap based on a ChainMap and a list of similar ChainMaps.

        Args:
            chain_map (ChainMap): The ChainMap to create a new ChainMap from.
            similar_messages (List[ChainMap]): A list of similar ChainMaps.
            hierarchy (ChainTree): The hierarchy to create the new ChainMap in.

        Returns:
            ChainMap: The new ChainMap.
        """
        # Create a new ChainMap
        new_chain_map = ChainMap(
            id=str(uuid.uuid4()),
            message=chain_map.message,
            parent=chain_map.parent,
            children=[],
            references=[],
            relationships={},
        )

        # Add the new ChainMap to the hierarchy
        hierarchy.mapping[new_chain_map.id] = new_chain_map

        # Add the new ChainMap to the parent's children
        if new_chain_map.parent:
            hierarchy.mapping[new_chain_map.parent].children.append(new_chain_map.id)

        # Add the new ChainMap to the similar messages' references
        for similar_message in similar_messages:
            similar_message.references.append(new_chain_map.id)

        return new_chain_map

    def build_assistant_hierarchy(
        self, merged_hierarchy: ChainTree, similarity_threshold: float = 0.8
    ) -> ChainTree:
        """
        Build another layer of hierarchy based on assistant messages' similarity.

        Args:
            merged_hierarchy (ChainTree): The merged hierarchy.
            similarity_threshold (float): The threshold for considering messages as similar.

        Returns:
            ChainTree: A new hierarchy with additional layers based on assistant messages.
        """
        new_hierarchy = ChainTree(
            title="Assistant Hierarchy",
            create_time=time.time(),
            update_time=time.time(),
            mapping={},
            current_node=None,
        )

        # Iterate through the ChainMaps in the merged hierarchy
        for chain_map in merged_hierarchy.mapping.values():
            # If the ChainMap belongs to an assistant message
            if chain_map.message.author.role == "assistant":
                # Find similar assistant messages within the new hierarchy
                similar_messages = []
                for existing_chain_map in new_hierarchy.mapping.values():
                    if existing_chain_map.message.author.role == "assistant":
                        similarity_score = calculate_similarity(
                            chain_map.message.embedding,
                            existing_chain_map.message.embedding,
                        )
                        if similarity_score >= similarity_threshold:
                            similar_messages.append(existing_chain_map)

                # If similar assistant messages exist, create a new ChainMap and add them as children
                if similar_messages:
                    new_chain_map = ChainMap(
                        id=str(uuid.uuid4()),
                        message=chain_map.message,
                        parent=None,
                        children=[similar_map.id for similar_map in similar_messages],
                        references=[],
                        relationships={},
                    )
                    new_hierarchy.mapping[new_chain_map.id] = new_chain_map

                    # Update parent and relationship information for similar assistant messages
                    for similar_map in similar_messages:
                        similar_map.parent = new_chain_map.id
                        similar_map.relationships[
                            NodeRelationship.PARENT
                        ] = new_chain_map.id

                # If no similar assistant messages exist, create a new ChainMap with no children
                else:
                    new_chain_map = ChainMap(
                        id=str(uuid.uuid4()),
                        message=chain_map.message,
                        parent=None,
                        children=[],
                        references=[],
                        relationships={},
                    )
                    new_hierarchy.mapping[new_chain_map.id] = new_chain_map

        # Set the current node to the first ChainMap in the new hierarchy
        new_hierarchy.current_node = list(new_hierarchy.mapping.keys())[0]

        return new_hierarchy

    def combined_hierarchy(self, conversations: List[List[ChainTree]]) -> ChainTree:
        """
        Merge a list of hierarchies into a single hierarchy.

        Args:
            conversations (List[List[ChainTree]]): A list of hierarchies.

        Returns:
            ChainTree: A single merged hierarchy.
        """
        # Create a new ChainTree
        merged_hierarchy = ChainTree(
            title="Merged Hierarchy",
            create_time=time.time(),
            update_time=time.time(),
            mapping={},
            current_node=None,
        )

        # Keep track of unique ChainMap IDs in the merged hierarchy
        merged_chain_map_ids = set()

        # Iterate through each hierarchy
        for conversation in conversations:
            # Iterate through each ChainMap in the hierarchy
            for chain_map in conversation.mapping.values():
                # Exclude the system message role
                if chain_map.message.author.role != "system":
                    # Add the ChainMap to the merged hierarchy if its ID is not already present
                    if chain_map.id not in merged_chain_map_ids:
                        merged_hierarchy.mapping[chain_map.id] = chain_map
                        merged_chain_map_ids.add(chain_map.id)

        # Set the current node to the first ChainMap in the merged hierarchy
        if merged_chain_map_ids:
            merged_hierarchy.current_node = list(merged_chain_map_ids)[0]

        return merged_hierarchy

    def group_similar_terms_from_dict(
        self, embedding_dict: Dict[str, np.ndarray], similarity_threshold: float = 0.9
    ) -> List[str]:
        """
        Group similar terms based on their embeddings.
        Return the resulting list of grouped terms.

        Args:
            embedding_dict (Dict[str, np.ndarray]): The dictionary containing the terms and their embeddings.
            similarity_threshold (float, optional): The similarity threshold for grouping similar terms.
                Defaults to 0.9.

        Returns:
            List[str]: The list of grouped terms.
        """
        try:
            # Group similar terms based on their embeddings
            grouped_terms = []
            for term in embedding_dict.keys():
                if term not in grouped_terms:
                    grouped_terms.append(term)
                    for other_term in embedding_dict.keys():
                        if (
                            other_term not in grouped_terms
                            and calculate_similarity(
                                embedding_dict[term], embedding_dict[other_term]
                            )
                            >= similarity_threshold
                        ):
                            grouped_terms.append(other_term)

            return grouped_terms

        except Exception as e:
            print(f"Error grouping similar terms: {e}")
            return []

    def group_similar_terms(
        self,
        df: pd.DataFrame,
        element_type: ElementType,
        embedding_column: str,
        similarity_threshold: float = 0.9,
    ) -> pd.DataFrame:
        """
        Group similar terms in the DataFrame based on their embeddings.
        Return the resulting DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the elements and their embeddings.
            element_type (ElementType): The type of the elements (e.g., ElementType.STEP, ElementType.CHAPTER, ElementType.PAGE).
            embedding_column (str): The name of the column containing the embeddings.
            similarity_threshold (float, optional): The similarity threshold for grouping similar terms.
                Defaults to 0.9.

        Returns:
            pd.DataFrame: The DataFrame with grouped similar terms.
        """
        try:
            # Group similar terms based on their embeddings
            df_copy = (
                df.copy()
            )  # Create a copy of the DataFrame to avoid potential warnings
            embedding_dict = dict(
                zip(df_copy[element_type.value], df_copy[embedding_column])
            )
            grouped_terms = self.group_similar_terms_from_dict(
                embedding_dict, similarity_threshold
            )

            # Add the grouped terms to the DataFrame
            df_copy[element_type.value] = grouped_terms

            return df_copy

        except Exception as e:
            print(f"Error grouping similar terms: {e}")
            return pd.DataFrame()

    def get_top_n_similar_terms(
        self,
        df: pd.DataFrame,
        element_type: ElementType,
        embedding_column: str,
        term: str,
        n: int = 5,
    ) -> pd.DataFrame:
        """
        Get the top n similar terms for a given term based on their embeddings.
        Return the resulting DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the elements and their embeddings.
            element_type (ElementType): The type of the elements (e.g., ElementType.STEP, ElementType.CHAPTER, ElementType.PAGE).
            embedding_column (str): The name of the column containing the embeddings.
            term (str): The term for which to find similar terms.
            n (int, optional): The number of similar terms to return. Defaults to 5.

        Returns:
            pd.DataFrame: The DataFrame with the top n similar terms.
        """
        try:
            # Get the embeddings for the given term
            term_embeddings = df[df[element_type.value] == term][embedding_column]

            # Calculate the similarity between the term and all other terms
            df_copy = (
                df.copy()
            )  # Create a copy of the DataFrame to avoid potential warnings
            df_copy["Similarity"] = df_copy[embedding_column].apply(
                lambda x: calculate_similarity(term_embeddings, x)
            )

            # Sort the DataFrame by similarity and return the top n similar terms
            return df_copy.sort_values(by="Similarity", ascending=False).head(n)

        except Exception as e:
            print(f"Error getting top n similar terms: {e}")
            return pd.DataFrame()

    def get_term_frequencies_from_string(self, text: str) -> Dict[str, int]:
        """
        Get the term frequencies for the given text.
        Return the resulting dictionary.

        Args:
            text (str): The text to get the term frequencies for.

        Returns:
            Dict[str, int]: The dictionary containing the term frequencies.
        """
        try:
            # Get the term frequencies for the given text
            term_frequencies = {}
            for term in text.split():
                if term in term_frequencies.keys():
                    term_frequencies[term] += 1
                else:
                    term_frequencies[term] = 1

            return term_frequencies

        except Exception as e:
            print(f"Error getting term frequencies: {e}")
            return {}

    def get_embeddings_separate_columns(
        self,
        df: pd.DataFrame,
        element_type: ElementType = ElementType.STEP,
    ) -> pd.DataFrame:
        """
        Add the embeddings for each step in a separate column.
        Return the resulting DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the steps.
            element_type (ElementType): The type of the elements (e.g., ElementType.STEP, ElementType.CHAPTER, ElementType.PAGE).

        Returns:
            pd.DataFrame: The DataFrame with the embeddings for each step in a separate column.
        """
        try:
            # Add the embeddings for each step in a separate column
            for i in range(self.embedding_size):
                df[f"{element_type.value}_{i}"] = df[element_type.value].apply(
                    lambda x: x[i] if len(x) > i else 0
                )

            return df

        except Exception as e:
            print(f"Error getting embeddings for each step in a separate column: {e}")
            return pd.DataFrame()

    def get_embeddings(
        self,
        df: pd.DataFrame,
        element_type: ElementType = ElementType.STEP,
        grouped_terms: Optional[Dict[str, str]] = None,
    ) -> Dict[str, np.ndarray]:
        """
        Get the embeddings for each element in the DataFrame.
        Return the resulting dictionary.

        Args:
            df (pd.DataFrame): The DataFrame containing the elements.
            element_type (ElementType): The type of the elements (e.g., ElementType.STEP, ElementType.CHAPTER, ElementType.PAGE).
            grouped_terms (Optional[Dict[str, str]], optional): The dictionary containing the grouped terms. Defaults to None.

        Returns:
            Dict[str, np.ndarray]: The dictionary containing the embeddings.
        """
        try:
            # Get the embeddings for each element
            embedding_dict = {}
            for index, row in df.iterrows():
                embedding_dict[row[element_type.value]] = self.get_embedding(
                    row[element_type.value], grouped_terms
                )

            return embedding_dict

        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return {}

    def get_embedding(
        self,
        text: str,
        grouped_terms: Optional[Dict[str, str]] = None,
    ) -> np.ndarray:
        """
        Get the embedding for the given text.
        Return the resulting array.

        Args:
            text (str): The text to get the embedding for.
            grouped_terms (Optional[Dict[str, str]], optional): The dictionary containing the grouped terms. Defaults to None.

        Returns:
            np.ndarray: The array containing the embedding.
        """
        try:
            # Get the embedding for the given text
            embedding = np.zeros(self.embedding_size)
            term_frequencies = self.get_term_frequencies(text)
            for term, frequency in term_frequencies.items():
                if grouped_terms is not None and term in grouped_terms.keys():
                    term = grouped_terms[term]
                try:
                    embedding += frequency * self.semantic_model.encode_texts(term)
                except Exception as e:
                    print(f"Error getting embedding for term {term}: {e}")

            return embedding

        except Exception as e:
            print(f"Error getting embedding: {e}")
            return np.zeros(self.embedding_size)

    def get_term_frequencies(
        self, df: pd.DataFrame, element_type: ElementType
    ) -> pd.DataFrame:
        """
        Get the term frequencies for each element in the DataFrame.
        Return the resulting DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the elements.
            element_type (ElementType): The type of the elements (e.g., ElementType.STEP, ElementType.CHAPTER, ElementType.PAGE).

        Returns:
            pd.DataFrame: The DataFrame with added columns for term frequencies.
        """
        try:
            # Get the term frequencies for each element
            df_copy = (
                df.copy()
            )  # Create a copy of the DataFrame to avoid potential warnings
            df_copy["term frequencies"] = df_copy[element_type.value].apply(
                lambda x: self.get_term_frequencies_from_string(x)
            )

            return df_copy

        except Exception as e:
            print(f"Error getting term frequencies: {e}")
            return pd.DataFrame()
