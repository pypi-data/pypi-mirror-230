from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import random
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import openai
import collections
from sentence_transformers import SentenceTransformer


class QueryGenerator(BaseModel):
    """
    A class for generating creative prompts using a combination of linguistic analysis
    and phrase synthesis.
    """

    keywords: List[str] = Field(...)
    templates: List[str] = Field(default_factory=list, description="List of templates.")
    min_keywords: int = Field(
        1, description="Minimum number of keywords to use in each prompt."
    )
    max_keywords: int = Field(
        3, description="Maximum number of keywords to use in each prompt."
    )
    phrase_ratio: float = Field(
        0.5, description="Ratio of new phrases to include in each prompt."
    )

    transformer: SentenceTransformer = SentenceTransformer("all-mpnet-base-v2")

    keyword_usage: Dict[str, int] = Field(
        default_factory=lambda: collections.defaultdict(int)
    )
    verification_threshold: float = Field(
        0.5, description="The threshold for accepting a phrase as logical."
    )

    class Config:
        arbitrary_types_allowed = True

    def _get_word_embedding(self, word: str) -> np.array:
        """Get the word embedding for a given word using the specified word embedding model."""
        return self.transformer.encode([word])[0]

    def add_keyword(self, keyword: str) -> None:
        """Add a new keyword to the list."""
        self.keywords.append(keyword)
        self.keyword_usage[keyword] = 0

    def remove_keyword(self, keyword: str) -> None:
        """Remove a keyword from the list."""
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            if keyword in self.keyword_usage:
                del self.keyword_usage[keyword]

    def _get_least_used_keywords(self, num_keywords: int):
        """Get the least used keywords."""
        return sorted(self.keywords, key=lambda k: self.keyword_usage[k])[:num_keywords]

    def generate_related_phrase(self, keywords: List[str]) -> str:
        """Generate a related phrase for given keywords using the GPT-3 language model."""

        keywords_string = ", ".join(keywords[:-1]) + " and " + keywords[-1]
        prompts = [
            f"{keywords_string} are associated with",
            f"{keywords_string} reminds me of",
            f"Something common between {keywords_string} is",
        ]
        results = []
        for prompt in prompts:
            response = openai.Completion.create(
                engine="text-davinci-003", prompt=prompt, temperature=0.7, max_tokens=20
            )
            related_phrase = response["choices"][0]["text"].strip()
            results.append(related_phrase)

        # return the phrase with the highest cosine similarity with keywords
        keyword_embeddings = np.mean(
            [self._get_word_embedding(k) for k in keywords], axis=0
        )
        related_phrase_embeddings = [self._get_word_embedding(r) for r in results]
        similarities = [
            np.dot(keyword_embeddings, r)
            / (np.linalg.norm(keyword_embeddings) * np.linalg.norm(r))
            for r in related_phrase_embeddings
        ]
        best_index = np.argmax(similarities)

        return results[best_index]

    def verify_phrase(self, phrase: str) -> bool:
        """Verify the logical coherence of a phrase using GPT-3 model."""
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{phrase} makes sense.",
            temperature=0.7,
            max_tokens=20,
        )
        verification = response["choices"][0]["text"].strip().lower()
        verification_score = (
            response["choices"][0]["finish_reason"] == "stop"
        )  # if the model decided to stop, it's more likely the phrase makes sense.
        return (
            verification in ["yes", "true", "certainly"]
            and verification_score > self.verification_threshold
        )

    def synthesize_new_word_or_phrase(self, num_keywords: int) -> str:
        """Generate a new word or phrase using a random selection of keywords."""
        if num_keywords == 1:
            return random.choice(self.keywords)
        keywords = sorted(self.keywords, key=lambda k: self.keyword_usage[k])[
            :num_keywords
        ]
        for keyword in keywords:
            self.keyword_usage[keyword] += 1
        synonyms = [self.generate_related_phrase([keyword]) for keyword in keywords]
        random.shuffle(synonyms)
        return " and ".join(synonyms)

    def generate_new_prompt(
        self, template: str, num_keywords: Optional[int] = None
    ) -> str:
        """Generate a new prompt using a given template and a specified number of keywords."""
        if num_keywords is None:
            num_keywords = random.randint(self.min_keywords, self.max_keywords)
        new_keywords = self.synthesize_new_word_or_phrase(num_keywords)
        return template.format(new_keywords)

    def get_semantically_similar_keywords(
        self, keyword: str, topn: int = 10
    ) -> List[str]:
        """Find semantically similar keywords to a given keyword."""
        keyword_embedding = self._get_word_embedding(keyword)
        keyword_embeddings = [self._get_word_embedding(kw) for kw in self.keywords]

        # Compute cosine similarity between keyword and all other keywords
        cosine_similarities = cosine_similarity(
            [keyword_embedding], keyword_embeddings
        )[0]
        # Get indices of keywords sorted by cosine similarity
        sorted_indices = np.argsort(cosine_similarities)[::-1]
        # Return the topn most similar keywords
        return [self.keywords[idx] for idx in sorted_indices[:topn]]

    def get_semantically_similar_keywords_batch(
        self, keywords: List[str], topn: int = 10
    ) -> List[List[str]]:
        """Find semantically similar keywords to a given keyword."""
        keyword_embeddings = [self._get_word_embedding(kw) for kw in keywords]
        keyword_embeddings = np.array(keyword_embeddings)

        # Compute cosine similarity between keyword and all other keywords
        cosine_similarities = cosine_similarity(keyword_embeddings, keyword_embeddings)
        # Get indices of keywords sorted by cosine similarity
        sorted_indices = np.argsort(cosine_similarities, axis=1)[:, ::-1]
        # Return the topn most similar keywords
        return [[keywords[idx] for idx in indices[:topn]] for indices in sorted_indices]

    def generate_expressive_prompts(
        self,
        templates: List[str],
        num_prompts: int = 10,
        prompt_keywords: Dict[str, List[str]] = None,
    ) -> List[str]:
        """Generate a list of expressive prompts by repeatedly applying the generate_new_prompt method on a list of templates."""
        prompts = []
        for _ in range(num_prompts):
            template = random.choice(templates)  # Randomly select a template
            prompts.append(self.generate_new_prompt(template, prompt_keywords))
        return prompts

    def generate_prompt(self, template: str, num_keywords: int = 3) -> str:
        """Generate a new prompt by randomly injecting synthesized words or phrases into the template."""
        new_keywords = [
            self.synthesize_new_word_or_phrase(num_keywords)
            for _ in range(num_keywords)
        ]
        random.shuffle(new_keywords)

        return template.format(*new_keywords)

    def generate_expressive_prompts_batch(
        self,
        templates: List[str],
        num_prompts: int = 10,
        prompt_keywords: Dict[str, List[str]] = None,
    ) -> List[str]:
        """Generate a list of expressive prompts by repeatedly applying the generate_new_prompt method on a list of templates."""
        prompts = []
        for _ in range(num_prompts):
            template = random.choice(templates)

            # Randomly select a template
            prompts.append(self.generate_prompt(template, prompt_keywords))
        return prompts
