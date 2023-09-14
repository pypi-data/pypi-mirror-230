""" ResetPh Instruction """

from qpysequence.program.instructions.instruction import Instruction


class ResetPh(Instruction):
    """
    Reset the absolute phase of the NCO used by the AWG and acquisition to 0°. This also resets any relative phase
    offsets that were already statically or dynamically set. The reset is cached and only applied when the `upd_param`,
    `play`, `acquire` or `acquired_weighed` instructions are executed.
    """

    def __init__(self):
        super().__init__()
