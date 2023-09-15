import base64
import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

import dill
from dimod import SampleSet


class StrangeworksSolutionType(Enum):
    SampleSet = "SampleSet"
    ListSolution = "list"


class StrangeworksSolution(ABC):
    solution: Any
    solution_type: StrangeworksSolutionType
    solution_options: dict | None = None
    strangeworks_parameters: dict | None = None

    @abstractmethod
    def to_str(self) -> str:
        ...

    @staticmethod
    @abstractmethod
    def from_str(
        solution_str: str,
    ) -> SampleSet | list:  # These types should match the types in the StrangeworksSolutionType Enum
        ...


class StrangeworksSampleSetSolution(StrangeworksSolution):
    def __init__(
        self,
        solution: SampleSet,
    ):
        self.solution = solution
        self.solution_type = StrangeworksSolutionType.SampleSet

    def to_str(self) -> str:
        return json.dumps(self.solution.to_serializable())

    @staticmethod
    def from_str(solution_str: str) -> SampleSet:
        s = SampleSet.from_serializable(json.loads(solution_str))
        if isinstance(s, SampleSet):
            return s
        else:
            raise TypeError("Unexpected type for solution")


class StrangeworksListSolution(StrangeworksSolution):
    def __init__(
        self,
        solution,
    ):
        self.solution = solution
        self.solution_type = StrangeworksSolutionType.ListSolution

    def to_str(self) -> str:
        return base64.b64encode(dill.dumps(self.solution)).decode()

    @staticmethod
    def from_str(solution_str: str) -> list:
        return list(dill.loads(base64.b64decode(solution_str)))


class StrangeworksSolutionFactory:
    @staticmethod
    def from_solution(solution):
        if solution is None:
            return None
        elif isinstance(solution, StrangeworksSolution):
            return solution
        elif isinstance(solution, SampleSet):
            return StrangeworksSampleSetSolution(solution=solution)
        elif isinstance(solution, list):
            return StrangeworksListSolution(solution=solution)
        else:
            raise ValueError("Unsupported solution type")

    @staticmethod
    def from_solution_str(
        solution_str: str,
        solution_type_str: str,
        solution_options: str | None = None,
        strangeworks_parameters: str | None = None,
    ):
        s: SampleSet | list
        solution_type = StrangeworksSolutionType(solution_type_str)
        if solution_type == StrangeworksSolutionType.SampleSet:
            s = StrangeworksSampleSetSolution.from_str(solution_str)
        elif solution_type == StrangeworksSolutionType.ListSolution:
            s = StrangeworksListSolution.from_str(solution_str)
        else:
            raise ValueError("Unsupported solution type")
        ss = StrangeworksSolutionFactory.from_solution(s)
        ss.solution_options = json.loads(solution_options) if solution_options else None
        ss.strangeworks_parameters = json.loads(strangeworks_parameters) if strangeworks_parameters else None
        return ss
