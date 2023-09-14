""" Wait Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.constants import INST_MAX_WAIT, INST_MIN_WAIT
from qpysequence.utils.enums import InstructionArgument


class Wait(Instruction):
    """
    Wait for `wait_time` number of nanoseconds.

    Args:
        wait_time (Register | int): value/register with the waiting time in nanoseconds.
    """

    def __init__(self, wait_time: Register | int):
        args: list[int | str | Register] = [wait_time]
        types = [[InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER]]
        bounds: list[tuple[int, int] | None] = [(INST_MIN_WAIT, INST_MAX_WAIT)]
        super().__init__(args, types, bounds, wait_time if isinstance(wait_time, int) else -4)
        # Add registers to read/write registers sets
        self.add_read_registers({wait_time})
