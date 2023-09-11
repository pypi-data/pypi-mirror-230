from typing import List
from dlm_matrix.chaintrees.base import SynthesisTechnique
from .synthesis import *
import random


class SynthesisTechniqueManager:
    def __init__(self):
        self.synthesis_techniques = [
            TheInfiniteMind(),
            ChaosTheory(),
            EurekaElicitation(),
            NonLinearNavigation(),
            Morphogenesis(),
            MetaphysicalIllumination(),
            ConvergentFusion(),
            DivergentExpansion(),
            ParadoxicalReflection(),
            QuantumEntanglement(),
            RadicalCollaboration(),
            SynergeticFusion(),
            OrganicSynthesis(),
            ThePowerOfPerspective(),
            EmergentSynthesis(),
        ]

    def get_random_synthesis_technique_name(self) -> str:
        return random.choice(self.get_synthesis_technique_names())

    def get_synthesis_technique(self, name: str) -> SynthesisTechnique:
        for synthesis_technique in self.synthesis_techniques:
            if synthesis_technique.technique_name == name:
                return synthesis_technique
        raise ValueError(f"Unknown synthesis technique {name}")

    def get_synthesis_technique_names(self) -> list[str]:
        return [
            synthesis_technique.technique_name
            for synthesis_technique in self.synthesis_techniques
        ]

    def get_synthesis_technique_epithets(self) -> List[str]:
        return [
            synthesis_technique.epithet
            for synthesis_technique in self.synthesis_techniques
        ]

    def get_synthesis_technique_imperatives(self) -> List[str]:
        return [
            synthesis_technique.imperative
            for synthesis_technique in self.synthesis_techniques
        ]

    def get_synthesis_technique_prompts(self) -> List[str]:
        return [
            synthesis_technique.prompts
            for synthesis_technique in self.synthesis_techniques
        ]

    def create_synthesis_technique(self, name: str) -> SynthesisTechnique:
        return self.get_synthesis_technique(name)
