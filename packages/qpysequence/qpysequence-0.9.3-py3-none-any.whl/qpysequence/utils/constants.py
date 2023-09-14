"""Constants"""

# Prefix for a Q1ASM register identifier (prefix + number).
PROG_REG_PREFIX = "R"
# Maximum number of registers in a program
PROG_MAX_REGISTERS = 64
# Minimum wait in nanoseconds for an instruction with a wait parameter
INST_MIN_WAIT = 4
# Maximum wait in nanoseconds for an instruction with a wait parameter
INST_MAX_WAIT = 2**16 - 4
# Maximum value of the NCO phase (equivalent to 360º).
NCO_MAX_INT_PHASE = int(1e9)
# Minimum int representation value of the NCO frequency (used by Q1ASM instructions).
NCO_MIN_INT_FREQ = int(-2e9)
# Maximum int representation value of the NCO frequency (used by Q1ASM instructions).
NCO_MAX_INT_FREQ = int(2e9)
# Minimum value the NCO frequency in Hz.
NCO_MIN_HZ_FREQ = int(-0.5e9)
# Maximum value the NCO frequency in Hz.
NCO_MAX_HZ_FREQ = int(0.5e9)
# Maximum gain of the Arbitrary Waveform Generator
AWG_MAX_GAIN = 2**15 - 1
# Maximum value for an immediate argument type
IMMD_MAX_VALUE = 2**32 - 1
# Number of markers in a sequencer
SEQ_N_MARKERS = 4
# Step of waiting times for sequencer instructions
SEQ_WAIT_STEP = 4
# Maximum value of a mask used in latch instructions
MASK_MAX_VALUE = 2**15 - 1
