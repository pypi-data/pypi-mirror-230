from __future__ import annotations

import numpy as np

one_billion = int(1e9)


class TimeStamp:
    def __init__(
        self,
        sec: np.ndarray = np.zeros(
            1,
        ),
        nsec: np.ndarray = np.zeros(
            1,
        ),
    ):
        sec = np.asarray(sec)
        nsec = np.asarray(nsec)
        self.dtype = np.int64

        sec_int = sec + nsec / one_billion
        self.sec = (sec_int).astype(self.dtype)
        delta_nsec = np.round((sec - self.sec) * one_billion + nsec).astype(self.dtype)
        self.nsec = np.sign(delta_nsec) * (np.abs(delta_nsec) % one_billion)

    def as_seconds(self) -> np.ndarray:
        return self.sec + self.nsec / one_billion

    def __add__(self, other: TimeStamp) -> TimeStamp:
        nsec_add = self.nsec + other.getNanoSeconds()
        nsec_in_sec = (nsec_add / one_billion).astype(self.dtype)

        sec = self.sec + other.getSeconds() + nsec_in_sec
        nsec = nsec_add - (nsec_in_sec * one_billion).astype(self.dtype)
        return TimeStamp(sec, nsec)

    def __sub__(self, other: TimeStamp) -> TimeStamp:
        nsec_sub = np.asarray(self.nsec - other.getNanoSeconds())
        sec = np.asarray(self.sec - other.getSeconds()).astype(self.dtype)

        isNegative = nsec_sub < 0
        sec[isNegative] -= 1
        nsec = np.asarray(self.nsec).astype(self.dtype)
        nsec[isNegative] = one_billion + nsec_sub[isNegative]
        nsec[~isNegative] = nsec_sub[~isNegative]

        return TimeStamp(sec, nsec)

    def __lt__(self, other) -> np.ndarray:
        return np.asarray(self.sec <= other.getSeconds()) | np.asarray(
            self.nsec < other.getNanoSeconds()
        )

    def __le__(self, other) -> np.ndarray:
        return np.asarray(self.sec <= other.getSeconds()) | np.asarray(
            self.nsec <= other.getNanoSeconds()
        )

    def __gt__(self, other) -> np.ndarray:
        return np.asarray(self.sec >= other.getSeconds()) | np.asarray(
            self.nsec > other.getNanoSeconds()
        )

    def __ge__(self, other) -> np.ndarray:
        return np.asarray(self.sec >= other.getSeconds()) | np.asarray(
            self.nsec >= other.getNanoSeconds()
        )

    def __eq__(self, other) -> np.ndarray:
        return np.asarray(self.sec == other.getSeconds()) & np.asarray(
            self.nsec == other.getNanoSeconds()
        )

    def __ne__(self, other) -> np.ndarray:
        return not self.__eq__(other)

    def __abs__(self) -> np.ndarray:
        return TimeStamp(abs(self.sec), abs(self.nsec))

    def __repr__(self):
        s = self.as_seconds()
        if s.size == 1:
            tag = "seconds"
            if self.sec == 1 and self.nsec == 0:
                tag = "second"
            return f"{s} {tag}"
        elif s.size > 5:
            first_three = ", ".join([f"{si} sec" for si in s[:3]])
            last = f"{s[-1]} sec"
            return f"{first_three}, ..., {last}"
        else:
            return ", ".join([f"{si} sec" for si in s])

    def getSeconds(self) -> np.ndarray:
        return self.sec

    def getNanoSeconds(self) -> np.ndarray:
        return self.nsec

    def size(self) -> int:
        return self.sec.size

    def reshape(self, newshape, order="C") -> TimeStamp:
        return TimeStamp(
            self.sec.reshape(newshape, order=order),
            self.nsec.reshape(newshape, order=order),
        )

    def __len__(self) -> int:
        return self.size()

    def __getitem__(self, idx: int) -> TimeStamp:
        return TimeStamp(self.sec[idx], self.nsec[idx])

    def min(self, axis=None) -> TimeStamp:
        t = self.as_seconds()
        idx = np.argmin(t, axis=axis)
        return self.__getitem__(idx)

    def max(self, axis=None) -> TimeStamp:
        t = self.as_seconds()
        idx = np.argmax(t, axis=axis)
        return self.__getitem__(idx)
