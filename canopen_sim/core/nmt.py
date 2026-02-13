# core/nmt.py
from enum import Enum

class NMTState(Enum):
    INITIALIZING = 0
    STOPPED = 4
    OPERATIONAL = 5
    PRE_OPERATIONAL = 127


class NMTCommand(Enum):
    START = 0x01
    STOP = 0x02
    ENTER_PRE_OP = 0x80
    RESET_NODE = 0x81
    RESET_COMM = 0x82
