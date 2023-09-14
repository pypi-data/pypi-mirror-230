""" Or Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.enums import InstructionArgument


class Or(Instruction):
    """Bit-wise OR `var` to the value in `origin` and move the result to `destination`.

    Args:
        origin (Register): origin register.
        var (Register | int): value/register to be "ored" to the value in `origin`.
        destination (Register): destination register.
    """

    def __init__(self, origin: Register, var: Register | int, destination: Register):
        args: list[int | str | Register] = [origin, var, destination]
        types = [
            [InstructionArgument.REGISTER],
            [InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER],
            [InstructionArgument.REGISTER],
        ]
        super().__init__(args, types)
        # Add registers to read/write registers sets
        self.add_read_registers({var})
        self.add_write_registers({origin, destination})
