from tensorwrap.nn.losses import Loss
from jax import numpy as jnp

__all__ = ["mse", "mae"]

class MeanSquaredError(Loss):
    def __init__(self) -> None:
        super().__init__()
        pass

    def call(self, y_pred, y_true):
        return jnp.mean((y_true - y_pred)**2)

class MeanAbsoluteError(Loss):
    def __init__(self) -> None:
        super().__init__()
        pass

    def call(self, y_pred, y_true):
        return jnp.mean(jnp.abs(y_true - y_pred))

# Inspection Fixes:
MeanSquaredError.__module__ = "tensowrap.nn.losses"
MeanAbsoluteError.__module__ = "tensorwrap.nn.losses"


# Adding proper names:
MeanSquaredError.__repr__ = "<function mse>"
MeanAbsoluteError.__repr__ = "<function mae>"