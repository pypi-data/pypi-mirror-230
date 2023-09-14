import pytest

from qpysequence.program import Register
from qpysequence.program.memory import Memory


@pytest.fixture(name="memory")
def fixture_memory() -> Memory:
    """Loads Program

    Returns:
        Program: Instance of the Program class
    """
    return Memory(max_registers=2)


class TestMemory:
    """Unitary tests checking the Memory class behavior"""

    def test_allocate_register(self, memory: Memory):
        """Tests that a Memory allocates registers properly."""

        register_a = Register()
        register_b = Register()

        memory.allocate_register(register_a)
        memory.allocate_register(register_a)
        memory.allocate_register(register_b)

        assert register_a.allocated
        assert register_b.allocated
        assert repr(register_a) == "R0"
        assert repr(register_b) == "R1"
