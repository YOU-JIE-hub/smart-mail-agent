# Offline stub for PyTorch (package form).
from __future__ import annotations

from contextlib import contextmanager

__all__ = [
    "cuda",
    "device",
    "load",
    "no_grad",
    "Tensor",
    "nn",
    "softmax",
    "dtype",
    "float32",
    "int64",
]


class _Cuda:
    @staticmethod
    def is_available() -> bool:
        return False


cuda = _Cuda()


def device(name: str):
    return name


def load(*args, **kwargs):
    raise RuntimeError("offline stub: torch.load unavailable")


@contextmanager
def no_grad():
    yield


class Tensor: ...


class _NN:
    class Module: ...


nn = _NN()


def softmax(x, dim=None):
    return x


class dtype: ...


float32 = dtype()
int64 = dtype()
