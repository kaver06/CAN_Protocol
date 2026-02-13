# od/datatypes.py

class ODType:
    def __init__(self, size):
        self.size = size  # bytes

UNSIGNED8  = ODType(1)
UNSIGNED16 = ODType(2)
UNSIGNED32 = ODType(4)

