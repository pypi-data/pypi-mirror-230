import pytest

from qpysequence.program import Loop
from qpysequence.program.instructions import Add, Jge, Jlt
from qpysequence.program.instructions import Loop as LoopInstr
from qpysequence.program.instructions import Nop, Sub


class TestLoops:
    """Unitary tests checking the Waveforms class behavior"""

    def test_simple_loop(self):
        """Tests that simple loop instructions are generated correctly."""
        loop = Loop("simple_loop", 100)
        assert len(loop.builtin_components) == 1
        assert isinstance(loop.loop_instr, LoopInstr)
        assert loop.init_counter_instr.args[0] == 100

    def test_jlt_loop(self):
        """Tests that jlt loop instructions are generated correctly."""
        loop = Loop("jlt_loop", 3, 98, 7)
        assert len(loop.builtin_components) == 3
        assert isinstance(incr_instr := loop.builtin_components[0], Add)
        assert incr_instr.args[1] == 7
        assert isinstance(loop.loop_instr, Jlt)
        assert loop.loop_instr.args[1] == 98
        assert loop.init_counter_instr.args[0] == 3
        assert isinstance(loop.builtin_components[1], Nop)

    def test_jge_loop(self):
        """Tests that jge loop instructions are generated correctly."""
        loop = Loop("jge_loop", 100, 10, -8)
        assert isinstance(incr_instr := loop.builtin_components[0], Sub)
        assert incr_instr.args[1] == 8
        assert isinstance(loop.loop_instr, Jge)
        assert loop.loop_instr.args[1] == 11
        assert loop.init_counter_instr.args[0] == 100
        assert isinstance(loop.builtin_components[1], Nop)
