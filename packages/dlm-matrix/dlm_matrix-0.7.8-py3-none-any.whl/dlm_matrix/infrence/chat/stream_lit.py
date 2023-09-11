import time
from dlm_matrix.infrence.generator import PromptGenerator
import streamlit as st


class SynergyChat(PromptGenerator):
    def save_conversation(self, conversation_id: str, title: str = "Untitled"):
        conversation = self.conversation_manager.get_conversation(conversation_id)

        # Save the conversation in the session state
        st.session_state.saved_conversations[title] = "\n".join(
            conversation.get_messages()
        )

        conversation.save_conversation(title)  # As

    def run_prompt(
        self,
        initial_prompt: str = "",
    ):
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

        if "saved_conversations" not in st.session_state:
            st.session_state.saved_conversations = {}

        conversation_id = self.conversation_manager.start_conversation(initial_prompt)
        agent_response = None  # Initially, there's no agent response

        st.title("Symphony of Synthesis")

        sidebar = st.sidebar
        sidebar.title("Conversations")
        saved_conversation_title = sidebar.selectbox(
            "Select a saved conversation",
            [""] + list(st.session_state.saved_conversations.keys()),
        )

        if saved_conversation_title:
            loaded_conversation = self.load_conversation(saved_conversation_title)
            st.session_state.conversation_history.append(
                (f"AI: {loaded_conversation}", "ai")
            )

        if "user_input_key" not in st.session_state:
            st.session_state.user_input_key = ""

        chat_col, control_col = st.columns([3, 2])

        with chat_col:
            user_input = st.text_input("Your Message:", key="user_input_key")

            if st.button("Send"):
                st.session_state.conversation_history.append(
                    (f"You: {user_input}", "user")
                )

                # Clear the user_input in session_state for next input
                st.session_state.user_input = ""

                # AI Typing Indicator
                typing_indicator = st.empty()
                for _ in range(3):
                    typing_indicator.text("AI is typing...")
                    time.sleep(0.4)
                    typing_indicator.text("")
                    time.sleep(0.2)
                typing_indicator.empty()

                # Command Handling
                if user_input.startswith("/"):
                    response = self.handle_command(
                        user_input.strip().lower(), conversation_id
                    )
                    st.session_state.conversation_history.append(
                        (f"AI: {response}", "ai")
                    )

                    if user_input.strip().lower() == "/restart":
                        self.conversation_manager.end_conversation(conversation_id)
                        conversation_id = self.conversation_manager.start_conversation()
                        agent_response = None
                    return

                if user_input.strip().lower() == "quit":
                    st.write("Thank you for using the system. Goodbye!")
                    return

                use_process_conversations_flag = True if not agent_response else False

                try:
                    last_message_id = self.conversation_manager.get_conversation(
                        conversation_id
                    ).get_last_message_id()

                    prompt_parts = self.generate_prompt_task(
                        prompt=user_input,
                        response=agent_response,
                        use_process_conversations=use_process_conversations_flag,
                        custom_conversation_data=None,
                    )
                    agent_prompt = prompt_parts
                    agent_response = agent_prompt

                    self.conversation_manager.handle_user_input(
                        conversation_id, user_input, last_message_id
                    )

                    agent_prompt = "\n\n".join(agent_prompt)

                    self.conversation_manager.handle_agent_response(
                        conversation_id, agent_prompt, last_message_id
                    )

                    # agent_prompt = self.get_raw_response(agent_prompt)
                    st.session_state.conversation_history.append(
                        (f"AI: {agent_prompt}", "ai")
                    )

                except Exception as e:
                    st.error(f"An error occurred: {e}. Please try again.")

        with control_col:
            st.subheader("Controls")

            if st.button("Restart Conversation"):
                response = self.handle_command("/restart", conversation_id)
                st.session_state.conversation_history.append((f"AI: {response}", "ai"))

            save_title = st.text_input("Save title:", "Untitled")
            if st.button("Save Conversation"):
                command = f"/save {save_title}"
                response = self.handle_command(command, conversation_id)
                st.session_state.conversation_history.append((f"AI: {response}", "ai"))

            if st.button("View History"):
                response = self.handle_command("/history", conversation_id)
                st.session_state.conversation_history.append((f"AI: {response}", "ai"))

        sidebar.subheader("Conversation History")
        history_expander = sidebar.expander("Show/Hide History")
        with history_expander:
            for message, msg_type in st.session_state.conversation_history:
                if msg_type == "user":
                    sidebar.markdown(
                        f"""
                        <div style='background-color:#F0F0F0;
                                    padding:5px;
                                    border-radius:5px;
                                    margin-bottom:5px;
                                    border: 1px solid #B0B0B0;
                                    box-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);'>
                            <span style='color:black;'>{message}</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                elif msg_type == "ai":
                    sidebar.markdown(
                        f"""
                        <div style='background-color:#DFF2E1;
                                    padding:5px;
                                    border-radius:5px;
                                    margin-bottom:5px;
                                    border: 1px solid #B7E4C7;
                                    box-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);'>
                            <span style='color:black;'>{message}</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                elif msg_type == "rating":
                    sidebar.markdown(
                        f"""
                        <div style='background-color:#FFF9E0;
                                    padding:5px;
                                    border-radius:5px;
                                    margin-bottom:5px;
                                    border: 1px solid #FFEAB5;
                                    box-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);'>
                            <span style='color:black;'>{message}</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    sidebar.write(message)

        self.conversation_manager.end_conversation(conversation_id)
