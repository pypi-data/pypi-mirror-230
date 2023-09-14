""" AcquireWeighed Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.constants import INST_MAX_WAIT, INST_MIN_WAIT
from qpysequence.utils.enums import InstructionArgument


class AcquireWeighed(Instruction):
    """
    Update the marker, phase, phase offset, gain and offset parameters set using their respective instructions, start
    the acquisition refered to using index `acq_index` argument and store the bin data in `bin_index`, finally wait for
    `wait_time` number of nanoseconds. Integration is executed using weights stored at indexes `weight_index_0` for
    path 0 and `weight_index_1` for path 1. The arguments are either all set through immediates or registers.

    Args:
        acq_index (int): index of the acquisition.
        bin_index (Register | int): value/register with the index of the bin.
        weight_index_0 (Register | int): value/register with the index of the weight for path 0.
        weight_index_1 (Register | int): value/register with the index of the weight for path 1.
        wait_time (int, optional): time to wait in nanoseconds. Defaults to 4.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        acq_index: int,
        bin_index: Register | int,
        weight_index_0: Register | int,
        weight_index_1: Register | int,
        wait_time: int = 4,
    ):
        args: list[int | str | Register] = [acq_index, bin_index, weight_index_0, weight_index_1, wait_time]
        types = [
            [InstructionArgument.IMMEDIATE],
            [InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER],
            [InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER],
            [InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER],
            [InstructionArgument.IMMEDIATE],
        ]
        bounds: list[tuple[int, int] | None] = [None, None, None, None, (INST_MIN_WAIT, INST_MAX_WAIT)]
        super().__init__(args, types, bounds, wait_time)
        # Add registers to read/write registers sets
        self.add_read_registers({weight_index_0, weight_index_1})
        self.add_write_registers({bin_index})
