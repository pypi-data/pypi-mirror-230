""" Nop Instruction """
from qpysequence.program.instructions.instruction import Instruction


class Nop(Instruction):
    """
    No operation instruction, that does nothing. It is used to pass a single cycle in the classic part of the sequencer
    without any operations.
    """

    def __init__(self):
        super().__init__()
