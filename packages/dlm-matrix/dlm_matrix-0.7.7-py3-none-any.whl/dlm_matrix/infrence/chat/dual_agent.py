import streamlit as st
from dlm_matrix.infrence.parallel import SynergyParrallel
import datetime
import threading
import time
from typing import Union, List, Dict, Optional, Any
import matplotlib.pyplot as plt
import json
import os


class SynergyChat(SynergyParrallel):
    @staticmethod
    def load_saved_conversations(json_file_path: str):
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as file:
                return json.load(file)
        return {}

    @staticmethod
    def save_conversation_to_json(conversation_data, title: str, json_file_path: str):
        existing_conversations = {}
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as file:
                existing_conversations = json.load(file)
        existing_conversations[title] = conversation_data
        with open(json_file_path, "w") as file:
            json.dump(existing_conversations, file, indent=4)

    def adjust_temperature_based_on_feedback(self, rating: int) -> str:
        message = ""

        # Adjust temperature based on feedback
        if rating in [1, 2]:
            self.chat.temperature = min(1.0, self.chat.temperature + 0.05)
            message = (
                "Increased randomness to explore more varied answers."
                " This might help get better or different insights!"
            )
        elif rating in [4, 5]:
            self.chat.temperature = max(0.2, self.chat.temperature - 0.05)
            message = (
                "Decreased randomness for more deterministic answers."
                " This provides consistent and targeted answers!"
            )

        return message

    def plot_temperature_history(self, history):
        plt.figure(figsize=(10, 4))
        plt.plot(history, marker="o")
        plt.title("Temperature History")
        plt.xlabel("Feedback Entries")
        plt.ylabel("Temperature")
        plt.ylim(0, 1)
        st.pyplot(plt)

    def handle_command(
        self, command: str, conversation_id1: str, conversation_id2: str
    ):
        if command.startswith("/save"):
            title = st.text_input("Give this conversation a title:", key="convo_title")
            if title:
                try:
                    self.save_conversation_to_json(
                        {
                            "agent1": st.session_state.agent1_conversation_history,
                            "agent2": st.session_state.agent2_conversation_history,
                        },
                        title,
                        "saved_conversations.json",
                    )
                    return "Conversation saved successfully with title: " + title
                except Exception as e:
                    return f"Error saving conversation: {e}"
            else:
                return "Please provide a title. Use /save <title>."

        elif command == "/restart":
            st.session_state.agent1_conversation_history = []
            st.session_state.agent2_conversation_history = []
            self.conversation_manager.end_conversation(conversation_id1)
            self.conversation_manager.end_conversation(conversation_id2)
            return "Conversations for both agents restarted!"

        elif command == "/help":
            return "Type your message to continue the conversation. Use '/quit' to exit, '/restart' to restart the conversation, '/history' to view past messages."

        elif command == "/history":
            history1 = "\n".join(
                self.conversation_manager.get_conversation(
                    conversation_id1
                ).get_messages()
            )
            history2 = "\n".join(
                self.conversation_manager.get_conversation(
                    conversation_id2
                ).get_messages()
            )
            return f"Agent 1 History:\n{history1}\n\nAgent 2 History:\n{history2}"

        else:
            return "Unknown command. Type '/help' for a list of commands."

    @staticmethod
    def styled_text(text, user_type="user"):
        if user_type == "user":
            return f"""
            <div style='text-align:right; 
                        padding:12px; 
                        margin:5px; 
                        border-radius:8px; 
                        background: linear-gradient(160deg, #4A90E2, #444); 
                        color: white; 
                        box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
                        font-family: Arial, sans-serif; 
                        font-size: 14px;'>
                {text}
            </div>
            """
        else:  # AI response
            return f"""
            <div style='text-align:left; 
                        padding:12px; 
                        margin:5px; 
                        border-radius:8px; 
                        background: linear-gradient(160deg, #FF6B6B, #555); 
                        color: white; 
                        box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
                        font-family: Arial, sans-serif; 
                        font-size: 14px;'>
                {text}
            </div>
            """

    def get_conversation_id(self, conversation_id: Union[str, List[str]]):
        if isinstance(conversation_id, str):
            return self.conversation_manager.get_conversation(
                conversation_id
            ).get_last_message_id()
        elif isinstance(conversation_id, list):
            return [
                self.conversation_manager.get_conversation(c_id).get_last_message_id()
                for c_id in conversation_id
            ]

    @staticmethod
    def typing_indicator():
        typing_indicator = st.empty()
        for _ in range(3):
            typing_indicator.text("AI is typing...")
            time.sleep(0.4)
            typing_indicator.text("")
            time.sleep(0.2)
        typing_indicator.empty()

    @staticmethod
    def current_timestamp():
        return datetime.datetime.now().strftime("%H:%M:%S")

    def initialize_conversation_ui(self):
        # Load the saved conversations from JSON
        saved_conversations = self.load_saved_conversations("saved_conversations.json")

        # Initialize or set agent conversation histories
        if "agent1_conversation_history" not in st.session_state:
            st.session_state.agent1_conversation_history = saved_conversations.get(
                "agent1", []
            )
        if "agent2_conversation_history" not in st.session_state:
            st.session_state.agent2_conversation_history = saved_conversations.get(
                "agent2", []
            )

        # Initialize temperature histories if not already initialized
        if "temp_history_agent1" not in st.session_state:
            st.session_state.temp_history_agent1 = [self.chat.temperature]
        if "temp_history_agent2" not in st.session_state:
            st.session_state.temp_history_agent2 = [self.chat.temperature]

        # Dropdown to select and load a saved conversation
        if saved_conversations:
            selected_saved_convo = st.selectbox(
                "Select a saved conversation to load",
                ["None"] + list(saved_conversations.keys()),
            )
            if selected_saved_convo and selected_saved_convo != "None":
                st.session_state.agent1_conversation_history = saved_conversations[
                    selected_saved_convo
                ]["agent1"]
                st.session_state.agent2_conversation_history = saved_conversations[
                    selected_saved_convo
                ]["agent2"]

        # Start new conversations
        conversation_id1 = self.conversation_manager.start_conversation("")
        conversation_id2 = self.conversation_manager.start_conversation("")

        return conversation_id1, conversation_id2

    def _prepare_generate_parallel_params(
        self,
        user_input: str,
        use_process_conversations: bool = False,
        custom_conversation_data: Optional[List[Dict[str, str]]] = None,
        num_prompts: int = 1,
        max_workers: int = 2,
        batch_size: int = 1,
    ) -> Dict[str, Any]:
        """
        Prepares the parameters required for the generate_parallel method.

        Parameters:
        - user_input (str): The user's input message.
        - use_process_conversations (bool, optional): Flag to determine if conversations should be processed. Default is False.
        - custom_conversation_data (Optional[List[Dict[str, str]]]): Optional custom data for the conversation.
        - num_prompts (int, optional): Number of prompts for parallel generation. Defaults to 1.
        - max_workers (int, optional): Maximum number of worker threads for parallel generation. Defaults to 4.
        - batch_size (int, optional): Size of batches for generation. Defaults to 1.

        Returns:
        - Dict[str, Any]: A dictionary containing parameters for the generate_parallel method.

        Raises:
        - ValueError: If any of the integer parameters are non-positive.
        """

        for val, param_name in [
            (num_prompts, "num_prompts"),
            (max_workers, "max_workers"),
            (batch_size, "batch_size"),
        ]:
            if val <= 0:
                raise ValueError(f"{param_name} should be a positive integer.")

        if custom_conversation_data and not isinstance(custom_conversation_data, list):
            raise ValueError(
                "custom_conversation_data should be a list of dictionaries."
            )

        return {
            "num_prompts": num_prompts,
            "max_workers": max_workers,
            "batch_size": batch_size,
            "example_pairs": [(user_input, user_input)],
            "use_process_conversations": use_process_conversations,
            "custom_conversation_data": custom_conversation_data,
        }

    def get_agent_response(
        self, conversation_id: str, user_input: str, **kwargs
    ) -> str:
        """
        Generates and returns an agent's response based on the provided user input.

        Parameters:
        - conversation_id (str): The ID associated with the ongoing conversation.
        - user_input (str): The user's input message.
        - **kwargs: Additional parameters for the _prepare_generate_parallel_params method.

        Returns:
        - str: The generated agent response.

        Raises:
        - ValueError: If invalid data is provided.
        """

        params = self._prepare_generate_parallel_params(user_input, **kwargs)
        agent_response = self.generate_parallel(**params)

        self.conversation_manager.handle_agent_response(
            conversation_id,
            agent_response[0],
            self.get_conversation_id(conversation_id),
        )
        return agent_response

    def threaded_agent_response(
        self,
        idx: int,
        conversation_id: str,
        user_input: str,
        responses_list: List[str],
        **kwargs,
    ) -> None:
        """
        Handles agent's response generation in a threaded manner.

        Parameters:
        - idx (int): The index position in the responses_list where the agent's response should be stored.
        - conversation_id (str): The ID associated with the ongoing conversation.
        - user_input (str): The user's input message.
        - responses_list (List[str]): A list to store the agent responses.
        - **kwargs: Additional parameters for the get_agent_response method.

        Returns:
        - None

        Raises:
        - ValueError: If invalid data is provided.
        """

        agent_response = self.get_agent_response(conversation_id, user_input, **kwargs)
        responses_list[idx] = agent_response

    def run_prompt(self, **kwargs):
        # Initialize the Streamlit UI and load saved conversations
        st.set_page_config(layout="wide")

        conversation_id1, conversation_id2 = self.initialize_conversation_ui()

        timestamp = self.current_timestamp()
        agent1_col, chat_col, agent2_col = st.columns([4, 3, 4])
        responses = [None, None]
        threads = []

        use_process_conversations_flag = (
            True if not responses[0] and not responses[1] else False
        )

        with chat_col:
            st.markdown(
                """
                <style>
                    .centered {
                        display: flex;
                        justify-content: center;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <style>
                    .centered {
                        text-align: center;
                    }
                    .conversation-background {
                        background: linear-gradient(135deg, #E1FFE1, #FFEBCC);
                        border-radius: 8px;
                        padding: 15px;
                        box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
                    }
                    .title-inline {
                        display: inline-block;
                        font-size: 2rem;
                        font-weight: 600;
                        margin-bottom: 1rem;
                        color: #5A9;
                    }
                    .message {
                        border: 1px solid #EEE;
                        padding: 0.5rem;
                        margin: 0.5rem 0;
                        border-radius: 8px;
                    }
                    .user {
                        background-color: #E1FFE1;
                    }
                    .ai {
                        background-color: #FFEBCC;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                "<div class='centered title-inline'>Symphony of Synthesis</div>",
                unsafe_allow_html=True,
            )

            user_input = st.text_input(
                "Your Message:",
                value=st.session_state.get("user_input_key", ""),
                key="user_input_key",
                on_change=lambda: setattr(st.session_state, "user_input_key", ""),
            )

            if st.button("Send"):
                # Update the UI with user's message
                st.session_state.agent1_conversation_history.append(
                    self.styled_text(f"{timestamp} - You: {user_input}", "user")
                )
                st.session_state.agent2_conversation_history.append(
                    self.styled_text(f"{timestamp} - You: {user_input}", "user")
                )

                # Handle Command
                if user_input.startswith("/"):
                    response = self.handle_command(
                        user_input.strip().lower(), conversation_id1, conversation_id2
                    )
                    st.info(response)

                # Add user input to conversations
                self.conversation_manager.handle_user_input(
                    conversation_id1,
                    user_input,
                    self.get_conversation_id([conversation_id1, conversation_id2]),
                )

                # Start threads for agent responses
                threads = []
                for idx, convo_id in enumerate([conversation_id1, conversation_id2]):
                    t = threading.Thread(
                        target=self.threaded_agent_response,
                        args=(
                            idx,
                            convo_id,
                            user_input,
                            responses,
                        ),
                        kwargs={
                            "use_process_conversations": use_process_conversations_flag,
                            **kwargs,
                        },
                    )
                    threads.append(t)
                    t.start()

                for thread in threads:
                    thread.join()

                # Update the UI with agent responses
                agent_response_1 = responses[0][0]
                agent_response_2 = responses[1][0]

                agent_1 = "\n\n".join(agent_response_1)
                agent_2 = "\n\n".join(agent_response_2)

                st.session_state.agent1_conversation_history.append(
                    self.styled_text(f"{agent_1}", "ai")
                )
                st.session_state.agent2_conversation_history.append(
                    self.styled_text(f"{agent_2}", "ai")
                )

                self.conversation_manager.handle_agent_response(
                    conversation_id1,
                    agent_response_1,
                    self.get_conversation_id(conversation_id1),
                )

                self.conversation_manager.handle_agent_response(
                    conversation_id2,
                    agent_response_2,
                    self.get_conversation_id(conversation_id2),
                )

        # Function to render a message with a bubble-like appearance
        def render_message_bubble(message, speaker):
            return f"""<div style="border: 1px solid #EEE; padding: 0.5rem; margin: 0.5rem 0; border-radius: 15px;"> {message}</div>"""

        sidebar = st.sidebar

        # Styling the sidebar
        sidebar.markdown(
            """
            <style>
                .sidebar .sidebar-content {
                    background: linear-gradient(160deg, #FF6B6B, #555);
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
                    font-family: Arial, sans-serif;  /* Using a common font, but you can add your preferred one */
                }
                
                .stButton>button {
                    border-radius: 20px;
                    border: none;
                    background-color: linear-gradient(160deg, #FF6B6B, #555);;
                    color: white;
                    font-size: 15px;
                    padding: 8px 20px;
                    margin-top: 5px;
                    transition: background-color 0.3s;
                }

                .stButton>button:hover {
                    background-color: linear-gradient(160deg, #FF6B6B, #555);
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        sidebar.title("Options")

        # Save conversations inside sidebar
        if sidebar.button("Save Conversation"):
            title = sidebar.text_input(
                "Give this conversation a title:", key="convo_title"
            )
            if title:
                try:
                    self.save_conversation_to_json(
                        {
                            "agent1": st.session_state.agent1_conversation_history,
                            "agent2": st.session_state.agent2_conversation_history,
                        },
                        title,
                        "saved_conversations.json",
                    )
                    sidebar.info("Conversation saved successfully with title: " + title)
                except Exception as e:
                    sidebar.error(f"Error saving conversation: {e}")
            else:
                sidebar.warning("Please provide a title. Use /save <title>.")

        # Restart conversations inside sidebar
        if sidebar.button("Restart Conversations"):
            st.session_state.agent1_conversation_history = []
            st.session_state.agent2_conversation_history = []
            self.conversation_manager.end_conversation(conversation_id1)
            self.conversation_manager.end_conversation(conversation_id2)
            sidebar.info("Conversations for both agents restarted!")

        # Merge conversations inside sidebar
        if sidebar.button("Merge Conversations"):
            try:
                self.conversation_manager.merge_conversations(
                    conversation_id1, conversation_id2
                )
                sidebar.info("Conversations merged successfully!")
            except Exception as e:
                sidebar.error(f"Error merging conversations: {e}")

        # Expandable conversation logs
        if sidebar.button("Expand Older Messages"):
            show_all = True
        else:
            show_all = False

        if not show_all:
            num_messages_to_show = 1

        # Display Agent 1's conversation history
        with agent1_col:
            messages_to_display = (
                st.session_state.agent1_conversation_history[-num_messages_to_show:]
                if num_messages_to_show is not None
                else st.session_state.agent1_conversation_history
            )
            for message_html in reversed(messages_to_display):
                st.markdown(
                    render_message_bubble(
                        message_html, "ai" if "Agent" in message_html else "user"
                    ),
                    unsafe_allow_html=True,
                )

            # Feedback System for Agent 1
            rating1 = st.slider("Rate Agent 1's response:", 1, 5, key="rating1_slider")

            if st.button("Submit Feedback for Agent 1"):
                adjustment_message = self.adjust_temperature_based_on_feedback(rating1)
                st.session_state.temp_history_agent1.append(self.chat.temperature)
                self.plot_temperature_history(st.session_state.temp_history_agent1)

                st.success(
                    f"Rating for Agent 1: {rating1}. "
                    f"Adjusted temperature to: {self.chat.temperature:.2f}. {adjustment_message}"
                )

        # Display Agent 2's conversation history
        with agent2_col:
            messages_to_display = (
                st.session_state.agent2_conversation_history[-num_messages_to_show:]
                if num_messages_to_show is not None
                else st.session_state.agent2_conversation_history
            )
            for message_html in reversed(messages_to_display):
                st.markdown(
                    render_message_bubble(
                        message_html, "ai" if "Agent" in message_html else "user"
                    ),
                    unsafe_allow_html=True,
                )
            # Feedback System for Agent 2
            rating2 = st.slider("Rate Agent 2's response:", 1, 5, key="rating2_slider")

            if st.button("Submit Feedback for Agent 2"):
                adjustment_message = self.adjust_temperature_based_on_feedback(rating2)

                st.session_state.temp_history_agent2.append(self.chat.temperature)
                self.plot_temperature_history(st.session_state.temp_history_agent2)

                st.success(
                    f"Rating for Agent 2: {rating2}. "
                    f"Adjusted temperature to: {self.chat.temperature:.2f}. {adjustment_message}"
                )
