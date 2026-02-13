# od/od_entry.py

class ODEntry:
    def __init__(self, index, subindex, datatype, value, access="rw"):
        self.index = index
        self.subindex = subindex
        self.datatype = datatype
        self.value = value
        self.access = access

    def read(self):
        return self.value

    def write(self, value):
        if self.access == "ro":
            raise PermissionError("Object is read-only")
        self.value = value
