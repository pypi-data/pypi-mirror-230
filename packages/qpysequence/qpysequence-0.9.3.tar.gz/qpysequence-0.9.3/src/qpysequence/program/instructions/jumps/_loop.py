""" Loop Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.enums import InstructionArgument


class Loop(Instruction):
    """
    Subtract `count` by one and jump to the instruction indicated by `instr` until `count` reaches zero.

    Args:
        count (Register): Register.
        instr (int | str | Register): Number of the line, or register holding such number, or label to jump to.
    """

    def __init__(self, count: Register, instr: int | str | Register):
        args: list[int | str | Register] = [count, instr]
        types = [
            [InstructionArgument.REGISTER],
            [InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER, InstructionArgument.LABEL],
        ]
        super().__init__(args, types)
        # Add registers to read/write registers sets
        self.add_read_registers({instr, count})
        self.add_write_registers({count})
