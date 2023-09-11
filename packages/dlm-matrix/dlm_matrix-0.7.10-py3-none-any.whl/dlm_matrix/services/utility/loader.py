import pandas as pd
from typing import Union, Optional
import os
import json
from dlm_matrix.services.utility.prompt import PromptManager
import logging
from sklearn.model_selection import train_test_split
import random
from pathlib import Path
import os
import json
import logging


class DatasetLoader:
    def __init__(
        self,
        prompt_directory: str,
        prompt_col: str,
        response_col: str,
        data_split: str = "train",
        dataframe: Optional[pd.DataFrame] = None,
        local_dataset_path: Optional[str] = None,
        huggingface_dataset_name: Optional[str] = None,
    ):
        # Ensure only one data source is provided
        sources = [dataframe, local_dataset_path, huggingface_dataset_name]
        if sum(source is not None for source in sources) > 1:
            logging.error("Please provide only one data source.")
            raise ValueError("Multiple data sources provided.")

        # Load the data
        if dataframe is not None:
            self.data = dataframe
            self.output_directory = Path.cwd()
            logging.info(f"Loaded data from DataFrame.")
        elif local_dataset_path:
            self._load_data_from_local_path(local_dataset_path)
            self.output_directory = Path(os.path.dirname(local_dataset_path))
        elif huggingface_dataset_name:
            self.data = self._load_data_from_huggingface(
                huggingface_dataset_name, data_split, prompt_col, response_col
            )
            self.output_directory = Path.cwd()
        else:
            logging.error("No data source provided.")
            raise ValueError("No data source provided.")
        self.prompt_manager = PromptManager(prompt_directory)

        # Set and create prompt directory
        self.prompt_directory = self.output_directory / prompt_directory
        self.prompt_directory.mkdir(parents=True, exist_ok=True)

        self.prompt_col = prompt_col
        self.response_col = response_col

        logging.info(
            f"Data loaded and prompt directory set to: {self.prompt_directory}"
        )

    def _load_data_from_local_path(self, dataset_path: str):
        """Load data from a given local path."""

        if not Path(dataset_path).exists():
            logging.error(f"Provided dataset path does not exist: {dataset_path}")
            raise FileNotFoundError("Dataset path not found.")

        _, file_extension = os.path.splitext(dataset_path)
        if file_extension == ".csv":
            self.data = pd.read_csv(dataset_path)
            logging.info(f"Loaded data from CSV at {dataset_path}")
        elif file_extension == ".json":
            with open(dataset_path, "r") as file:
                json_data = json.load(file)
                self.data = pd.DataFrame(json_data)
            logging.info(f"Loaded data from JSON at {dataset_path}")
        else:
            logging.error(
                f"Unsupported file format {file_extension}. Only .csv and .json are supported."
            )
            raise ValueError("Unsupported file format.")

    def _load_data_from_huggingface(
        self, dataset_name: str, split: str, prompt_col, response_col
    ):
        """Load data from the HuggingFace datasets library."""

        from datasets import load_dataset

        dataset = load_dataset(dataset_name, split=split)

        # Rename columns
        dataset = dataset.rename_column("input_text", prompt_col)
        dataset = dataset.rename_column("output_text", response_col)

        # Convert to pandas DataFrame
        self.data = dataset.to_pandas()

        logging.info(f"Loaded data from HuggingFace dataset: {dataset_name} ({split})")

        return self.data

    def preview(self, n: int = 5) -> None:
        """Preview the first n rows of the loaded dataset."""
        if n <= 0:
            print("Please provide a positive integer for preview.")
            return
        print(self.data.head(n))

    def get_dataset(self) -> pd.DataFrame:
        """Return the loaded dataset."""
        return self.data

    def split_jsonl_data(
        self,
        original_file_path: str,
        train_file_path: str,
        test_file_path: str,
        train_proportion: float = 0.8,
    ):
        """
        Splits a .jsonl dataset into training and testing sets, saving them into separate files.

        Args:
        - original_file_path (str): Path to the original .jsonl file.
        - train_file_path (str): Path to the output .jsonl file for training data.
        - test_file_path (str): Path to the output .jsonl file for testing data.
        - train_proportion (float): Proportion of data to use for training. Defaults to 0.8.

        Returns:
        - None
        """

        # Read the original .jsonl file and load all lines
        with open(original_file_path, "r") as f:
            lines = f.readlines()

        # Shuffle the lines
        random.shuffle(lines)

        # Calculate the number of lines for training
        num_train = int(train_proportion * len(lines))

        # Write the training lines to the training output file
        with open(train_file_path, "w") as f:
            for line in lines[:num_train]:
                f.write(line)

        # Write the testing lines to the testing output file
        with open(test_file_path, "w") as f:
            for line in lines[num_train:]:
                f.write(line)

        print(
            f"Data split complete. {num_train} lines written to {train_file_path} and {len(lines) - num_train} lines written to {test_file_path}."
        )

    def generate_training_examples(
        self,
        data: Union[str, pd.DataFrame],
        filename: str,
        system_message: str = "You are a helpful assistant.",
    ) -> None:
        """
        Generate training examples in the format required for GPT-3.5 fine-tuning and save to a .jsonl file.

        Args:
            data (Union[str, pd.DataFrame]): If a string is provided, it's treated as a path to a CSV file. If a DataFrame is provided, it's used directly.
            filename (str): Name of the file to save the training examples to.
            system_message (str): System message to prepend to each conversation.

        Returns:
            None
        """

        # Check if data is a string (path to CSV) or a DataFrame
        if isinstance(data, str):
            df = pd.read_csv(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError(
                "The 'data' argument must be either a path to a CSV file or a pandas DataFrame."
            )

        training_examples = []

        for index, row in df.iterrows():
            training_example = {
                "messages": [
                    {"role": "system", "content": system_message.strip()},
                    {"role": "user", "content": row["prompt"]},
                    {"role": "assistant", "content": row["response"]},
                ]
            }
            training_examples.append(training_example)

        # Save training examples to a .jsonl file
        with open(f"{filename}.jsonl", "w") as f:
            for example in training_examples:
                f.write(json.dumps(example) + "\n")

    def clean_data(self, prompt_col: str, response_col: str) -> pd.DataFrame:
        """
        Clean the loaded dataset.

        Args:
        - prompt_col (str): Name of the prompt column.
        - response_col (str): Name of the response column.

        Returns:
        - pd.DataFrame: The cleaned dataset.
        """

        # Clean up leading and trailing whitespaces from the response column
        self.data[response_col] = self.data[response_col].apply(
            lambda x: "\n".join([line.strip() for line in x.split("\n")])
        )

        # clean up leading and trailing whitespaces from the prompt column
        self.data[prompt_col] = self.data[prompt_col].apply(
            lambda x: "\n".join([line.strip() for line in x.split("\n")])
        )

        # Remove duplicate rows
        self.data.drop_duplicates(subset=[prompt_col, response_col], inplace=True)

        # Remove rows where the prompt and response are the same
        self.data = self.data[
            self.data[prompt_col] != self.data[response_col]
        ].reset_index(drop=True)

        # Remove rows where the prompt is empty
        self.data = self.data[self.data[prompt_col] != ""].reset_index(drop=True)

        # Remove rows where the response is empty
        self.data = self.data[self.data[response_col] != ""].reset_index(drop=True)

        return self.data

    def get_data_columns(self):
        """Return the names of the prompt and response columns."""
        return self.prompt_col, self.response_col

    def split_data(
        self,
        test_size: float = 0.1,
        random_state: Optional[int] = None,
        file_name_prefix: Optional[str] = "split_data",
    ) -> (pd.DataFrame, pd.DataFrame):
        """
        Split the dataset into training and test sets and save them as .jsonl files.

        Args:
        - test_size (float): Proportion of the dataset to include in the test set. Defaults to 0.1 (10%).
        - random_state (int, optional): Seed for the random number generator. Defaults to None.
        - file_name_prefix (str, optional): Prefix for the output files where the train and test sets will be saved. Defaults to 'split_data'.

        Returns:
        - tuple(pd.DataFrame, pd.DataFrame): The training and test DataFrames.
        """

        if self.data is None:
            raise ValueError("Data is not loaded. Cannot perform split.")

        train_data, test_data = train_test_split(
            self.data, test_size=test_size, random_state=random_state
        )

        # Reset the indices for good measure
        train_data = train_data.reset_index(drop=True)
        test_data = test_data.reset_index(drop=True)

        # Full paths for saving train and test data
        train_file_path = f"{self.prompt_directory}{file_name_prefix}_train.jsonl"
        test_file_path = f"{self.prompt_directory}{file_name_prefix}_test.jsonl"
        original_file_path = f"{self.prompt_directory}{file_name_prefix}_original.jsonl"

        # Save train and test data to .jsonl files
        with open(train_file_path, "w") as f:
            for _, row in train_data.iterrows():
                f.write(json.dumps(row.to_dict()) + "\n")

        with open(test_file_path, "w") as f:
            for _, row in test_data.iterrows():
                f.write(json.dumps(row.to_dict()) + "\n")

        # Save original data to .jsonl file
        with open(original_file_path, "w") as f:
            for _, row in self.data.iterrows():
                f.write(json.dumps(row.to_dict()) + "\n")

        return train_data, test_data

    @classmethod
    def from_dataframe(
        cls,
        dataframe: pd.DataFrame,
        output_path: Union[str, Path],
        file_format: str = "csv",  # Default is csv, but can be set to json
        prompt_dir: str = "prompts",
        prompt_col: str = "prompt",  # New parameter
        response_col: str = "response",  # New parameter
    ) -> "DatasetLoader":
        """
        Create a DatasetLoader instance from a pandas DataFrame.

        Args:
        - dataframe (pd.DataFrame): The input dataframe.
        - output_path (Union[str, Path]): Path to save the processed dataset.
        - file_format (str): Desired output format, either "csv" or "json".
        - prompt_dir (str): Directory to save prompts.
        - prompt_col (str): Name of the prompt column.
        - response_col (str): Name of the response column.

        Returns:
        DatasetLoader: An instance of the DatasetLoader class.
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame.")

        # Ensure that the dataframe contains the necessary columns
        required_columns = [prompt_col, response_col]
        missing_columns = [
            col for col in required_columns if col not in dataframe.columns
        ]
        if missing_columns:
            raise ValueError(
                f"DataFrame is missing columns: {', '.join(missing_columns)}"
            )

        # Save to the appropriate format
        if file_format == "csv":
            dataframe.to_csv(output_path, index=False)
        elif file_format == "json":
            dataframe.to_json(output_path, orient="records", indent=4)
        else:
            raise ValueError(
                f"Unsupported file format: {file_format}. Supported formats are 'csv' and 'json'."
            )

        print(f"Data successfully saved to {output_path}")

        return cls(
            str(output_path),
            prompt_dir,
            prompt_col=prompt_col,
            response_col=response_col,
        )  # Updated constructor call

    def get_data_columns(self):
        """Return the names of the prompt and response columns."""
        return self.prompt_col, self.response_col

    def filter_responses(
        self,
        use_specific_patterns: bool = False,
        min_elements: Optional[int] = 6,
        element_type: str = "STEP",
    ) -> pd.DataFrame:
        """
        Filter responses based on the data source and certain conditions.

        Args:
        - use_specific_patterns (bool): Whether to use specific patterns for filtering.
        - min_elements (int, optional): Minimum number of elements for filtering.
        - element_type (str, optional): Type of element for filtering.

        Returns:
        - pd.DataFrame: The filtered or original data.
        """

        SPF = [
            "Imagine That:",
            "Brainstorming:",
            "Thought Provoking Questions:",
            "Create Prompts:",
            "Synergetic Prompt:",
            "Category:",
        ]
        if not use_specific_patterns:
            logging.info("Using data directly without filtering.")
            return self.data

        # If specific patterns are to be used for filtering
        cleaned_data = self.data.copy()

        # Clean up leading and trailing whitespaces from the response column
        cleaned_data[self.response_col] = cleaned_data[self.response_col].apply(
            lambda x: "\n".join([line.strip() for line in x.split("\n")])
        )

        for pattern in SPF:
            cleaned_data = cleaned_data[
                cleaned_data[self.response_col].str.contains(pattern)
            ]

        cleaned_data = cleaned_data[
            cleaned_data[self.response_col].apply(
                lambda x: len([part for part in x.split(element_type) if ":" in part])
                >= min_elements
            )
        ]

        logging.info(
            f"Filtered data using specific patterns and found {len(cleaned_data)} relevant responses."
        )
        return cleaned_data

    def generate_prompts(
        self,
        use_specific_patterns: bool = False,
        min_elements: Optional[int] = 6,
        element_type: str = "STEP",
    ) -> None:
        """
        Generate prompts from the loaded dataset.

        Args:
        - use_specific_patterns (bool): Whether to use specific patterns for filtering.
        - min_elements (int, optional): Minimum number of elements for filtering.
        - element_type (str, optional): Type of element for filtering.
        """

        # Filter the responses
        filtered_data = self.filter_responses(
            use_specific_patterns, min_elements, element_type
        )

        # Generate prompts
        self.prompt_manager.generate_prompts(
            filtered_data[self.prompt_col], filtered_data[self.response_col]
        )

    def generate_prompts_from_dataframe(
        self,
        dataframe: pd.DataFrame,
        prompt_col: str = "prompt",
        response_col: str = "response",
    ) -> None:
        """
        Generate prompts from a given dataframe.

        Args:
        - dataframe (pd.DataFrame): The input dataframe.
        - prompt_col (str): Name of the prompt column.
        - response_col (str): Name of the response column.
        """
        self.prompt_manager.generate_prompts(
            dataframe[prompt_col], dataframe[response_col]
        )

    def generate_prompts_from_file(
        self,
        file_path: Union[str, Path],
        prompt_col: str = "prompt",
        response_col: str = "response",
    ) -> None:
        """
        Generate prompts from a given file.

        Args:
        - file_path (Union[str, Path]): Path to the input file.
        - prompt_col (str): Name of the prompt column.
        - response_col (str): Name of the response column.
        """
        dataframe = pd.read_csv(file_path)
        self.generate_prompts_from_dataframe(dataframe, prompt_col, response_col)

    def generate_prompts_from_huggingface(
        self,
        dataset_name: str,
        split: str = "train",
        prompt_col: str = "prompt",
        response_col: str = "response",
    ) -> None:
        """
        Generate prompts from a given HuggingFace dataset.

        Args:
        - dataset_name (str): Name of the dataset in HuggingFace.
        - split (str): Desired data split.
        - prompt_col (str): Name of the prompt column.
        - response_col (str): Name of the response column.
        """
        data = self._load_data_from_huggingface(
            dataset_name, split, prompt_col, response_col
        )
        self.generate_prompts_from_dataframe(data, prompt_col, response_col)
