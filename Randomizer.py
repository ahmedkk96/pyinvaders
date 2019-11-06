import random


class Weighted:
    def __init__(self):
        self.items = {}
        self.total_weight = 0
        self._index = 0

    def append(self, key, weight):
        self.items[self._index] = (key, weight)
        self.total_weight += weight
        self._index += 1

    def roll(self):
        r = random.randrange(self.total_weight)
        cur_weight = 0
        for item, weight in self.items.values():
            cur_weight += weight
            if r < cur_weight:
                return item

        raise Exception('Something is wrong!')

    def count(self):
        return len(self.items)


def Bool(chance=0.2):
        r = random.randint(0, 100)
        max_val = 100 * chance
        return r < max_val
