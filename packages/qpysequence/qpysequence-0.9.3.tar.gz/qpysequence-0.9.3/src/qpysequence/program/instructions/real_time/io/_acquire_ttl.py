""" Acquire Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.constants import INST_MAX_WAIT, INST_MIN_WAIT
from qpysequence.utils.enums import InstructionArgument


class AcquireTtl(Instruction):
    """
    Update the marker, phase, phase offset, gain and offset parameters set using their respective instructions, start
    the TTL trigger acquisition refered to using index `acq_index` argument and store the bin data in `bin_index`,
    enable the acquisition by writing 1 to `trigger`, finally wait for `wait_time` number of nanoseconds. The TTL
    trigger acquisition has to be actively disabled afterwards by writing 0 to `trigger`.


    Args:
        acq_index (int): index of the acquisition.
        bin_index (int | Register): value/register with the index of the bin.
        trigger (int): TTL trigger value. 0 = disabled, 1 = enabled.
        wait_time (int, optional): time to wait in nanoseconds. Defaults to 4.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        acq_index: int,
        bin_index: int | Register,
        trigger: int,
        wait_time: int = 4,
    ):
        args: list[int | str | Register] = [acq_index, bin_index, trigger, wait_time]
        types = [
            [InstructionArgument.IMMEDIATE],
            [InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER],
            [InstructionArgument.IMMEDIATE],
            [InstructionArgument.IMMEDIATE],
        ]
        bounds: list[tuple[int, int] | None] = [None, None, (0, 1), (INST_MIN_WAIT, INST_MAX_WAIT)]
        super().__init__(args, types, bounds, wait_time)
        # Add registers to read/write registers sets
        self.add_write_registers({bin_index})
