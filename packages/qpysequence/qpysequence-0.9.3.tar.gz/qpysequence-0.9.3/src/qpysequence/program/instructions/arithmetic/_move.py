""" Move Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.enums import InstructionArgument


class Move(Instruction):
    """`var` is moved/copied to `register`.

    Args:
        var (Register | int): value/register to be moved/copied.
        register (Register): destination register.
    """

    def __init__(self, var: Register | int, register: Register):
        args: list[int | str | Register] = [var, register]
        types = [[InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER], [InstructionArgument.REGISTER]]
        super().__init__(args, types)
        # Add registers to read/write registers sets
        self.add_read_registers({var})
        self.add_write_registers({register})
