"""Components module.
Contains the elements to build a Program: Blocks and Loops.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .memory import Memory
from .nopper import Nopper


class Component(ABC):
    """
    Abstract class to contain the common methods and attributes of Blocks and
    Instructions.
    """

    @property
    @abstractmethod
    def duration(self) -> int:
        """Returns the real time duration for the execution of the component in nanoseconds.

        Raises:
            NotImplementedError: Abstract Method.

        Returns:
            int: Real time duration of the component in nanoseconds.
        """
        raise NotImplementedError

    @abstractmethod
    def allocate_registers(self, memory: Memory):
        """Allocates the registers used in this component."""

    @abstractmethod
    def check_nops(self, nopper: Nopper, depth: int):
        """Searches where Nop instructions are needed and saves those positions."""
