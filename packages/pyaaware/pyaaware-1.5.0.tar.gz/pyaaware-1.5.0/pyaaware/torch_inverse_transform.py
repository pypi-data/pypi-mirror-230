from typing import Tuple

import torch


class TorchInverseTransform:
    def __init__(self,
                 N: int = 256,
                 R: int = 64,
                 bin_start: int = 1,
                 bin_end: int = 128,
                 ttype: str = 'stft-olsa-hanns',
                 gain: torch.float32 = 1) -> None:
        import numpy as np

        from pyaaware.transform_types import Overlap
        from pyaaware.transform_types import Window
        from pyaaware.transform_types import window

        self._N = N
        self._R = R
        self._bin_start = bin_start
        self._bin_end = bin_end
        self._ttype = ttype
        self._gain = gain

        if self.N % self.R:
            raise ValueError('R is not a factor of N')

        if self.bin_start >= self.N:
            raise ValueError('bin_start is greater than N')

        if self.bin_end >= self.N:
            raise ValueError('bin_end is greater than N')

        if self.bin_start >= self.bin_end:
            raise ValueError('bin_start is greater than bin_end')

        self._real_mode = self.bin_end <= self.N // 2
        self._cj_indices = list(range(self.N // 2 + 1, self.N))
        self._i_indices = list(range(int(np.ceil(self.N / 2)) - 1, 0, -1))
        self._ob_indices = list(range(self.N - self.R, self.N))
        self._bin_indices = list(range(self.bin_start, self.bin_end + 1))
        self._bins = self.bin_end - self.bin_start + 1

        self._W = None
        self._overlap_type = None
        self._xfs = None
        self._pyo = None

        if self.ttype == 'stft-olsa-hanns':
            self._W = window(Window.HANN01, self.N, self.R)
            itr_user_gain = self.N / 2
            self._overlap_type = Overlap.OLA
        elif self.ttype == 'stft-ols':
            self._W = window(Window.RECT, self.N, self.R)
            itr_user_gain = self.N ** 2 / self.R / 2
            self._overlap_type = Overlap.OLS
        elif self.ttype == 'stft-olsa':
            self._W = window(Window.W01, self.N, self.R)
            itr_user_gain = self.N / 2
            self._overlap_type = Overlap.OLA
        elif self.ttype == 'stft-olsa-hann':
            self._W = window(Window.RECT, self.N, self.R)
            itr_user_gain = self.N / 2
            self._overlap_type = Overlap.OLA
        elif self.ttype == 'stft-olsa-hannd':
            self._W = window(Window.HANN, self.N, self.R)
            itr_user_gain = self.N / 3
            self._overlap_type = Overlap.OLA
        elif self.ttype == 'stft-olsa-hammd':
            self._W = window(Window.HAMM, self.N, self.R)
            itr_user_gain = self.N / 2.72565243
            self._overlap_type = Overlap.OLA
        elif self.ttype == 'stft-ola':
            self._W = window(Window.RECT, self.N, self.R)
            itr_user_gain = self.N ** 2 / self.R / 2
            self._overlap_type = Overlap.OLA
        else:
            raise ValueError(f"Unknown ttype: '{self.ttype}'")

        if len(self._W) != self.N:
            raise RuntimeError('W is not of length N')

        wdc_gain = torch.sum(self._W)
        o_gain = 1 / (self.gain * wdc_gain / self.R) * itr_user_gain
        self._W = self._W * o_gain

        self.reset()

    @property
    def N(self) -> int:
        return self._N

    @property
    def R(self) -> int:
        return self._R

    @property
    def bin_start(self) -> int:
        return self._bin_start

    @property
    def bin_end(self) -> int:
        return self._bin_end

    @property
    def ttype(self) -> str:
        return self._ttype

    @property
    def gain(self) -> torch.float32:
        return self._gain

    @property
    def bins(self) -> int:
        return self._bins

    @property
    def W(self) -> torch.Tensor:
        return self._W

    def reset(self) -> None:
        self._xfs = torch.zeros(self.N, dtype=torch.complex64)
        self._pyo = torch.zeros(self.N, dtype=torch.float32)

    def execute_all(self, xf: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        if xf.ndim != 3 and xf.ndim != 3:
            raise ValueError('Input must have either 2 or 3 dimensions')

        has_channels = xf.ndim == 3
        bins = xf.shape[0]

        if bins != self.bins:
            raise ValueError(f'Input must have {self.bins} bins')

        if has_channels:
            channels = xf.shape[1]
            frames = xf.shape[2]
        else:
            channels = 1
            frames = xf.shape[1]

        samples = frames * self.R

        if has_channels:
            yt = torch.empty((samples, channels), dtype=torch.float32)
            energy_t = torch.empty((channels, frames), dtype=torch.float32)
        else:
            yt = torch.empty(samples, dtype=torch.float32)
            energy_t = torch.empty(frames, dtype=torch.float32)

        for channel in range(channels):
            self.reset()
            for frame in range(frames):
                start = frame * self.R
                stop = start + self.R
                if has_channels:
                    yt[start:stop, channel], energy_t[channel, frame] = self.execute(xf[:, channel, frame])
                else:
                    yt[start:stop, frame], energy_t[frame] = self.execute(xf[:, frame])

        return yt, energy_t

    def execute(self, xf: torch.Tensor) -> Tuple[torch.Tensor, float]:
        from pyaaware.transform_types import Overlap

        if xf.ndim != 1 or xf.shape[0] != self.bins:
            raise ValueError(f'Input shape must be a vector of length {self.bins}')

        self._xfs[self._bin_indices] = xf
        if self._real_mode:
            self._xfs[self._cj_indices] = torch.conj(self._xfs[self._i_indices])

        if not self.N % 2:
            self._xfs[self.N // 2].imag = 0

        if self._overlap_type == Overlap.OLA:
            tmp = self.W * torch.fft.irfft(self._xfs, n=self.N) + self._pyo
            self._pyo[0:(self.N - self.R)] = tmp[self.R:]
            yt = tmp[0:self.R]
        elif self._overlap_type == Overlap.OLS:
            tmp = self.W * torch.fft.irfft(self._xfs, n=self.N)
            yt = tmp[self._ob_indices]
        else:
            raise ValueError(f"Unsupported overlap type: '{self._overlap_type}")

        energy_t = torch.mean(torch.square(yt))
        return yt, float(energy_t)
