""" SetPhDelta Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.constants import NCO_MAX_INT_PHASE
from qpysequence.utils.enums import InstructionArgument


class SetPhDelta(Instruction):
    """
    Set an `offset` on top of the relative phase of the NCO used by the AWG and acquisition. The offset
    is applied on top of the phase set using `set_ph`. The offset phase is divided into 1e9 steps between 0º and 360º,
    expressed as an integer between 0 and 1e9 (e.g. 45º=125e6). The parameters are cached and only updated when the
    `upd_param`, `play`, `acquire` or `acquire_weighted` instructionns are executed.

    Args:
        offset (int | Register): integer between 0 and 1e9 representing the NCO offset phase from 0º to 360º.
    """

    def __init__(self, phase: int | Register):
        args: list[int | str | Register] = [phase]
        types = [[InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER]]
        bounds: list[tuple[int, int] | None] = [(0, NCO_MAX_INT_PHASE)]
        super().__init__(args, types, bounds)
        # Add registers to read/write registers sets
        self.add_read_registers({phase})
