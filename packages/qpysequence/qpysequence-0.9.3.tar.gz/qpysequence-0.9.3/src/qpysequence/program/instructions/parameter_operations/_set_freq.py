""" SetPh Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.constants import NCO_MAX_INT_FREQ, NCO_MIN_INT_FREQ
from qpysequence.utils.enums import InstructionArgument


class SetFreq(Instruction):
    """Set the frequency of the NCO used by the AWG and acquisition using `frequency`. The frequency is divided into
    4e9 steps between -500MHz and 500MHz and expressed as an integer between -2e9 and 2e9 (e.g. 1MHz=4e6). The
    frequency parameter is cached and only applied when the `upd_param`, `play`, `acquire` or `acquire_weighed`
    instructions are executed.

    Args:
        frequency (int | Register): integer between -2e9 and 2e9 representing the NCO frequency from -500MHz to 500MHz.
    """

    def __init__(self, frequency: int | Register):
        args: list[int | str | Register] = [frequency]
        types = [[InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER]]
        bounds: list[tuple[int, int] | None] = [(NCO_MIN_INT_FREQ, NCO_MAX_INT_FREQ)]
        super().__init__(args, types, bounds)
        # Add registers to read/write registers sets
        self.add_read_registers({frequency})
