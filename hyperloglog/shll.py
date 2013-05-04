"""
Sliding HyperLogLog
"""

import math
import heapq
from hashlib import sha1
from bisect import bisect_right
from itertools import chain

class SlidingHyperLogLog(object):
    """
    Sliding HyperLogLog: Estimating cardinality in a data stream (Telecom ParisTech)
    """

    __slots__ = ('window', 'alpha', 'b', 'm', 'LPFM', 'bitcount_arr')

    def __init__(self, error_rate, window):
        """
        Implementes a HyperLogLog

        error_rate = abs_err / cardinality
        """

        self.window = window
        if not (0 < error_rate < 1):
            raise ValueError("Error_Rate must be between 0 and 1.")

        # error_rate = 1.04 / sqrt(m)
        # m = 2 ** b

        b = int(math.ceil(math.log((1.04 / error_rate) ** 2, 2)))

        self.alpha = self._get_alpha(b)
        self.b = b
        self.m = 1 << b
        self.LPFM = [ [] for i in range(self.m) ]
        self.bitcount_arr = [ 1L << i for i in range(160 - b + 1) ]

    @staticmethod
    def _get_alpha(b):
        if not (4 <= b <= 16):
            raise ValueError("b=%d should be in range [4 : 16]" % b)

        if b == 4:
            return 0.673

        if b == 5:
            return 0.697

        if b == 6:
            return 0.709

        return 0.7213 / (1.0 + 1.079 / (1 << b))

    @staticmethod
    def _get_rho(w, arr):
        rho = len(arr) - bisect_right(arr, w)
        if rho == 0:
            raise ValueError('w overflow')
        return rho

    def add(self, timestamp, value):
        """
        Adds the item to the HyperLogLog
        """
        # h: D -> {0,1} ** 160
        # x = h(v)
        # j = <x_1x_2..x_b>
        # w = <x_{b+1}x_{b+2}..>
        # <t_i, rho(w)>

        x = long(sha1(value).hexdigest(), 16)
        j = x & ((1 << self.b) - 1)
        w = x >> self.b
        R = self._get_rho(w, self.bitcount_arr)

        Rmax = None
        tmp = []
        tmax = None
        tmp2 = list(heapq.merge(self.LPFM[j], [(timestamp, R)]))

        for t, R in reversed(tmp2):
                if tmax is None:
                    tmax = t

                if t < (tmax - self.window):
                    break

                if R > Rmax:
                    tmp.append((t, R))
                    Rmax = R

        tmp.reverse()
        self.LPFM[j] = tmp

    def update(self, *others):
        """
        Merge other counters
        """

        for item in others:
            if self.m != item.m:
                raise ValueError('Counters precisions should be equal')

        for j in xrange(len(self.LPFM)):
            Rmax = None
            tmp = []
            tmax = None
            tmp2 = list(heapq.merge(*([item.LPFM[j] for item in others] + [self.LPFM[j]])))

            for t, R in reversed(tmp2):
                if tmax is None:
                    tmax = t

                if t < (tmax - self.window):
                    break

                if R > Rmax:
                    tmp.append((t, R))
                    Rmax = R

            tmp.reverse()
            self.LPFM[j] = tmp

    def __eq__(self, other):
        if self.m != other.m:
            raise ValueError('Counters precisions should be equal')

        return self.LPFM == other.LPFM

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        raise NotImplemented

    def card(self, t, w=None):
        """
        Returns the estimate of the cardinality
        """
        if w is None:
            w = self.window

        if not 0 < w <= self.window:
            raise ValueError('0 < w <= W')

        M = [max(chain((R for ts, R in lpfm if ts >= (t - w)), iter([0]))) for lpfm in self.LPFM]
        E = self.alpha * float(self.m ** 2) / sum(math.pow(2.0, -x) for x in M)

        if E <= 2.5 * self.m:               # Small range correction
            #print 'Small corr'
            V = M.count(0)                  #count number or registers equal to 0
            return self.m * math.log(self.m / float(V)) if V > 0 else E
        elif E <= float(1L << 160) / 30.0:  #intermidiate range correction -> No correction
            #print 'No corr'
            return E
        else:
            #print 'Large corr'
            return -(1L << 160) * math.log(1.0 - E / (1L << 160))


