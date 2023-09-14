# Stable modules:
import jax
import jax.numpy as jnp

# Custom Built Modules:
from tensorwrap.nn.layers import Layer

# General N-D Pool Layer

class PoolND(Layer):
    def __init__(self,
                 rank:int,
                 window_shape,
                 strides,
                 func,
                 padding: str = "valid",
                 name: str = "PoolND",
                 start_value = -jnp.inf,) -> None:
        super().__init__(name)
        self.rank = rank
        self.window_shape = window_shape
        self.strides = strides
        self.padding = padding.upper()
        self.func = func
        self.start_value = start_value
    
    def build(self, inputs):
        in_shape = jnp.shape(inputs)
        if len(in_shape) != self.rank + 2:
            raise ValueError(f"Data dimension doesn't equal to {self.rank + 2}.\n"
                             f"Data dimensions should be (batch_size, ..., depth).\n Current Shape: {in_shape}")
        if not jnp.array(jnp.array(in_shape) > 0).any():
            raise ValueError(f"Data shape isn't positive. Please reshape to have positive data shapes.")
        
        if len(self.window_shape) != self.rank:
            raise ValueError(f"Window dimensions isn't equal to {self.rank}."
                             f"Window dimensions should be (lenght, width, height, ...). \n Current shape: {in_shape}")
        self.window_shape = (1,) + self.window_shape + (1,)
        self.strides = (1,) + self.strides + (1,)

    def pool(self, inputs):
        return jax.lax.reduce_window(
            inputs,
            self.start_value,
            self.func,
            self.window_shape,
            self.strides,
            self.padding
        )

    def call(self, params, inputs):
        return self.pool(inputs)

# General N-D MaxPool Layer:
class MaxPoolND(PoolND):
    def __init__(self, rank: int, window_shape, strides, padding: str = "valid", name: str = "MaxPoolND") -> None:
        super().__init__(rank, window_shape, strides, jax.lax.max, padding, name)

# Common MaxPool Layers:

class MaxPool1D(MaxPoolND):
    def __init__(self,
                 window_shape,
                 strides, 
                 padding: str = "valid", 
                 name: str = "MaxPool1D") -> None:
        super().__init__(1, window_shape, strides, padding, name)

class MaxPool2D(MaxPoolND):
    def __init__(self,
                 window_shape,
                 strides, 
                 padding: str = "valid", 
                 name: str = "MaxPool2D") -> None:
        super().__init__(2, window_shape, strides, padding, name)

class MaxPool3D(MaxPoolND):
    def __init__(self,
                 window_shape,
                 strides, 
                 padding: str = "valid", 
                 name: str = "MaxPool3D") -> None:
        super().__init__(3, window_shape, strides, padding, name)