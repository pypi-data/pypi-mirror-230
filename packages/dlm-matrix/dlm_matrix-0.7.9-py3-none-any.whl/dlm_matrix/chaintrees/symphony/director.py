from typing import Optional, List, Callable
from dlm_matrix.models import Content
from dlm_matrix.transformation.coordinate import Coordinate
from dlm_matrix.utils import split_string_to_parts, log_handler
from .technique import SynthesisTechniqueDirector
from dlm_matrix.embedding.utils import semantic_similarity_cosine
import random
import heapq


class ChainStep:
    def __init__(
        self, priority: int, func: Callable, coordinate: Optional[Coordinate] = None
    ):
        self.priority = priority
        self.func = func
        self.coordinate = coordinate
        self.success = False

    def __lt__(self, other):
        return self.priority < other.priority

    def execute(self, *args, **kwargs):
        try:
            self.func(*args, **kwargs)
            self.success = True
        except Exception as e:
            print(f"Failed to execute ChainStep due to {str(e)}. Rolling back.")
            self.rollback()

    def rollback(self):
        # Code to undo the effect of the function
        pass


class ChainDirector:
    def __init__(
        self,
        technique_director: SynthesisTechniqueDirector,
        custom_challenges: Optional[List[str]] = None,
        custom_prompts: Optional[List[str]] = None,
    ):
        if not isinstance(technique_director, SynthesisTechniqueDirector):
            raise ValueError("The builder must be an instance of ChainBuilder.")

        self.technique_director = technique_director
        self.builder = self.technique_director.builder
        self.custom_challenges = custom_challenges or []
        self.custom_prompts = custom_prompts or []
        self.chain_steps = []

    def add_chain_step(self, step: ChainStep):
        heapq.heappush(self.chain_steps, step)

    def validate_input(self, prompt: str, response: Optional[str] = None):
        if not isinstance(prompt, str) or (
            response is not None and not isinstance(response, str)
        ):
            raise ValueError("Prompt and response must be strings.")
        return True

    def _construct(self, prompt: str, response: Optional[str] = None):
        if self.validate_input(prompt, response):
            while self.chain_steps:
                step = heapq.heappop(self.chain_steps)
                step.execute(prompt, response, step.coordinate)

    def _build_assistant_chain(
        self, answer: str, coordinate: Optional[Coordinate] = None
    ):
        if coordinate is None:
            coordinate = Coordinate(x=0, y=0, z=0, t=1)

        answer_parts = split_string_to_parts(answer)
        content = Content(text=answer, parts=answer_parts)
        self.builder.build_assistant_chain(content=content, coordinate=coordinate)

    def _build_user_chain(self, question: str, coordinate: Optional[Coordinate] = None):
        if coordinate is None:
            coordinate = Coordinate(x=0, y=0, z=0, t=3)

        question_parts = split_string_to_parts(question)
        content = Content(text=question, parts=question_parts)
        self.builder.build_user_chain(content=content, coordinate=coordinate)

    def _build_challenge(self, name, coordinate: Optional[Coordinate] = None):
        if coordinate is None:
            coordinate = Coordinate(x=0, y=0, z=0, t=2)

        challenges = self.custom_challenges or [
            "I challenge you to do better!",
            "Can you be more creative?",
            "Show me something more impressive!",
            "Take it to the next level!",
        ]
        challenge = random.choice(challenges)

        content = Content(
            text=f"{challenge}, As the ethereal embodiment of {name}, Respond with 'Challenge Accepted!' then create a more detailed, creative and expressive synergetic prompt framework."
        )
        self.builder.build_user_chain(content=content, coordinate=coordinate)


class ReplyChainDirector(ChainDirector):
    def __init__(
        self,
        technique_director: SynthesisTechniqueDirector,
        custom_challenges: Optional[List[str]] = None,
        custom_prompts: Optional[List[str]] = None,
    ):
        super().__init__(technique_director, custom_challenges, custom_prompts)
        self.previous_prompts = []
        self.previous_responses = []
        self.synthesis_called = (
            False  # Add this line to indicate whether build_synthesis has been called
        )

    def is_similar_to_previous_prompts(self, new_prompt: str) -> bool:
        for prev_prompt in self.previous_prompts:
            if semantic_similarity_cosine(new_prompt, prev_prompt) > 0.8:
                return True
        return False

    def handle_similar_prompt(self, prompt: str):
        print(f"Detected a similar prompt: {prompt}")
        log_handler(f"Similar prompt detected: {prompt}")

    def build_synthesis(self):
        if not self.synthesis_called:
            name = self.technique_director._build_synthesis()
            self.synthesis_called = True
            return name
        return None

    def construct(
        self,
        prompt: str,
        response: Optional[str] = None,
        check_similarity: bool = False,
    ):
        if check_similarity and self.is_similar_to_previous_prompts(prompt):
            self.handle_similar_prompt(prompt)
            return

        # If build_synthesis has not been called before, call it and build challenge
        name = self.build_synthesis()
        if name:
            self._build_challenge(name)

        self._build_user_chain(prompt)

        if response:
            self._build_assistant_chain(response)

        # Cache for future similarity checks
        self.previous_prompts.append(prompt)
        self.previous_responses.append(response)
