from dlm_matrix.services.utility.loader import DatasetLoader
from dlm_matrix.services.utility.helper import DataHelper
from dlm_matrix.services.utility.retriever import DataRetriever
from dlm_matrix.services.utility.tuner import DataTuner
from typing import List, Union, Optional, Callable, Tuple
import pandas as pd
import os


class DataEngine:
    def __init__(
        self,
        dataframe: Optional[pd.DataFrame] = None,
        local_dataset_path: Optional[str] = None,
        huggingface_dataset_name: Optional[str] = None,
        prompt_subdir: Optional[str] = "prompt/",
        prompt_col: str = "prompt",
        response_col: str = "response",
        root_directory: Optional[str] = None,
    ):
        # Default to the root directory of the current script if not provided
        if root_directory is None:
            root_directory = os.getcwd()

        # Here, concatenate root_directory and prompt_subdir to form the full path
        full_prompt_directory = (
            os.path.join(root_directory, prompt_subdir)
            if root_directory
            else prompt_subdir
        )

        self.dataset_loader = DatasetLoader(
            dataframe=dataframe,  # Pass the DataFrame here
            local_dataset_path=local_dataset_path,
            huggingface_dataset_name=huggingface_dataset_name,
            prompt_directory=full_prompt_directory,
            prompt_col=prompt_col,
            response_col=response_col,
        )
        self.data_helper = DataHelper(self.dataset_loader)
        self.data_tuner = DataTuner(self.dataset_loader)
        self.data_retriever = DataRetriever(data_helper=self.data_helper)
        self.manager = self.dataset_loader.prompt_manager
        self.prompt_col = prompt_col
        self.response_col = response_col
        self.root_directory = root_directory  # store the root separately

    def execute_chain(self, operations: List[Callable]) -> "DataEngine":
        """
        Apply a series of operations sequentially on the data using a chainable pattern.

        Args:
            operations (List[Callable]): A list of functions (operations) to be applied in order.
                                         Each item in the list should be a tuple of (function, args, kwargs),
                                         where function is a reference to the function to be called,
                                         args is a tuple of arguments, and kwargs is a dictionary of keyword arguments.

        Returns:
            DataEngine: The updated DataEngine instance after applying operations.
        """
        # Ensure the DataHelper's chain method is available
        if hasattr(self.data_helper, "chain"):
            self.data_helper.chain(operations)
        else:
            raise AttributeError(
                "DataHelper does not have a 'chain' method. Make sure it's defined."
            )

        return self

    def get_random_example_pairs(self):
        """
        Retrieves a random set of example pairs.

        Returns:
            List[Tuple[str, str]]: Random example pairs.
        """
        return self.data_helper.get_random_example_pairs()

    def filter_by_keyword(self, keyword: str) -> "DataEngine":
        """
        Filters the data by the given keyword, retaining only the entries that contain the keyword.

        Args:
            keyword (str): The keyword to filter by.

        Returns:
            DataEngine: The updated DataEngine instance.
        """
        self.data_helper.filter_by_keyword(keyword)
        return self

    def filter_by_condition(self, column: str, condition_fn: Callable) -> "DataEngine":
        """
        Filters the data by a custom condition on a specified column.

        Args:
            column (str): The name of the column to apply the condition to.
            condition_fn (Callable): A function that takes a column value and returns a boolean. Rows that meet the condition are retained.

        Returns:
            DataEngine: The updated DataEngine instance.
        """
        self.data_helper.filter_by_condition(column, condition_fn)
        return self

    def get_random_examples(self, n: int, pair_type: str = "both"):
        """
        Retrieves a random set of examples.

        Args:
            n (int): The number of random examples to retrieve.
            pair_type (str, optional): Specifies whether to retrieve "prompts", "responses", or "both". Defaults to "both".

        Returns:
            List[Union[str, Tuple[str, str]]]: Random examples of the specified type.
        """
        return self.data_retriever.get_random_examples(n, pair_type)

    def search_examples(self, keywords: Union[str, List[str]], pair_type: str = "both"):
        """
        Searches for examples containing the specified keywords.

        Args:
            keywords (Union[str, List[str]]): The keywords to search for.
            pair_type (str, optional): Specifies whether to retrieve "prompts", "responses", or "both". Defaults to "both".

        Returns:
            List[Union[str, Tuple[str, str]]]: Examples containing the specified keywords.
        """
        return self.data_retriever.search_examples(keywords, pair_type)

    def get_examples(self, pair_type: str = "both"):
        """
        Retrieves all examples.

        Args:
            pair_type (str, optional): Specifies whether to retrieve "prompts", "responses", or "both". Defaults to "both".

        Returns:
            List[Union[str, Tuple[str, str]]]: All examples of the specified type.
        """
        return self.data_retriever.get_examples(pair_type)

    def get_first_n_examples(self, n: int, pair_type: str = "both"):
        """
        Retrieves the first n examples.

        Args:
            n (int): The number of examples to retrieve.
            pair_type (str, optional): Specifies whether to retrieve "prompts", "responses", or "both". Defaults to "both".

        Returns:
            List[Union[str, Tuple[str, str]]]: The first n examples of the specified type.
        """
        return self.data_retriever.get_first_n_examples(n, pair_type)

    def count_keyword(self, keyword: str, pair_type: str = "both"):
        """
        Counts the number of examples containing the specified keyword.

        Args:
            keyword (str): The keyword to count.
            pair_type (str, optional): Specifies whether to count "prompts", "responses", or "both". Defaults to "both".

        Returns:
            Union[int, Dict[str, int]]: The number of examples containing the specified keyword.
        """
        return self.data_retriever.count_keyword(keyword, pair_type)

    def find_similar(
        self, keywords: Union[str, List[str]], num_keywords: int = 1, query: str = None
    ):
        """
        Finds examples similar to the given text.

        Args:
            text (str): The text to find similar examples to.
            top_n (int, optional): The number of top similar examples to retrieve. Defaults to 1.
            pair_type (str, optional): Specifies whether to retrieve "prompts", "responses", or None for both. Defaults to None.

        Returns:
            List[Union[str, Tuple[str, str]]]: Examples similar to the given text.
        """
        return self.data_retriever.compute_similar_keywords(
            keywords, num_keywords, query
        )

    def peek(self, rows: int = 5):
        """
        Allows users to peek into the current state of the data.

        Args:
            rows (int, optional): The number of rows to display. Defaults to 5.

        Returns:
            DataEngine: The current DataEngine instance, for chaining further operations.
        """
        self.data_helper.peek(rows)
        return self

    def finalize(self):
        """
        Concludes the chain and returns the final state of the data.

        Returns:
            pd.DataFrame: The final processed data.
        """
        return self.data_helper.finalize()

    def get_pairs_by_keyword(self, keyword: str) -> List[Tuple[str, str]]:
        """
        Retrieve (prompt, response) pairs that contain the given keyword.

        Args:
            keyword (str): The keyword to search for.

        Returns:
            List[Tuple[str, str]]: Pairs of prompts and responses containing the keyword.
        """
        filtered_data = self.data_helper.filter_by_keyword(keyword).finalize()
        return list(
            zip(filtered_data[self.prompt_col], filtered_data[self.response_col])
        )
