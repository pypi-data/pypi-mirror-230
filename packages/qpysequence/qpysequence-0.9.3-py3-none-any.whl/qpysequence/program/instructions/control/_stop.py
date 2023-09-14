""" Stop Instruction """
from qpysequence.program.instructions.instruction import Instruction


class Stop(Instruction):
    """
    Instruction that stops the sequencer.
    """

    def __init__(self):
        super().__init__()
