import pytest

from qpysequence.acquisitions import Acquisitions
from qpysequence.program import Program
from qpysequence.sequence import Sequence
from qpysequence.waveforms import Waveforms
from qpysequence.weights import Weights


@pytest.fixture
def qpysequence():
    """_summary_

    Returns:
        _type_: _description_
    """
    return Sequence(Program(), Waveforms(), Acquisitions(), Weights())


class TestQPySequence:
    """Unitary tests checking the QPySequence initialization steps and values"""

    def test_qpysequence_constructor(self, qpysequence):
        """_summary_

        Args:
            qpysequence (_type_): _description_
        """
        assert isinstance(qpysequence, Sequence)
