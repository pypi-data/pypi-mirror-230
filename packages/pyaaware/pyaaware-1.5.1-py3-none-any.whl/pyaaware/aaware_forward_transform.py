from typing import Optional
from typing import Tuple

import numpy as np


class AawareForwardTransform:
    def __init__(self,
                 N: Optional[int] = None,
                 R: Optional[int] = None,
                 bin_start: Optional[int] = None,
                 bin_end: Optional[int] = None,
                 ttype: Optional[str] = None) -> None:
        import pyaaware

        self._ft = pyaaware._ForwardTransform()
        self._config = self._ft.config()

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

        self._ft.config(self._config, False)
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
    def bins(self) -> int:
        return self._bins

    @property
    def W(self) -> np.ndarray:
        return self._ft.W()

    def reset(self) -> None:
        self._ft.reset()

    def execute_all(self, xt: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        assert xt.ndim == 2 or xt.ndim == 1

        has_channels = xt.ndim == 2
        samples = xt.shape[0]
        frames = int(np.ceil(samples / self.R))

        if has_channels:
            channels = xt.shape[1]
            xt_pad = np.pad(xt, ((0, frames * self.R - samples), (0, 0)), 'constant')
            yf = np.empty((self.bins, channels, frames), dtype=np.complex64)
            energy_t = np.empty((channels, frames), dtype=np.float32)
        else:
            channels = 1
            xt_pad = np.pad(xt, (0, frames * self.R - samples), 'constant')
            yf = np.empty((self.bins, frames), dtype=np.complex64)
            energy_t = np.empty(frames, dtype=np.float32)

        for channel in range(channels):
            for frame in range(frames):
                start = frame * self.R
                stop = start + self.R
                tmp = np.empty(self.bins, dtype=np.complex64)
                if has_channels:
                    self._ft.execute(xt_pad[start:stop, channel], tmp)
                    yf[:, channel, frame] = tmp
                    energy_t[channel, frame] = self._ft.energy_t()
                else:
                    self._ft.execute(xt_pad[start:stop], tmp)
                    yf[:, frame] = tmp
                    energy_t[frame] = self._ft.energy_t()
            self.reset()

        return yf, energy_t

    def execute(self, xt: np.ndarray) -> Tuple[np.ndarray, np.float32]:
        assert xt.ndim == 1
        assert xt.shape[0] == self.R

        yf = np.empty(self.bins, dtype=np.complex64)
        self._ft.execute(xt, yf)
        energy_t = self._ft.energy_t()
        return yf, energy_t
