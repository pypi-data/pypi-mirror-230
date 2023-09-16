from typing import List
from typing import Optional
from typing import Tuple

import numpy as np


class NNPDetect:
    def __init__(self,
                 channels: Optional[int] = None,
                 classes: Optional[int] = None,
                 risethresh: Optional[List[np.float32]] = None,
                 fallthresh: Optional[List[np.float32]] = None,
                 riseframes: Optional[List[int]] = None,
                 fallframes: Optional[List[int]] = None,
                 hold: Optional[List[int]] = None,
                 smoothf: Optional[List[np.float32]] = None) -> None:
        import pyaaware

        self._nnp_detect = pyaaware._NNPDetect()
        self._config = self._nnp_detect.config()

        if channels is not None:
            self._config.channels = channels

        if classes is not None:
            self._config.classes = classes

        if risethresh is not None:
            self._config.risethresh = risethresh

        if fallthresh is not None:
            self._config.fallthresh = fallthresh

        if riseframes is not None:
            self._config.riseframes = riseframes

        if fallframes is not None:
            self._config.fallframes = fallframes

        if hold is not None:
            self._config.hold = hold

        if smoothf is not None:
            self._config.smoothf = smoothf

        self._nnp_detect.config(self._config)

    @property
    def channels(self) -> int:
        return self._config.channels

    @property
    def classes(self) -> int:
        return self._config.classes

    @property
    def risethresh(self) -> List[np.float32]:
        return self._config.risethresh

    @property
    def fallthresh(self) -> List[np.float32]:
        return self._config.fallthresh

    @property
    def riseframes(self) -> List[int]:
        return self._config.riseframes

    @property
    def fallframes(self) -> List[int]:
        return self._config.fallframes

    @property
    def hold(self) -> List[int]:
        return self._config.hold

    @property
    def smoothf(self) -> List[np.float32]:
        return self._config.smoothf

    def reset(self):
        self._nnp_detect.reset()

    def execute_all(self, x: np.ndarray, eof: np.ndarray, get_smooth: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        assert x.ndim == 3
        assert x.shape[0] == self.channels
        assert x.shape[1] == self.classes
        frames = x.shape[2]

        assert eof.ndim == 1
        assert eof.shape[0] == frames

        y = np.empty((self.channels, self.classes, frames), dtype=int)
        smooth = np.empty((self.channels, self.classes, frames), dtype=np.float32)
        for in_idx in range(frames):
            y[:, :, in_idx] = self._nnp_detect.execute(x[:, :, in_idx], bool(eof[in_idx]))
            if get_smooth:
                smooth[:, :, in_idx] = self._nnp_detect.smooth()

        return y, smooth

    def execute(self, x: np.ndarray, eof: bool) -> np.ndarray:
        assert x.ndim == 2
        assert x.shape[0] == self.channels
        assert x.shape[1] == self.classes

        return self._nnp_detect.execute(x, eof)

    def smooth(self) -> np.ndarray:
        return self._nnp_detect.smooth()
