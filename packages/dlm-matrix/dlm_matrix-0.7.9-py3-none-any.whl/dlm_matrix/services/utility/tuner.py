import openai
import os
import pandas as pd
from typing import Optional
from dlm_matrix.services.utility.loader import DatasetLoader
import time


class DataTuner:
    def __init__(self, dataset_loader: DatasetLoader):
        self.dataset_loader = dataset_loader

    def wait_for_file_ready(self, file_id, timeout=600, poll_interval=10):
        """
        Polls OpenAI's servers for the file's status until it's ready or until the timeout.

        Args:
            file_id (str): The ID of the uploaded file.
            timeout (int, optional): Maximum waiting time in seconds. Defaults to 600 (10 minutes).
            poll_interval (int, optional): Time in seconds between each polling request. Defaults to 10.

        Returns:
            bool: True if the file is ready, False otherwise.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            file_status = openai.File.retrieve(file_id)
            if file_status["status"] == "processed":
                return True
            time.sleep(poll_interval)
        return False

    def process_and_fine_tune(
        self,
        conversation_dataframe: pd.DataFrame,
        output_filename: str,
        model_suffix: str,
        system_message_text: str = "",
        target_model: str = "gpt-3.5-turbo",
        upload_purpose: str = "fine-tune",
        openai_api_key: Optional[str] = None,
    ) -> str:
        """
        Generates training examples from a DataFrame and fine-tunes a language model.

        Args:
            conversation_dataframe: DataFrame containing the conversation data.
            output_filename: The name of the output file where training data will be saved.
            system_message_text: Text for the system message to include in the training data.
            model_suffix: Suffix for the fine-tuned model.
            target_model: Name of the base model to fine-tune. Defaults to 'gpt-3.5-turbo'.
            upload_purpose: Purpose for uploading the training file. Defaults to 'fine-tune'.
            openai_api_key: OpenAI API key, if not available as an environment variable.

        Returns:
            str: The job ID for the fine-tuning process.
        """

        # Step 1: Generate Training Examples
        # Generate training examples and save them in a file. This file will be uploaded for fine-tuning.
        print("Generating training examples...")
        self.dataset_loader.generate_training_examples(
            conversation_dataframe, output_filename, system_message_text
        )

        # Append the appropriate file extension for the fine-tuning process
        jsonl_output_filename = f"{output_filename}.jsonl"
        print(f"Training examples saved to {jsonl_output_filename}")

        # Step 2: File Upload for Fine-Tuning
        # Initialize OpenAI API key
        openai.api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")

        # Upload the file
        print("Uploading training file to OpenAI...")
        with open(jsonl_output_filename, "rb") as training_file:
            uploaded_file_id = openai.File.create(
                file=training_file, purpose=upload_purpose
            ).id

        # Wait for OpenAI to process the uploaded file
        print(f"Waiting for file {uploaded_file_id} to be processed...")
        if not self.wait_for_file_ready(uploaded_file_id):
            raise Exception(f"File {uploaded_file_id} was not ready after waiting.")

        # Step 3: Fine-Tuning the Model
        # Start the fine-tuning process
        print(f"Starting the fine-tuning process on model: {target_model}")
        fine_tuning_job = openai.FineTuningJob.create(
            training_file=uploaded_file_id,
            model=target_model,
            suffix=model_suffix,
        )

        print(f"Fine-tuning job started with ID: {fine_tuning_job.id}")

        return fine_tuning_job.id
