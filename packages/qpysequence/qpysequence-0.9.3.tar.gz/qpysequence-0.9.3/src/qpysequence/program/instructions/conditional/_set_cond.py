""" SetCond Instruction """

from qpysequence.program.instructions.instruction import Instruction
from qpysequence.program.register import Register
from qpysequence.utils.constants import INST_MAX_WAIT, INST_MIN_WAIT
from qpysequence.utils.enums import InstructionArgument


class SetCond(Instruction):
    """
    Enable/disable conditionality on all following real-time instructions based on the `enable` argument. The condition
    is based on the trigger network address counters being thresholded based on the associated counter threshold
    parameters set through QCoDeS. The results are masked using the `mask` argument (bits 0-14), where the bit index
    plus one corresponds to the trigger address. This creates a selection to include in the final logical operation set
    using the `operator` argument. The logical operation result (true/false) determines the condition. If the
    condition is true upon evaluation, the next real-time instruction is executed. Else the real-time path ignores the
    instruction and waits for `wait_time` number of nanoseconds before continueing to the next. All following real-time
    instructions are subject to the same condition, until either the conditionality is disabled or updated. Disabling
    the conditionality does not affect the address counters. Logical Operators are  OR, NOR, AND, NAND, XOR, XNOR,
    where a value for `operator' of 0 is OR and 5 is XNOR respectively.

    Args:
        enable (Register | int): conditionality enabled (1) or disabled (0).
        mask (Register | int): 14 bits mask for the results.
        operator (Register | int): operator selection {0: OR, 1: NOR, 2: AND, 3: NAND, 4: XOR, 5: XNOR}.
        wait_time (int): time to wait in nanoseconds.
    """

    def __init__(self, enable: Register | int, mask: Register | int, operator: Register | int, wait_time: int):
        args: list[int | str | Register] = [enable, mask, operator, wait_time]
        types = [
            [InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER],
            [InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER],
            [InstructionArgument.IMMEDIATE, InstructionArgument.REGISTER],
            [InstructionArgument.IMMEDIATE],
        ]
        bounds: list[tuple[int, int] | None] = [(0, 1), (0, 2**14 - 1), (0, 5), (INST_MIN_WAIT, INST_MAX_WAIT)]
        super().__init__(args, types, bounds, wait_time)
        # Add registers to read/write registers sets
        self.add_write_registers({enable, mask, operator})
