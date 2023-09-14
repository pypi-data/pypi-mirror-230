""" Illegal Instruction """
from qpysequence.program.instructions.instruction import Instruction


class Illegal(Instruction):
    """
    Instruction that should not be executed. If it is executed, the sequencer will stop with the illegal instruction
    flag set.
    """

    def __init__(self):
        super().__init__()
