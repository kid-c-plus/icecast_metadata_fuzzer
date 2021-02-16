import string, re
from itertools import permutations

class Generator():
    # default input generation function
    def symbolFuzz(self):
        # fuzz all printable symbols
        charset = string.printable[62:]
        for length in range(1, 4):
            for perm in permutations(charset, length):
                yield ("".join(perm), "".join(perm).encode("unicode_escape").decode("utf-8"))
