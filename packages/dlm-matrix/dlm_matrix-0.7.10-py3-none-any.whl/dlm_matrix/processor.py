from typing import Dict, List, Tuple
from dlm_matrix.builder import ChainTreeBuilder
from dlm_matrix.pipeline.element import ElementLoader
from sklearn.model_selection import train_test_split
from abc import ABC, abstractmethod
from dlm_matrix.infrence.parallel import SynergyParrallel
from torch.utils.data import DataLoader, TensorDataset
from transformers import AutoTokenizer
from tqdm import tqdm
import pandas as pd
import copy
import logging


class ScenarioHandler(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def identify(self, df: pd.DataFrame) -> List[Dict[str, int]]:
        """Identify scenarios in the dataframe."""
        pass

    @abstractmethod
    def handle(self, df: pd.DataFrame, pairs: List[Dict[str, int]]) -> None:
        """Handle identified scenarios."""
        pass


class PhaseHandler(ScenarioHandler):
    def identify(
        self,
        df: pd.DataFrame,
        phase: str,
        match_strategy: str = "start",
        include_more: bool = False,
        case_sensitive: bool = False,
    ) -> List[Dict[str, int]]:
        """
        Identify scenarios that match the specified phase.

        Parameters:
            df (pd.DataFrame): The data frame containing the conversation data.
            phase (str): The keyword or phrase to look for in the user's text to identify a particular phase.
            match_strategy (str, optional): The strategy used for matching phase in user texts.
                - "start": Match from the start of the user text
                - Other strategies can be defined. Default is "start".
            include_more (bool, optional): Whether to include more than just the exact match of 'phase'. Default is False.
            case_sensitive (bool, optional): Whether the match should be case-sensitive. Default is False.

        Returns:
            List[Dict[str, int]]: A list of dictionaries, each containing a pair of message IDs that match the condition.
            Each dictionary has two keys: 'user_message_id' and 'assistant_message_id'.

        Raises:
            Logs an error if an exception occurs.
        """
        try:
            if df.empty:
                return []

            # Filtering user rows based on the phase, match_strategy, include_more, and case_sensitive
            user_texts = df[df["author"] == "user"]["text"].tolist()
            filtered_user_texts = ElementLoader.filter_by_prefix(
                user_texts,
                phase,
                include_more=include_more,
                case_sensitive=case_sensitive,
                match_strategy=match_strategy,
            )

            user_rows_with_continue = df[df["text"].isin(filtered_user_texts)]

            next_rows = df.shift(-1)
            valid_next_rows = next_rows[next_rows["author"] == "assistant"]

            continue_pairs = [
                {"user_message_id": user_id, "assistant_message_id": assistant_id}
                for user_id, assistant_id in zip(
                    user_rows_with_continue["message_id"], valid_next_rows["message_id"]
                )
            ]

            return continue_pairs

        except Exception as e:
            self.logger.error(f"Error identifying continue scenarios: {str(e)}")
            return []

    def handle(
        self,
        df: pd.DataFrame,
        continue_pairs: List[Dict[str, int]],
        default_response: str = "Take it to the next level!",
    ) -> None:
        """
        Handle the scenarios identified by the 'identify' method.

        Parameters:
            df (pd.DataFrame): The data frame containing the conversation data.
            continue_pairs (List[Dict[str, int]]): A list of dictionaries with pairs of message IDs.
                Each pair consists of a 'user_message_id' and an 'assistant_message_id'.
            default_response (str, optional): The default response to insert into the data frame when a match is found.
                Default is "Take it to the next level!".

        Raises:
            Logs an error if an exception occurs.
        """
        try:
            for pair in continue_pairs:
                user_message_id = pair["user_message_id"]
                matching_rows = df[df["message_id"] == user_message_id]

                if matching_rows.empty:
                    continue

                idx = matching_rows.index[0]
                df.loc[idx, "text"] = default_response

        except Exception as e:
            self.logger.error(f"Error handling continue scenarios: {str(e)}")


class UnwantedHandler(ScenarioHandler):
    def __init__(self, unwanted_phrases: List[str]):
        """
        Initialize the UnwantedHandler class.

        Parameters:
            unwanted_phrases (List[str]): A list of phrases that are considered unwanted in assistant responses.
        """
        super().__init__()
        self.unwanted_phrases = unwanted_phrases

    def identify(self, df: pd.DataFrame) -> List[Dict[str, int]]:
        """
        Identify scenarios where the assistant's response includes any of the unwanted phrases.

        Parameters:
            df (pd.DataFrame): The data frame containing the conversation data.

        Returns:
            List[Dict[str, int]]: A list of dictionaries, each containing a pair of message IDs where unwanted phrases were used.
            Each dictionary has two keys: 'assistant_message_id' and 'user_message_id'.

        Raises:
            Logs an error if an exception occurs.
        """
        try:
            masks = [
                df["text"].str.contains(phrase, case=False, na=False)
                for phrase in self.unwanted_phrases
            ]
            combined_mask = pd.concat(masks, axis=1).any(axis=1)

            unwanted_assistant_rows = df[combined_mask & (df["author"] == "assistant")]

            previous_rows = df.shift(1)
            valid_previous_rows = previous_rows[previous_rows["author"] == "user"]

            message_pairs = [
                {"assistant_message_id": assistant_id, "user_message_id": user_id}
                for assistant_id, user_id in zip(
                    unwanted_assistant_rows["message_id"],
                    valid_previous_rows["message_id"],
                )
            ]

            return message_pairs

        except Exception as e:
            self.logger.error(
                f"Error identifying unwanted response scenarios: {str(e)}"
            )
            return []

    def handle(
        self,
        df: pd.DataFrame,
        message_pairs: List[Dict[str, int]],
        replacement_phrase: str = "I challenge you to make it better!",
    ) -> None:
        """
        Handle the scenarios where unwanted phrases are found in the assistant's responses.

        Parameters:
            df (pd.DataFrame): The data frame containing the conversation data.
            message_pairs (List[Dict[str, int]]): A list of dictionaries with pairs of message IDs.
                Each pair consists of an 'assistant_message_id' and a 'user_message_id'.
            replacement_phrase (str, optional): The phrase to replace the unwanted text with.
                Default is "I challenge you to make it better!".

        Raises:
            Logs an error if an exception occurs.
        """
        try:
            for pair in message_pairs:
                assistant_message_id = pair["assistant_message_id"]
                matching_rows = df[df["message_id"] == assistant_message_id]

                if matching_rows.empty:
                    continue

                idx = matching_rows.index[0]
                df.loc[idx, "text"] = replacement_phrase

        except Exception as e:
            self.logger.error(f"Error handling unwanted response scenarios: {str(e)}")


class ChainTreeProcessor:
    def __init__(
        self,
        builder: ChainTreeBuilder,
        initial_unwanted_phrases: List[str] = None,
        dataset_path: str = None,
        openai_api_key: str = None,
    ):
        self.builder = builder
        self.conversations_data = None
        self.conversations_df = self.builder.create_message_map(format="df")
        self.original_conversations_df = copy.deepcopy(self.conversations_df)
        self.data_processed = False
        self.unwanted_phrases = (
            initial_unwanted_phrases if initial_unwanted_phrases else []
        )
        # Initialize our handlers
        self.continue_handler = PhaseHandler()
        self.unwanted_response_handler = UnwantedHandler(self.unwanted_phrases)

        # Initialize the counters
        self.unwanted_phrase_count = 0
        self.continue_count = 0

        # Initialize generator only if openai_api_key is provided
        if openai_api_key:
            self.generator = SynergyParrallel(
                dataset_path=dataset_path, openai_api_key=openai_api_key
            )
        else:
            self.generator = None

    def reset_data(self):
        """
        Reset the conversations_df to its original state and reset the processing flag.

        This method sets `conversations_df` back to its original state by deep copying `original_conversations_df`
        and resets the `data_processed` flag to False.
        """
        self.conversations_df = copy.deepcopy(self.original_conversations_df)
        self.data_processed = False

    def add_unwanted_phrase(self, phrase: str):
        """
        Add a new unwanted phrase to the list.

        Parameters:
            phrase (str): The phrase to add to the unwanted_phrases list.
        """
        if phrase not in self.unwanted_phrases:
            self.unwanted_phrases.append(phrase)

    def remove_unwanted_phrase(self, phrase: str):
        """
        Remove an unwanted phrase from the list.

        Parameters:
            phrase (str): The phrase to remove from the unwanted_phrases list.
        """
        if phrase in self.unwanted_phrases:
            self.unwanted_phrases.remove(phrase)

    def update_unwanted_phrases(self, new_phrases: List[str]):
        """
        Update the list of unwanted phrases.

        Parameters:
            new_phrases (List[str]): The new list of phrases to set or merge with the existing list.

        Note:
            This method replaces the entire existing list with the new list.
        """
        self.unwanted_phrases = new_phrases

    def handle_continue_responses(self, continue_pairs: List[Dict[str, int]]) -> None:
        """
        Handle 'continue' scenarios using the handler.

        Parameters:
            continue_pairs (List[Dict[str, int]]): A list of dictionaries with pairs of message IDs that fall under 'continue' scenarios.
        """
        self.continue_handler.handle(self.conversations_df, continue_pairs)

    def replace_unwanted_responses(self, message_pairs: List[Dict[str, int]]) -> None:
        """
        Replace unwanted responses using the handler.

        Parameters:
            message_pairs (List[Dict[str, int]]): A list of dictionaries with pairs of message IDs where unwanted phrases were used.
        """
        self.unwanted_response_handler.handle(self.conversations_df, message_pairs)

    def identify_continue_scenarios(self, user_phase: str) -> List[Dict[str, int]]:
        """
        Identify and count 'continue' scenarios based on the user's phase or query.

        Parameters:
            user_phase (str): The phase or query from the user that needs to be checked for 'continue' scenarios.

        Returns:
            List[Dict[str, int]]: A list of dictionaries with pairs of message IDs that fall under 'continue' scenarios.
        """
        continue_pairs = self.continue_handler.identify(
            self.conversations_df, user_phase
        )
        self.continue_count += len(continue_pairs)  # Update the counter
        return continue_pairs

    def identify_unwanted_responses(
        self, unwanted_phrases: List[str]
    ) -> List[Dict[str, int]]:
        """
        Identify unwanted responses based on a list of unwanted phrases.

        This method updates the list of unwanted phrases, then identifies any message pairs
        where the assistant's response contains an unwanted phrase.

        Parameters:
            unwanted_phrases (List[str]): A list of phrases that are considered unwanted in the assistant's responses.

        Returns:
            List[Dict[str, int]]: A list of dictionaries with pairs of message IDs where unwanted phrases were used.
            The keys are "assistant_message_id" and "user_message_id".
        """
        self.update_unwanted_phrases(unwanted_phrases)
        message_pairs = self.unwanted_response_handler.identify(self.conversations_df)
        self.unwanted_phrase_count += len(message_pairs)  # Update the counter
        return message_pairs

    def process_conversation(self, user_phase: str) -> None:
        """
        Process the conversation data to handle 'continue' scenarios and replace unwanted responses.

        This method goes through a pipeline of:
            1. Identifying "continue" scenarios based on the user's phase.
            2. Handling the identified "continue" scenarios.
            3. Identifying unwanted responses.
            4. Replacing unwanted responses.

        The method sets a flag to mark the data as processed upon completion.

        Parameters:
            user_phase (str): The phase or query from the user that needs to be checked for 'continue' scenarios.
        """
        # Check if data has been processed already
        if self.data_processed:
            return

        # 1. Identify "continue" scenarios
        continue_pairs = self.identify_continue_scenarios(user_phase)

        # 2. Handle the identified "continue" scenarios
        self.handle_continue_responses(continue_pairs)

        # 3. Identify unwanted responses after handling "continue" scenarios
        message_pairs = self.identify_unwanted_responses(self.unwanted_phrases)

        # 4. Replace unwanted responses
        self.replace_unwanted_responses(message_pairs)

        # Mark the data as processed
        self.data_processed = True

    def _add_instructions(
        self,
        conversations_df: pd.DataFrame,
        instruction_params: Dict[str, str],
        potential_phrases: List[str],
    ):
        """
        Add instructions to the formatted text in the conversation DataFrame based on certain conditions.

        This method modifies the conversation DataFrame in-place by adding an instruction message
        either before or after the original text of messages. It adds a 'USER_CONTINUE_INSTRUCTION'
        if the 'continue' phrase appears in a user's text and an 'ASSISTANT_UNWANTED_INSTRUCTION'
        if any unwanted phrase appears in the assistant's text.

        Parameters:
            conversations_df (pd.DataFrame): The DataFrame containing the conversation data.
                This DataFrame should have at least the columns "formatted_text", "text", and "author".

            instruction_params (Dict[str, str]): A dictionary containing the instruction messages to be added.
                Should contain keys "USER_CONTINUE_INSTRUCTION" and "ASSISTANT_UNWANTED_INSTRUCTION"
                along with a "REVERSE_INSTRUCTION_PLACEMENT" flag indicating whether the instruction
                should be placed before or after the original text.

            potential_phrases (List[str]): A list of phrases that are considered unwanted in the assistant's responses.
        """

        def modify_text(row, instruction_key, condition_key=None):
            instruction = instruction_params[instruction_key]
            reverse_placement = instruction_params["REVERSE_INSTRUCTION_PLACEMENT"]
            if reverse_placement:
                return instruction + row["formatted_text"]
            else:
                return row["formatted_text"] + instruction

        conversations_df["formatted_text"] = conversations_df.apply(
            lambda row: modify_text(row, "USER_CONTINUE_INSTRUCTION")
            if "continue" in row["text"].lower() and row["author"] == "user"
            else row["formatted_text"],
            axis=1,
        )
        conversations_df["formatted_text"] = conversations_df.apply(
            lambda row: modify_text(row, "ASSISTANT_UNWANTED_INSTRUCTION")
            if any(
                phrase.lower() in row["text"].lower() for phrase in potential_phrases
            )
            and row["author"] == "assistant"
            else row["formatted_text"],
            axis=1,
        )

    def prepare_conversation_data(
        self,
        user_phase: str = "",
        test_size: float = 0.1,
        regenerate: bool = False,
        instruction_params: Dict[str, str] = None,
        use_instruction: bool = False,
    ) -> Tuple[List[str], List[str]]:
        """
        Prepare the conversation data for training or validation.

        This method processes the conversation DataFrame, optionally adds instructions, regenerates prompts,
        and then splits the data into training and validation sets.

        Parameters:
            user_phase (str, optional): The specific phase or context of user interactions that need to be processed.
                Default is an empty string, which means no specific phase is considered.

            test_size (float, optional): The proportion of the dataset to be used as the validation set.
                Should be between 0 and 1. Default is 0.1.

            regenerate (bool, optional): Flag to indicate whether to regenerate the assistant's responses
                that include unwanted phrases. Default is False.

            instruction_params (Dict[str, str], optional): A dictionary containing instruction messages
                that can be added to the text in the DataFrame.
                Default is a set of placeholder instructions.

            use_instruction (bool, optional): Flag to indicate whether to add instructions to the DataFrame
                based on the conditions. Default is False.

        Returns:
            Tuple[List[str], List[str]]: Returns a tuple containing the list of training texts and the list
                of validation texts.

        Raises:
            ValueError: If test_size is not between 0 and 1.
        """

        if not (0 <= test_size <= 1):
            raise ValueError("test_size should be between 0 and 1.")

        if instruction_params is None:
            instruction_params = {
                "USER_CONTINUE_INSTRUCTION": "Your_Instruction_Here",
                "ASSISTANT_UNWANTED_INSTRUCTION": "Your_Other_Instruction_Here",
                "REVERSE_INSTRUCTION_PLACEMENT": True,
            }

        if not regenerate:
            self.process_conversation(user_phase)

        # Step 1: Extract Conversations
        conversations_df = self.conversations_df

        # Step 2: Preprocess Conversations
        conversations_df["formatted_text"] = (
            conversations_df["author"] + ": " + conversations_df["text"]
        )

        # Optional: Add instructions
        if use_instruction:
            self._add_instructions(
                conversations_df, instruction_params, self.unwanted_phrases
            )

        # Step 3: Combine Conversations
        grouped_conversations = (
            conversations_df.groupby("title")["formatted_text"]
            .apply(lambda x: "\n".join(x))
            .reset_index()
        )

        total_prompts = 0
        potential_phrases = self.unwanted_phrases

        for _, row in grouped_conversations.iterrows():
            convo_texts = row["formatted_text"].split("\n")
            total_prompts += sum(
                1
                for text in convo_texts
                if text.startswith("assistant:")
                and any(phrase in text for phrase in potential_phrases)
            )

        print(f"Total number of prompts to be regenerated: {total_prompts}")

        # Now proceed with regeneration.
        if (
            regenerate and total_prompts > 0
        ):  # Only proceed if there are prompts to regenerate
            with tqdm(total=total_prompts, desc="Regenerating Prompts") as pbar:
                for _, row in grouped_conversations.iterrows():
                    convo_texts = row["formatted_text"].split("\n")
                    for i, text in enumerate(convo_texts):
                        if text.startswith("assistant:"):
                            if any(phrase in text for phrase in potential_phrases):
                                pbar.update(1)  # Update tqdm progress bar
                                prompt = convo_texts[i - 1] if i - 1 >= 0 else ""
                                new_response = self.generator.generate_prompt_task(
                                    prompt=prompt,
                                    response=text.split("assistant:")[-1],
                                    include_prompt_in_create=True,
                                )
                                convo_texts[i] = "assistant: " + new_response[0]

                    row["formatted_text"] = "\n".join(convo_texts)

        # Step 5 (or Step 4 if not regenerating): Split Data
        train_texts, val_texts = train_test_split(
            grouped_conversations["formatted_text"].tolist(), test_size=test_size
        )

        # Save the conversation data to CSV
        self.conversations_data = grouped_conversations

        self.conversations_data.to_csv("conversations_data.csv", index=False)

        return train_texts, val_texts

    def tokenize_texts(
        self,
        train_texts: List[str],
        val_texts: List[str],
        batch_size: int = 16,
        max_sequence_length: int = 100,
    ) -> Tuple[DataLoader, DataLoader]:
        """
        Tokenizes the given train and validation texts and returns DataLoader objects.
        :param train_texts: List of training texts.
        :param val_texts: List of validation texts.
        :param batch_size: Batch size for both training and validation DataLoader.
        :param max_sequence_length: The maximum length for each sequence. Sequences longer than this will be truncated.
        :return: Tuple of training and validation DataLoaders.
        """
        # Using a pretrained tokenizer (GPT-2 in this example)
        tokenizer = AutoTokenizer.from_pretrained("gpt2")

        # Setting the padding token
        tokenizer.pad_token = tokenizer.eos_token

        # Tokenizing the datasets
        train_encodings = tokenizer(
            train_texts,
            truncation=True,
            padding="max_length",
            max_length=max_sequence_length,
            return_tensors="pt",
        )
        val_encodings = tokenizer(
            val_texts,
            truncation=True,
            padding="max_length",
            max_length=max_sequence_length,
            return_tensors="pt",
        )

        # Convert to PyTorch DataLoader format
        train_dataset = TensorDataset(
            train_encodings.input_ids, train_encodings.attention_mask
        )
        val_dataset = TensorDataset(
            val_encodings.input_ids, val_encodings.attention_mask
        )

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        return train_loader, val_loader
