"""Sequence module"""

from qpysequence.acquisitions import Acquisitions
from qpysequence.program import Program
from qpysequence.waveforms import Waveforms
from qpysequence.weights import Weights


class Sequence:
    """Sequence class. Its string representation can be obtained with the `repr()` method and be directly fed to a
    Qblox sequencer.

        Args:
            program (Program): Program of the sequence.
            waveforms (dict): Waveforms dictionary.
            acquisitions (dict): Acquisitions dictionary.
            weights (dict): Weights dictionary.
    """

    def __init__(self, program: Program, waveforms: Waveforms, acquisitions: Acquisitions, weights: Weights):
        self._program: Program = program
        self._waveforms: Waveforms = waveforms
        self._acquisitions: Acquisitions = acquisitions
        self._weights: Weights = weights

    def todict(self) -> dict:
        """JSON representation of the Sequence.

        Returns:
            dict: JSON representation of the sequence.
        """
        return {
            "waveforms": self._waveforms.to_dict(),
            "weights": self._weights.to_dict(),
            "acquisitions": self._acquisitions.to_dict(),
            "program": repr(self._program),
        }

    def __repr__(self) -> str:
        """String representation of the Sequence as JSON.
        It can be converted to json and used as a direct input for the Qblox devices.

        Returns:
            str: String representation of the sequence.
        """
        return str(self.todict())
