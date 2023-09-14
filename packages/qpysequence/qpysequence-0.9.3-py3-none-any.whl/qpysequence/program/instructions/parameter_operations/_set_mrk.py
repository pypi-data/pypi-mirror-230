""" SetMrk Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.constants import SEQ_N_MARKERS
from qpysequence.utils.enums import InstructionArgument


class SetMrk(Instruction):
    """Set marker output channels to `marker_outputs` (bits 0-3), where the bit index corresponds to the channel index
    for baseband modules. For QCM-RF module, bit indices 0 & 1 corespond to output enable 1 and 2 respectively; indices
    2 & 3 correspond to marker outputs 1 and 2 respectively. The values are OR'ed by that of other sequencers. The
    parameters are cached and only updated when real_time.io instructions are executed.

    Args:
        marker_outputs (str | int): value/register with a 4-bit integer representing the four marker outputs.
    """

    def __init__(self, marker_outputs: str | int):
        args: list[int | str | Register] = [marker_outputs]
        types = [[InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER]]
        bounds: list[tuple[int, int] | None] = [(0, SEQ_N_MARKERS**2 - 1)]
        super().__init__(args, types, bounds)
