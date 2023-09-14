""" LatchEn Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.constants import INST_MAX_WAIT, INST_MIN_WAIT, MASK_MAX_VALUE
from qpysequence.utils.enums import InstructionArgument


class SetLatchEn(Instruction):
    """
    Enable/disable all trigger network address counters based on the `enable` argument and then wait for `wait_time`
    number of nanoseconds. Once enabled, the trigger network address counters will count all triggers on the trigger
    network. When disabled, the counters hold their last values.

    Args:
        enable (Register | int): trigger mask bits 0-15.
        wait_time (int): waiting time in nanoseconds.
    """

    def __init__(self, enable: Register | int, wait_time: int):
        args: list[int | str | Register] = [enable, wait_time]
        types = [[InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER], [InstructionArgument.IMMEDIATE]]
        bounds: list[tuple[int, int] | None] = [(0, MASK_MAX_VALUE), (INST_MIN_WAIT, INST_MAX_WAIT)]
        super().__init__(args, types, bounds, wait_time)
        # Add registers to read/write registers sets
        self.add_read_registers({enable})
