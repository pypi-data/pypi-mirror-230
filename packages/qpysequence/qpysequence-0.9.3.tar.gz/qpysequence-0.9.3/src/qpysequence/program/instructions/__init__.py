""" Instructions Initialization """

from .arithmetic import Add, And, Asl, Asr, Move, Not, Or, Sub, Xor
from .conditional import SetCond
from .control import Illegal, Nop, Stop
from .instruction import Instruction
from .jumps import Jge, Jlt, Jmp, Loop
from .parameter_operations import ResetPh, SetAwgGain, SetAwgOffs, SetFreq, SetMrk, SetPh, SetPhDelta
from .real_time import (
    Acquire,
    AcquireTtl,
    AcquireWeighed,
    SetLatchEn,
    LatchRst,
    Play,
    UpdParam,
    Wait,
    WaitSync,
    WaitTrigger,
)
