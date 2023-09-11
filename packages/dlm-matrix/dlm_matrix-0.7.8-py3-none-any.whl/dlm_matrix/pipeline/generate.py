import random
from typing import List, Callable, Dict, Any, Optional
import string
from abc import ABC, abstractmethod
from dlm_matrix.models import BaseTreeGeneratorConfig


class BaseTreeGenerator(ABC):
    config: BaseTreeGeneratorConfig

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        pass

    def content_length_options(self) -> Dict[str, Callable[[], int]]:
        return {
            "uniform": lambda: (
                self.config.min_content_length + self.config.max_content_length
            )
            // 2,
            "short": lambda: self.config.min_content_length,
            "long": lambda: self.config.max_content_length,
        }

    def tree_structure_options(self) -> Dict[str, Callable[[], int]]:
        options = {
            "balanced": lambda: (self.config.min_depth + self.config.max_depth) // 2,
            "deep": lambda: self.config.max_depth,
            "shallow": lambda: self.config.min_depth,
        }

        if self.config.tree_structure_distribution == "lognormal":
            options["lognormal"] = lambda: int(
                random.lognormvariate(self.config.min_depth, self.config.max_depth)
            )
        elif self.config.tree_structure_distribution == "gamma":
            options["gamma"] = lambda: int(
                random.gammavariate(self.config.min_depth, self.config.max_depth)
            )
        elif self.config.tree_structure_distribution == "beta":
            options["beta"] = lambda: int(
                random.betavariate(self.config.min_depth, self.config.max_depth)
            )
        elif self.config.tree_structure_distribution == "exponential":
            options["exponential"] = lambda: int(
                random.expovariate(self.config.min_depth)
            )
        elif self.config.tree_structure_distribution == "normal":
            options["normal"] = lambda: int(
                random.normalvariate(self.config.min_depth, self.config.max_depth)
            )
        elif self.config.tree_structure_distribution == "pareto":
            options["pareto"] = lambda: int(random.paretovariate(self.config.min_depth))
        elif self.config.tree_structure_distribution == "triangular":
            options["triangular"] = lambda: int(
                random.triangular(self.config.min_depth, self.config.max_depth)
            )

        return options

    def content_generation_options(self) -> Dict[str, Callable[[], str]]:
        return {
            "random": lambda: "".join(
                random.choices(
                    self.config.content_characters,
                    k=self.content_length_options()[
                        self.config.content_length_distribution
                    ](),
                )
            ),
        }

    def tree_generation_options(self) -> Dict[str, Callable[[], Dict[str, Any]]]:
        return {
            "random": self.random_tree,
        }

    def random_tree(
        self,
        doc_hash: str,
        generation_parts: List[str],
        depth: int = None,
        tree_type: str = "random",
        x: float = None,
        y: float = None,
    ) -> None:
        try:
            assert depth is None or depth >= 0
            if depth is None:
                depth = self.tree_structure_options()[
                    self.config.tree_structure_distribution
                ]()

            if depth == 0:
                return None

            if tree_type == "random":
                tree_type = random.choice(["branch", "leaf"])

            if tree_type == "branch":
                children = []
                for _ in range(
                    random.randint(self.config.min_children, self.config.max_children)
                ):
                    children.append(
                        self.generate_tree(
                            doc_hash,
                            generation_parts,
                            depth=depth - 1,
                            tree_type="random",
                        )
                    )
                return {
                    "type": "branch",
                    "children": children,
                    "x": x,
                    "y": y,
                }

            elif tree_type == "leaf":
                content_length = self.content_length_options()[
                    self.config.content_length_distribution
                ]()
                if self.config.content_generation_algorithm == "random":
                    content = "".join(
                        random.choices(self.config.content_characters, k=content_length)
                    )
                else:
                    raise ValueError(
                        f"Unknown content generation algorithm: {self.config.content_generation_algorithm}"
                    )
                return {
                    "type": "leaf",
                    "content": content,
                    "x": x,
                    "y": y,
                }

            else:
                raise ValueError(f"Unknown tree type: {tree_type}")
        except Exception as e:
            print(e)

    def update_coordinates(
        self,
        tree: Dict[str, Any],
        x: float = None,
        y: float = None,
        depth: int = 0,
        children: int = 0,
    ) -> None:
        try:
            if x is None:
                x = 0
            if y is None:
                y = 0
            tree["x"] = x
            tree["y"] = y
            if tree["type"] == "branch":
                for child in tree["children"]:
                    self.update_coordinates(
                        child, x=x, y=y + 1, depth=depth + 1, children=children
                    )
                    children += 1
                    x += 1
            return tree
        except Exception as e:
            print(e)
            return None

    def generate_tree(
        self, doc_hash: str, generation_parts: List[str]
    ) -> Dict[str, Any]:
        tree = self.generate(doc_hash, generation_parts)
        return self.update_coordinates(tree)

    def generate_trees(
        self, doc_hashes: List[str], generation_parts: List[str]
    ) -> List[Dict[str, Any]]:
        trees = []
        for doc_hash in doc_hashes:
            trees.append(self.generate_tree(doc_hash, generation_parts))
        return trees


class TreeGenerator(BaseTreeGenerator):
    def __init__(self, config: BaseTreeGeneratorConfig):
        self.config = config
        self.trees = []

    def generate(self, doc_hash: str, generation_parts: List[str]) -> Dict[str, Any]:
        tree = {
            "doc_hash": doc_hash,
            "type": "branch",
            "children": [],
        }
        for part in generation_parts:
            if part == "content":
                tree["content"] = self.generate_content()
            elif part == "structure":
                tree["children"] = self.generate_structure()
        return tree

    def generate_content(self) -> str:
        return self.content_generation_options()[
            self.config.content_generation_algorithm
        ]()

    def generate_structure(self) -> List[Dict[str, Any]]:
        depth = self.tree_structure_options()[self.config.tree_structure_distribution]()
        return self._generate_structure(depth)

    def _generate_structure(self, depth: int) -> List[Dict[str, Any]]:
        if depth == 0:
            return [
                {
                    "type": "leaf",
                    "content": self.generate_content(),
                }
            ]
        else:
            return [
                {
                    "type": "branch",
                    "children": self._generate_structure(depth - 1),
                }
                for _ in range(
                    random.randint(self.config.min_children, self.config.max_children)
                )
            ]

    def generate_content_random(
        self,
        length: Optional[int] = None,
        length_distribution: Optional[str] = "uniform",
    ) -> str:
        if length is None:
            length = self.content_length_options()[length_distribution]()
        return "".join(random.choices(self.config.content_characters, k=length))


class TreeGeneratorConfig(BaseTreeGeneratorConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_generation_algorithm = kwargs.get(
            "content_generation_algorithm", "random"
        )
        self.content_length_distribution = kwargs.get(
            "content_length_distribution", "uniform"
        )
        self.min_content_length = kwargs.get("min_content_length", 10)
        self.max_content_length = kwargs.get("max_content_length", 100)
        self.tree_structure_distribution = kwargs.get(
            "tree_structure_distribution", "balanced"
        )
        self.min_depth = kwargs.get("min_depth", 1)
        self.max_depth = kwargs.get("max_depth", 10)
        self.content_characters = kwargs.get(
            "content_characters",
            string.ascii_letters + string.digits + string.punctuation,
        )


class TreeGeneratorFactory:
    @staticmethod
    def create(config: BaseTreeGeneratorConfig) -> BaseTreeGenerator:
        if config.content_generation_algorithm == "random":
            return TreeGenerator(config)
        else:
            raise ValueError("Invalid content generation algorithm")


class TreeGeneratorConfigFactory:
    @staticmethod
    def create(**kwargs) -> BaseTreeGeneratorConfig:
        return TreeGeneratorConfig(**kwargs)


class TreeGeneratorFactory:
    @staticmethod
    def create(config: BaseTreeGeneratorConfig) -> BaseTreeGenerator:
        if config.content_generation_algorithm == "random":
            return TreeGenerator(config)
        else:
            raise ValueError("Invalid content generation algorithm")


class TreeGeneratorConfigFactory:
    @staticmethod
    def create(**kwargs) -> BaseTreeGeneratorConfig:
        return TreeGeneratorConfig(**kwargs)


class TreeGeneratorFactory:
    @staticmethod
    def create(config: BaseTreeGeneratorConfig) -> BaseTreeGenerator:
        if config.content_generation_algorithm == "random":
            return TreeGenerator(config)
        else:
            raise ValueError("Invalid content generation algorithm")
