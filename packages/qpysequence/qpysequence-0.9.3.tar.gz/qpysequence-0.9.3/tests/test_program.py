from xml.dom import NotFoundErr

import pytest

from qpysequence.program import Program
from qpysequence.program.instructions import WaitSync
from qpysequence.program.loop import Loop


@pytest.fixture(name="program")
def fixture_program() -> Program:
    """Loads Program

    Returns:
        Program: Instance of the Program class
    """
    return Program()


class TestProgram:
    """Unitary tests checking the Program class behavior"""

    def test_initialization(self, program: Program):
        """Tests that a Program has been initialized as expected."""

        setup = None
        try:
            setup = program.get_block("setup")
        except NotFoundErr:
            assert False

        last_inst = None
        try:
            last_inst = setup.components[-1]
        except IndexError:
            assert False

        assert isinstance(last_inst, WaitSync)
        assert last_inst.args[0] == 4

    def test_compilation(self, program: Program):
        """Tests that a loop has its counter properly allocated when the program is compiled."""

        loop = Loop("loop", 100)
        program.append_block(loop)
        program.compile()
        assert repr(loop.counter_register) == "R0"
