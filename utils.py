from itertools import combinations
from queue import Queue


class AddOnceQueue:
    def __init__(self):
        self.queue: Queue[int] = Queue()
        self.set: set[int] = set()

    def add(self, item: int) -> int:
        if not item in self.set:
            self.set.add(item)
            self.queue.put(item)
            return 1
        return 0

    def dequeue(self) -> int | None:
        if not self.queue.empty():
            return self.queue.get()
        return None

    @property
    def empty(self) -> bool:
        return self.queue.empty()

    @property
    def count(self):
        return self.queue.qsize()


def bstr8(number: int, hi_z_mask: int = 0) -> str:
    binary_str = f"{number:08b}"
    mask_str = f"{hi_z_mask:08b}"
    result_str = "".join("Z" if mask_str[i] == "1" else binary_str[i] for i in range(8))
    return f"{result_str[:3]}_{result_str[3:7]}_{result_str[7:8]}"


def bstr18(number: int, hi_z_mask: int = 0):
    binary_str = f"{number:018b}"
    mask_str = f"{hi_z_mask:018b}"
    result_str = "".join(
        "Z" if mask_str[i] == "1" else binary_str[i] for i in range(18)
    )
    return f"{result_str[:2]}_{result_str[2:8]}_{result_str[8:]}"


def bcpl18(number: int):
    mask = (1 << 18) - 1
    return number ^ mask


def bcomb(number: int):
    # get positions of all "1" bits in the binary representation of the number
    ones_positions = [i for i in range(number.bit_length()) if number & (1 << i)]
    # generate all subsets of these positions
    combinations_list = []
    for r in range(len(ones_positions) + 1):
        combinations_list.extend(combinations(ones_positions, r))
    # generate numbers for each subset
    results = []
    for subset in combinations_list:
        new_number = number
        for pos in subset:
            new_number &= bcpl18(1 << pos)  # set the bit at position "pos" to 0
        results.append(new_number)
    return sorted(results)
