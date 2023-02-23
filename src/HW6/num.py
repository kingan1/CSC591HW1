import math
from typing import Union

from options import options
from utils import rand, rint, per


class Num:
    """
    Summarizes a stream of numbers.
    """

    def __init__(self, at: int = 0, txt: str = ""):
        self.at = at
        self.txt = txt

        self.n = 0

        self.lo = math.inf
        self.hi = -math.inf
        self.ok = True
        self.has_ = {}

        self.w = -1 if self.txt.endswith("-") else 1

    def add(self, x, n: float = 1) -> None:
        """
        Adds n and updates lo, hi and stuff needed for standard deviation.

        :param n: Number to add
        :return: None
        """
        if x != "?":
            self.n += n

            self.lo, self.hi = min(x, self.lo), max(x, self.hi)

            all = len(self.has_)

            pos = all + 1 if all < options['Max'] else rint(1, all) if rand() < options['Max'] / self.n else 0

            if pos:
                self.has_[pos] = x
                self.ok = False

    def mid(self) -> float:
        """
        Returns mean of the numbers added to the stream.

        :return: Mean of the numbers
        """
        return per(self.has(), .5)

    def div(self) -> float:
        """
        Returns standard deviation of the numbers using Welford's algorithm.

        :return: Standard deviation of the numbers
        """
        return (per(self.has(), .9) - per(self.has(), .1)) / 2.58

    def has(self):
        ret = dict(sorted(self.has_.items(), key=lambda x: x[1]))
        self.ok = True
        return list(ret.values())
