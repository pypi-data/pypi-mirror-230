from typing import Optional
from typing import Tuple

import numpy as np


class AawareInverseTransform:
    def __init__(self,
                 N: Optional[int] = None,
                 R: Optional[int] = None,
                 bin_start: Optional[int] = None,
                 bin_end: Optional[int] = None,
                 ttype: Optional[str] = None,
                 gain: Optional[np.float32] = None) -> None:
        import pyaaware

        self._it = pyaaware._InverseTransform()
        self._config = self._it.config()

        if N is not None:
            self._config.N = N

        if R is not None:
            self._config.R = R

        if bin_start is not None:
            self._config.bin_start = bin_start

        if bin_end is not None:
            self._config.bin_end = bin_end

        if ttype is not None:
            self._config.ttype = ttype

        if gain is not None:
            self._config.gain = gain

        self._it.config(self._config, False)
        self._bins = self._config.bin_end - self._config.bin_start + 1

    @property
    def N(self) -> int:
        return self._config.N

    @property
    def R(self) -> int:
        return self._config.R

    @property
    def bin_start(self) -> int:
        return self._config.bin_start

    @property
    def bin_end(self) -> int:
        return self._config.bin_end

    @property
    def ttype(self) -> str:
        return self._config.ttype

    @property
    def gain(self) -> np.float32:
        return self._config.gain

    @property
    def bins(self) -> int:
        return self._bins

    @property
    def W(self) -> np.ndarray:
        return self._it.W()

    def reset(self) -> None:
        self._it.reset()

    def execute_all(self, xf: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        assert xf.ndim == 3 or xf.ndim == 2

        has_channels = xf.ndim == 3
        bins = xf.shape[0]
        assert bins == self.bins

        if has_channels:
            channels = xf.shape[1]
            frames = xf.shape[2]
        else:
            channels = 1
            frames = xf.shape[1]

        samples = frames * self.R

        if has_channels:
            yt = np.empty((samples, channels), dtype=np.float32)
            energy_t = np.empty((channels, frames), dtype=np.float32)
        else:
            yt = np.empty(samples, dtype=np.float32)
            energy_t = np.empty(frames, dtype=np.float32)

        for channel in range(channels):
            for frame in range(frames):
                start = frame * self.R
                stop = start + self.R
                tmp = np.empty(self.R, dtype=np.float32)
                if has_channels:
                    self._it.execute(xf[:, channel, frame], tmp)
                    yt[start:stop, channel] = tmp
                    energy_t[channel, frame] = self._it.energy_t()
                else:
                    self._it.execute(xf[:, frame], tmp)
                    yt[start:stop] = tmp
                    energy_t[frame] = self._it.energy_t()
            self.reset()

        return yt, energy_t

    def execute(self, xf: np.ndarray) -> Tuple[np.ndarray, np.float32]:
        assert xf.ndim == 1
        assert xf.shape[0] == self.bins

        yt = np.empty(self.R, dtype=np.float32)
        self._it.execute(xf, yt)
        energy_t = self._it.energy_t()
        return yt, energy_t
