""" Jlt Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.enums import InstructionArgument


class Jlt(Instruction):
    """
    If `a` is less than `b`, jump to the instruction indicated by `instr`.

    Args:
        a (Register): Register.
        b (int): Immediate.
        instr (int | str | Register): Number of the line, or register holding such number, or label to jump to.
    """

    def __init__(self, a: Register, b: int, instr: int | str | Register):
        args: list[int | str | Register] = [a, b, instr]
        types = [
            [InstructionArgument.REGISTER],
            [InstructionArgument.IMMEDIATE],
            [InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER, InstructionArgument.LABEL],
        ]
        super().__init__(args, types)
        # Add registers to read/write registers sets
        self.add_read_registers({a, instr})
