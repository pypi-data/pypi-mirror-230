import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import hashlib
import json
from typing import List, Tuple
from transformers import AutoTokenizer


def count_starting_phrase(df: pd.DataFrame, phrase: str, author: str = "user") -> int:
    """
    Count the number of messages by a specific author that start with a given phrase.

    Args:
        df (pd.DataFrame): The DataFrame containing the message data.
        phrase (str): The phrase to search for at the start of messages.
        author (str): The author to search messages from. Default is 'assistant'.

    Returns:
        int: The number of messages by the author that start with the given phrase.
    """
    user_messages = df[df["author"] == author]["content"]
    count = user_messages.str.startswith(phrase).sum()
    return count


def get_top_ngrams(
    df: pd.DataFrame, text_column: str, n: int, top_k: int, return_type: str = "list"
):
    """
    Get top K n-grams from a DataFrame's text column.

    Args:
        df (pd.DataFrame): The DataFrame containing the text data.
        text_column (str): The name of the column containing the text data.
        n (int): The length of the n-grams.
        top_k (int): The number of top n-grams to return.
        return_type (str): The type of object to return. Can be 'list', 'dataframe', or 'series'.

    Returns:
        The top K n-grams and their counts, either as a list of tuples, a DataFrame, or a Series.
    """
    vec = CountVectorizer(ngram_range=(n, n)).fit(df[text_column])
    bag_of_words = vec.transform(df[text_column])
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    top_ngrams = words_freq[:top_k]

    if return_type == "dataframe":
        return pd.DataFrame(top_ngrams, columns=["Ngram", "Count"])
    elif return_type == "series":
        return pd.Series(dict(top_ngrams), name="Count")
    else:
        return top_ngrams


def calculate_message_metrics(
    df: pd.DataFrame, time_column: str = "create_time"
) -> dict:
    """
    Calculate the average messages per day and the average time difference between messages.

    Args:
        df (pd.DataFrame): DataFrame containing the messages.
        time_column (str): The name of the column containing the timestamp of messages.

    Returns:
        dict: A dictionary containing the 'avg_messages_per_day' and 'avg_time_diff'.
    """

    # Safety check to make sure DataFrame and time_column exist
    if df is None or time_column not in df.columns:
        return {"avg_messages_per_day": None, "avg_time_diff": None}

    # Calculate the number of days between the first and last message
    days = (df[time_column].max() - df[time_column].min()).days

    # Calculate average messages per day
    if days == 0:  # To avoid division by zero
        avg_messages_per_day = len(df)
    else:
        avg_messages_per_day = len(df) / days

    # Calculate the time difference between each message and the next one
    df["time_diff"] = df[time_column].diff()

    # Calculate the average time difference between messages
    avg_time_diff = df["time_diff"].mean()

    return {
        "avg_messages_per_day": avg_messages_per_day,
        "avg_time_diff": avg_time_diff,
    }


def calculate_user_message_metrics(
    df: pd.DataFrame,
    user_author: str,
    time_column: str = "time",
    content_column: str = "content",
) -> dict:
    """
    Calculate various metrics related to messages sent by a specific user.

    Args:
        df (pd.DataFrame): DataFrame containing the messages.
        user_author (str): The author whose messages you want to analyze.
        time_column (str): The name of the column containing the timestamp of messages.
        content_column (str): The name of the column containing the content of messages.

    Returns:
        dict: A dictionary containing calculated metrics.
    """

    # Safety check to make sure DataFrame and necessary columns exist
    if df is None or time_column not in df.columns or content_column not in df.columns:
        return {}

    # Filter only user messages
    user_df = df[df["author"] == user_author].copy()

    # Calculate number of messages sent by user per day
    user_df["date"] = user_df[time_column].dt.date
    messages_per_user_per_day = user_df["date"].value_counts().mean()

    # Average number of messages sent by user per hour of the day
    user_df["hour"] = user_df[time_column].dt.hour
    messages_per_user_per_hour = user_df["hour"].value_counts().mean()

    # Average length of user's messages
    user_df["message_length"] = user_df[content_column].apply(len)
    avg_message_length_user = user_df["message_length"].mean()

    # Most frequent starting phrase in user's messages
    def get_starting_phrase(message, n=3):
        return " ".join(message.split()[:n])

    user_df["starting_phrase"] = user_df[content_column].apply(get_starting_phrase)
    most_common_starting_phrase = user_df["starting_phrase"].mode()[0]

    # Longest time period without a message from the user
    user_df["time_diff"] = user_df[time_column].diff()
    longest_silence_user = user_df["time_diff"].max()

    return {
        "messages_per_user_per_day": messages_per_user_per_day,
        "messages_per_user_per_hour": messages_per_user_per_hour,
        "avg_message_length_user": avg_message_length_user,
        "most_common_starting_phrase": most_common_starting_phrase,
        "longest_silence_user": longest_silence_user,
    }


def calculate_additional_user_metrics(
    df: pd.DataFrame,
    user_author: str,
    time_column: str = "time",
    content_column: str = "content",
) -> dict:
    """
    Calculate additional metrics related to messages sent by a specific user.

    Args:
        df (pd.DataFrame): DataFrame containing the messages.
        user_author (str): The author whose messages you want to analyze.
        time_column (str): The name of the column containing the timestamp of messages.
        content_column (str): The name of the column containing the content of messages.

    Returns:
        dict: A dictionary containing calculated metrics.
    """

    # Safety check to make sure DataFrame and necessary columns exist
    if df is None or time_column not in df.columns or content_column not in df.columns:
        return {}

    # Filter only user messages
    user_df = df[df["author"] == user_author].copy()

    # Calculate standard deviation of user's message lengths
    std_message_length_user = user_df["message_length"].std()

    # Find the most active day of the week for the user
    user_df["day_of_week"] = user_df[time_column].dt.day_name()
    most_active_day = user_df["day_of_week"].mode()[0]

    # Find the most active hour of the day for the user
    most_active_hour = user_df["hour"].mode()[0]

    # Find frequency of certain key words
    keywords = ["hello", "thanks", "please", "sorry", "help"]  # add your own keywords
    keyword_frequencies = {
        word: user_df[content_column].apply(lambda x: x.lower().count(word)).sum()
        for word in keywords
    }

    return {
        "std_message_length_user": std_message_length_user,
        "most_active_day": most_active_day,
        "most_active_hour": most_active_hour,
        "keyword_frequencies": keyword_frequencies,
    }


def plot_hourly_activity_heatmap(
    user_df: pd.DataFrame, time_column: str = "time", content_column: str = "content"
):
    """
    Generate a heat map showing user activity by hour and day of the week.

    Args:
        user_df (pd.DataFrame): DataFrame containing the messages of a specific user.
        time_column (str): The name of the column containing the timestamp of messages.
        content_column (str): The name of the column containing the content of messages.
    """
    pivot = (
        user_df.groupby(
            [user_df[time_column].dt.hour, user_df[time_column].dt.day_name()]
        )
        .count()[content_column]
        .unstack()
    )
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot, cmap="YlGnBu", linewidths=0.5)
    plt.title("Hourly activity heat map (days of the week)")
    plt.xlabel("Day of the week")
    plt.ylabel("Hour of the day")
    plt.show()


def plot_activity_over_time_and_by_hour(
    user_df: pd.DataFrame, time_column: str = "time", content_column: str = "content"
):
    """
    Generate time series and polar plots showing user activity.

    Args:
        user_df (pd.DataFrame): DataFrame containing the messages of a specific user.
        time_column (str): The name of the column containing the timestamp of messages.
        content_column (str): The name of the column containing the content of messages.
    """
    plt.figure(figsize=(10, 6))
    user_activity_trend = user_df.resample("D", on=time_column).count()[content_column]
    plt.plot(user_activity_trend.index, user_activity_trend.values, color="skyblue")
    plt.title("User activity over time")
    plt.xlabel("Time")
    plt.ylabel("Number of messages")
    plt.show()

    user_messages_by_hour = user_df.groupby(user_df[time_column].dt.hour)[
        content_column
    ].count()
    user_messages_by_hour = user_messages_by_hour / user_messages_by_hour.max()

    plt.figure(figsize=(20, 10))
    ax = plt.subplot(111, polar=True)
    ax.fill(np.linspace(0, 2 * np.pi, 24), user_messages_by_hour, color="skyblue")

    ax.set_yticklabels([])  # remove radial labels
    ax.set_xticks(np.linspace(0, 2 * np.pi, 24))  # 24 hour ticks
    ax.set_xticklabels(range(24))  # label with hours
    ax.set_theta_offset(
        np.pi / 2 - np.pi / 24
    )  # rotate plot to have midnight at top, and each bar centered on its hour

    plt.title("User Activity by Hour of Day")
    plt.show()


def display_top_words_by_cluster(user_messages, kmeans_labels, n_clusters=3, top_n=10):
    """
    Display the top words for each cluster based on their TF-IDF scores.

    Args:
        user_messages (array-like): List or array of messages by the user.
        kmeans_labels (array-like): List or array of KMeans cluster labels corresponding to each message.
        n_clusters (int): Number of clusters used in KMeans.
        top_n (int): Number of top words to display for each cluster.
    """
    # Compute tf-idf scores
    vectorizer = TfidfVectorizer(max_features=1000)
    tfidf_scores = vectorizer.fit_transform(user_messages)

    # Get feature names (words)
    feature_names = vectorizer.get_feature_names_out()

    # Get tf-idf scores for each cluster
    cluster_tfidf_scores = []
    for i in range(n_clusters):
        # Find messages in this cluster
        messages_in_cluster = tfidf_scores[np.array(kmeans_labels) == i]

        # Compute average tf-idf scores for these messages
        avg_tfidf_scores = np.mean(
            messages_in_cluster, axis=0
        ).A1  # Convert matrix to 1D array

        # Store the results
        cluster_tfidf_scores.append(avg_tfidf_scores)

    # Display the top words for each cluster
    for i in range(n_clusters):
        print(f"Cluster {i}:")

        # Get indices of top scores
        top_indices = np.argsort(cluster_tfidf_scores[i])[-top_n:]

        # Get corresponding words
        top_words = [feature_names[idx] for idx in reversed(top_indices)]

        print(top_words)


def visualize_message_clusters(message_coord_map, n_clusters=3):
    """
    Visualize clusters of messages in a 3D scatter plot.

    Args:
        message_coord_map (dict): A mapping from messages to additional information and coordinates.
        n_clusters (int): The number of clusters for KMeans.

    """
    # Prepare the data
    data = list(message_coord_map.values())
    messages = [d["message"] for d in data if d["author"] == "user"]
    coordinates = [d["coordinates"] for d in data if d["author"] == "user"]

    # Use PCA to reduce dimensionality
    pca = PCA(n_components=3)
    result = pca.fit_transform(coordinates)

    # Cluster the messages using KMeans
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(result)

    # Extract keywords from each cluster using TF-IDF
    vectorizer = TfidfVectorizer(max_df=0.5, min_df=2, stop_words="english")
    X = vectorizer.fit_transform(messages)
    words = vectorizer.get_feature_names_out()

    keywords = []
    for i in range(n_clusters):
        cluster_messages = X[kmeans.labels_ == i]
        avg_tfidf = cluster_messages.mean(axis=0)
        keyword = words[avg_tfidf.argmax()]
        keywords.append(keyword)

    # Create traces
    traces = []
    for i in range(n_clusters):
        points = result[kmeans.labels_ == i]
        trace = go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode="markers",
            marker=dict(size=5, opacity=0.8),
            name=f"Cluster {i}",
        )
        traces.append(trace)

    # Define layout
    layout = go.Layout(
        title="3D Scatter plot of user messages",
        scene=dict(
            xaxis=dict(title="PC1"), yaxis=dict(title="PC2"), zaxis=dict(title="PC3")
        ),
        annotations=[
            dict(
                showarrow=False,
                x=points[:, 0].mean(),
                y=points[:, 1].mean(),
                z=points[:, 2].mean(),
                text=keywords[i],
                xanchor="left",
                xshift=10,
                opacity=0.7,
            )
            for i, points in enumerate(
                [result[kmeans.labels_ == j] for j in range(n_clusters)]
            )
        ],
    )

    # Create and show the plot
    fig = go.Figure(data=traces, layout=layout)
    fig.show()


def hash_dict(d):
    """Hashes a dictionary using SHA-256 and returns the hexadecimal digest."""
    d_str = json.dumps(d, sort_keys=True)
    return hashlib.sha256(d_str.encode()).hexdigest()


def add_token_info_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Initialize empty lists for the new columns
    df["token_ids"] = [[] for _ in range(len(df))]
    df["tokens"] = [[] for _ in range(len(df))]
    df["token_count"] = [0 for _ in range(len(df))]

    # Iterate over each row and fill in the new columns
    for idx, row in df.iterrows():
        metadata = row["metadata"]
        all_token_ids = []
        all_tokens = []
        total_token_count = 0

        # Create a copy of metadata dictionary for storing hashed values
        hashed_metadata = {}

        # Loop through each ID in the metadata dictionary
        for message_id, meta_dict in metadata.items():
            all_token_ids.extend(meta_dict.get("token_ids", []))
            all_tokens.extend(meta_dict.get("tokens", []))
            total_token_count += meta_dict.get("token_count", 0)

            hashed_key = hash_dict(meta_dict)
            hashed_metadata[hashed_key] = message_id

        df.at[idx, "metadata"] = hashed_metadata
        df.at[idx, "token_ids"] = all_token_ids
        df.at[idx, "tokens"] = all_tokens
        df.at[idx, "token_count"] = total_token_count

    return df


def compute_and_combine(
    main_dfs: List[pd.DataFrame],
) -> Tuple[float, float, pd.DataFrame]:
    combined_df = pd.concat(main_dfs, ignore_index=True)

    total_sum = 0
    total_count = 0
    for df in main_dfs:
        n_neighbors_sum = df["n_neighbors"].sum()

        total_sum += float(n_neighbors_sum)
        total_count += len(df)

    mean_neighbors = total_sum / total_count if total_count != 0 else 0.0

    return mean_neighbors, combined_df
