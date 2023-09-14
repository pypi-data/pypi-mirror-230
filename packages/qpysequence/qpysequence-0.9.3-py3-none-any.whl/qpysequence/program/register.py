"""Register module."""
from qpysequence.utils.constants import PROG_REG_PREFIX


class Register:
    """Register class."""

    def __init__(self):
        self.allocated = False
        self.number = -1

    def __repr__(self) -> str:
        """Returns a string representation of the Register.

        Returns:
            str: Q1ASM string representation if allocated, default Python representation otherwise.
        """
        return f"{PROG_REG_PREFIX}{self.number}" if self.allocated else super().__repr__()
