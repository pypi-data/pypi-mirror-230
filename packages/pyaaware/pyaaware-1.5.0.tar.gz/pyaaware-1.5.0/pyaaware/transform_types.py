from enum import Enum
from typing import Protocol

import numpy as np
import torch


class Overlap(Enum):
    OLA = 'OLA'
    OLS = 'OLS'


class Window(Enum):
    RECT = 'rect'
    HANN = 'hann'
    HAMM = 'hamm'
    W01 = 'w01'
    HANN01 = 'hann01'


def window(window_type: Window, N: int, R: int, periodic: bool = True) -> torch.Tensor:
    """Generate window

    :param window_type: Window type
    :param N: Transform length
    :param R: Overlap amount
    :param periodic: Window is periodic if True, otherwise it is symmetric
    :return: window [N]
    """
    sym = not periodic

    if window_type == Window.RECT:
        return torch.ones(N, dtype=torch.float32)

    if window_type == Window.HANN:
        return torch.signal.windows.hann(M=N, sym=sym, dtype=torch.float32)

    if window_type == Window.HAMM:
        return torch.signal.windows.hamming(M=N, sym=sym, dtype=torch.float32)

    if window_type == Window.W01:
        if not (N / R) % 2:
            return torch.concatenate((torch.zeros(N // 2, dtype=torch.float32),
                                      torch.ones(N // 2, dtype=torch.float32)))
        else:
            return torch.concatenate((torch.zeros(N - R, dtype=torch.float32),
                                      torch.ones(R, dtype=torch.float32)))

    if window_type == Window.HANN01:
        if R > (N // 4):
            raise ValueError(f'{window_type} window requires R <= N/4')
        if N / 2 % 2:
            raise ValueError(f'{window_type} window requires N to be even')
        return torch.concatenate((torch.zeros(N // 2, dtype=torch.float32),
                                  torch.signal.windows.hann(M=N // 2, sym=sym, dtype=torch.float32)))

    raise ValueError(f'Unknown window type: {window_type}')


class ForwardTransform(Protocol):
    @property
    def N(self) -> int:
        ...

    @property
    def R(self) -> int:
        ...

    @property
    def bin_start(self) -> int:
        ...

    @property
    def bin_end(self) -> int:
        ...

    @property
    def ttype(self) -> str:
        ...

    @property
    def bins(self) -> int:
        ...

    @property
    def W(self) -> np.ndarray:
        ...

    def reset(self) -> None:
        ...

    def execute_all(self, xt: np.ndarray) -> (np.ndarray, np.ndarray):
        ...

    def execute(self, xt: np.ndarray) -> (np.ndarray, np.float32):
        ...


class InverseTransform(Protocol):
    @property
    def N(self) -> int:
        ...

    @property
    def R(self) -> int:
        ...

    @property
    def bin_start(self) -> int:
        ...

    @property
    def bin_end(self) -> int:
        ...

    @property
    def ttype(self) -> str:
        ...

    @property
    def gain(self) -> np.float32:
        ...

    @property
    def bins(self) -> int:
        ...

    @property
    def W(self) -> np.ndarray:
        ...

    def reset(self) -> None:
        ...

    def execute_all(self, xf: np.ndarray) -> (np.ndarray, np.ndarray):
        ...

    def execute(self, xf: np.ndarray) -> (np.ndarray, np.float32):
        ...
