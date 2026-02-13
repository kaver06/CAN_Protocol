# od/object_dictionary.py

class ObjectDictionary:
    def __init__(self):
        self.entries = {}

    def add(self, entry):
        key = (entry.index, entry.subindex)
        self.entries[key] = entry

    def read(self, index, subindex):
        return self.entries[(index, subindex)].read()

    def write(self, index, subindex, value):
        self.entries[(index, subindex)].write(value)
