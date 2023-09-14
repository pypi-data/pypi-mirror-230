""" Jmp Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.enums import InstructionArgument


class Jmp(Instruction):
    """
    Jump to the next instruction indicated by `instr`.

    Args:
        instr (int | Register): number of the line, or register holding such number, or label to jump to.
    """

    def __init__(self, instr: int | Register):
        args: list[int | str | Register] = [instr]
        types = [[InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER]]
        super().__init__(args, types)
        self.potential_registers = [True]
        # Add registers to read/write registers sets
        self.add_read_registers({instr})
