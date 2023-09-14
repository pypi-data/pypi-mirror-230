"""Enum classes"""

from enum import Enum


class InstructionArgument(Enum):
    """Enum class for the Instruction Arguments type.

    Args:
        enum (str): Instruction Argument types:
            * immediate
            * register
            * label
    """

    IMMEDIATE = "immediate"
    REGISTER = "register"
    LABEL = "label"
