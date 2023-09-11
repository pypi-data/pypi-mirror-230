from concurrent.futures import ThreadPoolExecutor
import json
from dlm_matrix.infrence.generator import PromptGenerator
import json
import random
from prompt_toolkit.completion import WordCompleter
import os


class StoryChat(PromptGenerator):
    def init_game_realms(self):
        self.realms = {
            "A": "Real World",
            "B": "Fantasy Land",
            "C": "Sci-Fi City",
            "D": "Mystery Island",
            "E": "Adventure",
        }
        self.realm_rules = {
            "B": "You can use magic",
            "C": "You must solve a tech puzzle",
            "D": "Find the hidden treasure",
            "E": "Complete daring tasks",
        }
        self.realm_inventory = {key: [] for key in self.realms.keys()}
        self.realm_tasks = {key: [] for key in self.realms.keys()}
        self.realm_stories = {key: [] for key in self.realms.keys()}

    def get_realm_event(self, realm):
        events = {
            "A": ["You find a $10 bill on the street.", "A friend calls you."],
            "B": ["A dragon appears.", "You find a magic wand."],
            "C": ["Your spacecraft malfunctions.", "You discover an AI rebellion."],
            "D": ["You find a treasure map.", "You encounter a wild animal."],
            "E": [
                "You stumble upon a hidden cave.",
                "You find a backpack filled with supplies.",
                "A fast river blocks your path.",
            ],
        }
        return random.choice(events[realm])

    def run_prompt(self, prompt: str = ""):
        self.init_game_realms()
        conversation_id = self.conversation_manager.start_conversation(prompt)
        saved_messages = []

        while True:
            message_data = {}
            user_message = self.session.session.prompt(
                completer=WordCompleter(["quit", "restart"], ignore_case=True)
            )

            print("\n")
            # Command Handling
            if user_message.startswith("/"):
                response = self.handle_command(
                    user_message.strip().lower(), conversation_id
                )

                if user_message == "/quit":
                    filename = input("Enter a filename to save the conversation: ")
                    save_message_to_json(saved_messages, filename + ".json")
                    print(
                        f"Saved all messages to {filename}.json in a structured format."
                    )
                    print(response)
                    break

                print(response)
                print("\n\n")  # New line after the command's response
                continue

            last_message_id = self.conversation_manager.get_conversation(
                conversation_id
            ).get_last_message_id()
            executor = ThreadPoolExecutor(max_workers=4)

            future_A = executor.submit(
                self.generate_prompt_task,
                prompt=user_message,
            )

            future_B = executor.submit(self.generate_prompt_task, future_A.result()[0])
            future_C = executor.submit(self.generate_prompt_task, future_B.result()[0])
            future_D = executor.submit(self.generate_prompt_task, future_C.result()[0])
            future_E = executor.submit(
                self.generate_prompt_task,
                prompt=future_D.result()[0],
                response=future_C.result()[0],
            )

            message_data["A"] = future_A.result()
            message_data["B"] = future_B.result()
            message_data["C"] = future_C.result()
            message_data["D"] = future_D.result()
            message_data["E"] = future_E.result()

            event_B = executor.submit(self.get_realm_event, "B")
            event_C = executor.submit(self.get_realm_event, "C")
            event_D = executor.submit(self.get_realm_event, "D")
            event_E = executor.submit(self.get_realm_event, "E")

            # Save messages
            saved_messages.append(message_data)

            self.conversation_manager.handle_user_input(
                conversation_id, message_data["A"], last_message_id
            )
            self.conversation_manager.handle_agent_response(
                conversation_id, message_data["B"], last_message_id
            )

            self.conversation_manager.handle_user_input(
                conversation_id, message_data["C"], last_message_id
            )

            self.conversation_manager.handle_agent_response(
                conversation_id, message_data["D"], last_message_id
            )

            self.conversation_manager.handle_user_input(
                conversation_id, message_data["E"], last_message_id
            )
            # Save inventory
            for realm, message in message_data.items():
                if "You have" in message:
                    item = message.split("You have")[1].split(".")[0].strip()
                    self.realm_inventory[realm].append(item)

            # Save tasks
            for realm, message in message_data.items():
                if "You must" in message:
                    task = message.split("You must")[1].split(".")[0].strip()
                    self.realm_tasks[realm].append(task)

            # Save stories
            for realm, message in message_data.items():
                if "You are in" in message:
                    story = message.split("You are in")[1].split(".")[0].strip()
                    self.realm_stories[realm].append(story)

            # Display the conversation and events
            print(f"A (Real World): {future_A.result()}")
            print(f"Event in B: {event_B.result()}")
            print(f"B (Fantasy Land): {future_B.result()}")
            print(f"Event in C: {event_C.result()}")
            print(f"C (Sci-Fi City): {future_C.result()}")
            print(f"Event in D: {event_D.result()}")
            print(f"D (Mystery Island): {future_D.result()}")
            print(f"Event in E: {event_E.result()}")
            print(f"E (Adventure): {future_E.result()}")

            # Task check
            for realm, task in self.realm_tasks.items():
                if task:
                    print(f"Pending task in {self.realms[realm]}: {task}")

            print("\n\nRealm Stories:")
            for point, stories in self.realm_stories.items():
                print(f"{self.realms[point]}: {', '.join(stories)}")

            print("\n\nRealm Inventory:")
            for point, items in self.realm_inventory.items():
                print(f"{self.realms[point]}: {', '.join(items)}")

            print("\n\nRealm Tasks:")
            for point, tasks in self.realm_tasks.items():
                print(f"{self.realms[point]}: {', '.join(tasks)}")

            print("\n\n")  # Ensure there's a new line after user input


def save_message_to_json(message_data, json_file_path: str):
    # Create the folder if it doesn't exist
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
