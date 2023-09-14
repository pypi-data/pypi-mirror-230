"""TensorWrap is a high level nueral net library that aims to provide prebuilt models,
layers, and losses on top of JAX. It aims to allow for faster prototyping, intuitive solutions,
and a coherent workflow while maintaining the benefits/compatibility with JAX.

With the expansion of the project, TensorWrap will also be able to develop a production system,
enabling JAX models to deploy outside of the python environment as well. Therefore, the current
version only supports prototyping and efficiency.
"""

# JAX Built-ins:
from jax import disable_jit, grad, value_and_grad, custom_gradient
from jax import vmap as vectorized_map
from jax.numpy import *
from jax.numpy import asarray as convert_to_tensor
from jax.numpy import array as tensor
from jax.numpy import eye as identity
from jax.numpy import arange as range
from jax.numpy import concatenate as concat

# Library Paths:
from tensorwrap import nn

# Fast Loading Modules:
from tensorwrap import config, experimental
from tensorwrap.experimental.serialize import load_model, save_model
from tensorwrap.experimental.wrappers import function

# Path Shortener:

from tensorwrap.ops import last_dim, randn, randu

# Fast Loading Modules:
from tensorwrap.module import Module
from tensorwrap.version import __version__
