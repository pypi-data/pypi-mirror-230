from typing import List, Dict, Any, Tuple, Optional, Iterable, Union, Type, TypeVar
import logging
import uuid
import os
import json
import random

T = TypeVar("T")


def log_handler(message: str, level: str = "info", step=None) -> None:
    """
    Handle logging with different log levels.
    """

    if step is not None:
        message = f"Step {step}: {message}"

    if level.lower() == "info":
        logging.info(message)
    elif level.lower() == "warning":
        logging.warning(message)
    elif level.lower() == "error":
        logging.error(message)


def setup_logging():
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("dlm_matrix/infrence/logs/synergy_chat.log"),
            logging.StreamHandler(),
        ],
    )


def generate_id() -> str:
    return str(uuid.uuid4())


def split_string_to_parts(raw: str, delimiter: str = "\n") -> List[str]:
    return raw.split(delimiter)


def get_from_dict_or_env(
    data: Dict[str, Any], key: str, env_key: str, default: Optional[str] = None
) -> str:
    """Get a value from a dictionary or an environment variable."""
    if key in data and data[key]:
        return data[key]
    else:
        return get_from_env(key, env_key, default=default)


def get_from_env(key: str, env_key: str, default: Optional[str] = None) -> str:
    """Get a value from a dictionary or an environment variable."""
    if env_key in os.environ and os.environ[env_key]:
        return os.environ[env_key]
    elif default is not None:
        return default
    else:
        raise ValueError(
            f"Did not find {key}, please add an environment variable"
            f" `{env_key}` which contains it, or pass"
            f"  `{key}` as a named parameter."
        )


def _flatten_dict(
    nested_dict: Dict[str, Any], parent_key: str = "", sep: str = "_"
) -> Iterable[Tuple[str, Any]]:
    """
    Generator that yields flattened items from a nested dictionary for a flat dict.

    Parameters:
        nested_dict (dict): The nested dictionary to flatten.
        parent_key (str): The prefix to prepend to the keys of the flattened dict.
        sep (str): The separator to use between the parent key and the key of the
            flattened dictionary.

    Yields:
        (str, any): A key-value pair from the flattened dictionary.
    """
    for key, value in nested_dict.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, dict):
            yield from _flatten_dict(value, new_key, sep)
        else:
            yield new_key, value


def flatten_dict(
    nested_dict: Dict[str, Any], parent_key: str = "", sep: str = "_"
) -> Dict[str, Any]:
    """Flattens a nested dictionary into a flat dictionary.

    Parameters:
        nested_dict (dict): The nested dictionary to flatten.
        parent_key (str): The prefix to prepend to the keys of the flattened dict.
        sep (str): The separator to use between the parent key and the key of the
            flattened dictionary.

    Returns:
        (dict): A flat dictionary.

    """
    flat_dict = {k: v for k, v in _flatten_dict(nested_dict, parent_key, sep)}
    return flat_dict


def filter_none_values(d):
    """
    Recursively filter out keys from dictionary d where value is None.
    """
    if not isinstance(d, dict):
        return d
    return {k: filter_none_values(v) for k, v in d.items() if v is not None}


def load_and_preprocess_data(
    path: str, key_field: str, target_num: int = None, verbose: bool = True
) -> Tuple[List[Dict[str, Any]], set]:
    def log(message: str):
        if verbose:
            print(message)

    # Load data
    if not os.path.exists(path):
        log(f"Error: File {path} does not exist.")
        return [], set()

    data = load_json(path)

    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        log(f"Error: File {path} doesn't contain a list of dictionaries.")
        return [], set()

    # Filter data
    if target_num is not None:
        data = [item for item in data if len(item.get("mapping", [])) >= target_num]

    # Extract keys
    keys = {item.get(key_field) for item in data if key_field in item}

    return data, keys


def manage_conversations(
    path_1: str,
    path_2: str,
    output_path: str,
    key_field: str = "create_time",
    operation_mode: str = "update",
    strict_mode: bool = False,
    target_num: int = None,
    verbose: bool = True,
    save_result: bool = True,
) -> List[Dict[str, Any]]:
    def log(message: str):
        if verbose:
            print(message)

    data_1, keys_1 = load_and_preprocess_data(path_1, key_field, target_num, verbose)
    data_2, keys_2 = load_and_preprocess_data(path_2, key_field, target_num, verbose)

    if not data_1 or not data_2:
        log("Error: One or both input files are not loaded properly.")
        return []

    # Check for strict mode
    if strict_mode and (None in keys_1 or None in keys_2):
        log(f"Error: Missing '{key_field}' field in one or more entries.")
        return []

    # Initialize result variable
    result = []

    if operation_mode == "difference":
        difference_keys = keys_2 - keys_1
        if not difference_keys:
            log("No new entries found in the second file based on the provided key.")
            return []
        result = [item for item in data_2 if item.get(key_field) in difference_keys]
        log(f"Found {len(result)} new entries based on '{key_field}'.")

    elif operation_mode == "update":
        unique_to_data_1 = [
            item for item in data_1 if item.get(key_field) not in keys_2
        ]
        shared_keys = keys_1.intersection(keys_2)
        updated_shared_conversations = [
            item for item in data_1 if item.get(key_field) in shared_keys
        ]
        unique_to_data_2 = [
            item for item in data_2 if item.get(key_field) not in keys_1
        ]

        result = unique_to_data_1 + updated_shared_conversations + unique_to_data_2
        log(f"Total of {len(result)} entries after updating.")

    else:
        log(f"Error: Invalid operation mode '{operation_mode}'.")
        return []

    if save_result:
        save_json(output_path, result)
        log(f"Saved results to {output_path}.")

    return result


def load_json(source: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    if not os.path.isfile(source):
        raise ValueError(f"{source} does not exist.")
    with open(source, "r") as f:
        data = json.load(f)
    return data


def save_json(path: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def combine_json_files(path1: str, path2: str, output_path: str) -> None:
    data1 = load_json(path1)
    data2 = load_json(path2)

    if not isinstance(data1, list) or not isinstance(data2, list):
        raise ValueError("Both input files should contain a list of JSON objects.")

    combined_data = data1 + data2

    save_json(output_path, combined_data)
    print(f"Combined data saved to {output_path}.")

    return combined_data


def save_message_to_json(message_data, json_file_path: str):
    # Make sure a "message" directory exists
    if not os.path.exists("message"):
        os.mkdir("message")

    # Construct the final path
    json_file_path = os.path.join("message", json_file_path)

    # Load existing messages if the file exists
    existing_messages = []
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            existing_messages = json.load(file)

    # Append new message data
    existing_messages.append(message_data)

    # Save all messages back to the file
    with open(json_file_path, "w") as file:
        json.dump(existing_messages, file, indent=4)


def backoff_handler(retries: int) -> float:
    """
    Handle backoff and retries by calculating the wait time.
    """
    return (2**retries) + random.random()


def parse_generic(data: Any, obj_class: Type[T]) -> Union[T, List[T]]:
    if isinstance(data, dict):
        return obj_class(**data)
    elif isinstance(data, list):
        return [obj_class(**item) for item in data]
    else:
        raise TypeError(
            "Invalid data type. Data should be a dictionary or a list of dictionaries."
        )


class InvalidChainTypeException(Exception):
    pass


class InvalidIdException(Exception):
    pass


class InvalidContentException(Exception):
    pass


class InvalidCoordinateException(Exception):
    pass


class APIFailureException(Exception):
    pass
