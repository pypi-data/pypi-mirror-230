""" UpdParam Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.constants import INST_MAX_WAIT, INST_MIN_WAIT
from qpysequence.utils.enums import InstructionArgument


class UpdParam(Instruction):
    """
    Update the marker, phase, phase offset, gain and offset parameters set using their respective instructions and then
    wait for `wait_time` number of nanoseconds.

    Args:
        wait_time (int): time to wait in nanoseconds.
    """

    def __init__(self, wait_time: int):
        args: list[int | str | Register] = [wait_time]
        types = [[InstructionArgument.IMMEDIATE]]
        bounds: list[tuple[int, int] | None] = [(INST_MIN_WAIT, INST_MAX_WAIT)]
        super().__init__(args, types, bounds, wait_time)
