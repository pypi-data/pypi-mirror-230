"""Memory module."""
from .register import Register


class Memory:
    """Memory class to handle and allocate the registers used by a program.

    Args:
        max_registers (int): Maximum number of registers that can be allocated.
    """

    def __init__(self, max_registers: int):
        self.max_registers = max_registers
        self.cursor = -1

    def allocate_register(self, register: Register):
        """Allocates a new register if not already allocated.

        Args:
            register (Register): Register to allocate.

        Raises:
            MemoryError: Reached allocation limit.
        """
        if not register.allocated:
            self.cursor += 1
            if self.cursor >= self.max_registers:
                raise MemoryError(
                    f"""Memory limit exceeded: the maximum number of registers for this memory instance is
                    {self.max_registers}"""
                )
            register.number = self.cursor
            register.allocated = True
