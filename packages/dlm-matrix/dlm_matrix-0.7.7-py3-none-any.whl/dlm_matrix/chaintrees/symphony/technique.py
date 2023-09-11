from typing import Optional, List, Iterator, Dict, Any
from dlm_matrix.models import Content
from dlm_matrix.transformation.coordinate import Coordinate
from dlm_matrix.chaintrees.interface import ChainBuilder
import random
from .manager import SynthesisTechniqueManager
import re


class SynthesisTechniqueDirector:
    def __init__(
        self,
        builder: ChainBuilder,
        technique_manager: SynthesisTechniqueManager,
        technique_name: str,
        max_depth: int = 5,
        recursion_depth: int = 3,
        novelty_threshold: float = 0.25,
    ):
        if not isinstance(builder, ChainBuilder):
            raise ValueError("The builder must be an instance of ChainBuilder.")

        self.builder = builder
        self.technique_manager = technique_manager
        self.max_depth = max_depth
        self.novelty_threshold = novelty_threshold
        self.recursion_depth = recursion_depth
        self.conversation_history = ""
        self.last_prompt = None
        self.last_option = None
        self.last_dynamic_prompt = None

        self.set_technique(technique_name)

    def set_technique(self, technique_name: str) -> None:
        self.technique = self.technique_manager.create_synthesis_technique(
            technique_name
        )
        self.prompts_cycle = self._create_cycle(list(self.technique.prompts.keys()))

    def _create_cycle(self, items: List[str]) -> Iterator[str]:
        """Create a non-repeating, cyclic iterator over the given items."""
        while True:
            random.shuffle(items)
            for item in items:
                yield item

    def _build_synthesis(self, coordinate: Optional[Coordinate] = None):
        if coordinate is None:
            coordinate = Coordinate(x=0, y=0, z=0, t=4)

        # Get the list of prompts
        prompts = list(self.technique.prompts.keys())

        # Shuffle the prompts to ensure randomization
        random.shuffle(prompts)

        selected_prompt = None
        selected_option = None
        selected_dynamic_prompt = None

        # Find the first non-repeating prompt
        for prompt in prompts:
            if prompt != self.last_prompt:
                selected_prompt = prompt
                break

        self.last_prompt = selected_prompt

        if not self.technique.prompts[selected_prompt]:
            return

        # Get the branching options and dynamic prompts for the selected prompt
        branching_options = self.technique.prompts[selected_prompt]["branching_options"]
        dynamic_prompts = self.technique.prompts[selected_prompt]["dynamic_prompts"]

        # Shuffle the branching options and dynamic prompts to ensure randomization
        random.shuffle(branching_options)
        random.shuffle(dynamic_prompts)

        # Find the first non-repeating branching option
        for option in branching_options:
            if option != self.last_option:
                selected_option = option
                break

        self.last_option = selected_option

        # Find the first non-repeating dynamic prompt
        for dynamic_prompt in dynamic_prompts:
            if dynamic_prompt != self.last_dynamic_prompt:
                selected_dynamic_prompt = dynamic_prompt
                break

        self.last_dynamic_prompt = selected_dynamic_prompt

        extended_prompt = self._generate_prompt(
            selected_prompt, selected_option, selected_dynamic_prompt
        )

        pre_amble = f"Epithet of {self.technique.name}: {self.technique.epithet} "

        combined_content = pre_amble + extended_prompt

        content = Content(text=combined_content)

        self.builder.build_system_chain(content=content, coordinate=coordinate)

        new_message = extended_prompt

        if (
            self._compute_novelty_factor(new_message, self.conversation_history)
            < self.novelty_threshold
        ):
            return self._fallback()

        self.conversation_history += new_message

        return self.technique.epithet

    def _generate_prompt(
        self, prompt: str, selected_option: str, selected_dynamic_prompt: str
    ) -> str:
        prompt_data = self.technique.prompts[prompt]
        prompt_template = prompt_data.get("template")
        option_placeholder = "{option}"
        dynamic_prompt_placeholder = "{dynamic_prompt}"

        if prompt_template:
            # Replace placeholders in the template with the selected option and dynamic prompt
            prompt_text = prompt_template.replace(option_placeholder, selected_option)
            prompt_text = prompt_text.replace(
                dynamic_prompt_placeholder, selected_dynamic_prompt
            )

            # Capitalize the prompt text
            prompt_text = prompt_text.capitalize()
        else:
            # If a template is not provided, fallback to a default prompt construction
            prompt_text = f"{selected_option} {selected_dynamic_prompt}"

        # Combine the prompt text with the prompt name
        extended_prompt = f"{prompt} - {prompt_text}"

        # Remove extra whitespace and capitalize the prompt name and dynamic prompt
        extended_prompt = re.sub(r"\s+", " ", extended_prompt).strip()
        prompt_name, _, dynamic_prompt = extended_prompt.partition(" - ")
        dynamic_prompt = dynamic_prompt.capitalize()
        extended_prompt = f"{prompt_name} - {dynamic_prompt}"

        # Add an exclamation mark at the end of the prompt for emphasis
        extended_prompt += "!"

        # Highlight the selected option using asterisks
        highlighted_prompt = re.sub(
            re.escape(selected_option),
            lambda match: f"*{match.group(0)}*",
            extended_prompt,
            flags=re.IGNORECASE,
        )

        return highlighted_prompt

    def _fallback(self):
        current_technique_index = (
            self.technique_manager.get_synthesis_technique_names().index(
                self.technique.technique_name
            )
        )
        new_technique_index = (current_technique_index + 1) % len(
            self.technique_manager.get_synthesis_technique_names()
        )
        new_technique_name = self.technique_manager.get_synthesis_technique_names()[
            new_technique_index
        ]

        self.set_technique(new_technique_name)

        # Reset the state of the technique and prompt history for the new technique
        self.last_prompt = None
        self.last_option = None
        self.last_dynamic_prompt = None

    def _compute_novelty_factor(self, message: str, conversation_history: str) -> float:
        message_words = set(message.lower().split())
        history_words = set(conversation_history.lower().split())
        common_words = message_words.intersection(history_words)

        if len(message_words) == 0 and len(history_words) == 0:
            return 0.0

        sorensen_dice_coefficient = (2 * len(common_words)) / (
            len(message_words) + len(history_words)
        )
        novelty_factor = 1 - sorensen_dice_coefficient

        # Apply a decay factor based on the conversation length to prioritize recent messages
        conversation_length = len(conversation_history.split())
        decay_factor = max(1 - (conversation_length / self.max_depth), 0.2)
        novelty_factor *= decay_factor

        # Adjust novelty factor based on the length of the message
        message_length_factor = max(len(message_words) / self.max_depth, 0.2)
        novelty_factor *= message_length_factor

        # Ensure novelty factor is within the range of 0 to 1
        novelty_factor = max(min(novelty_factor, 1.0), 0.0)

        return novelty_factor

    def save_conversation_history(self, filename: str) -> None:
        with open(filename, "w") as f:
            f.write(self.conversation_history)

    def reset(self) -> None:
        self.conversation_history = ""
        self.set_technique(self.technique_manager.get_synthesis_technique_names()[0])

    def get_synthesis_technique_info(self) -> Dict[str, Any]:
        return {
            "name": self.technique.technique_name,
            "imperative": self.technique.imperative,
            "prompts": self.technique.prompts,
        }
