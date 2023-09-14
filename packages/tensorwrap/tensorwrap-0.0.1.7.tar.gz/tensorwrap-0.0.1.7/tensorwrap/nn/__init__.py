""" This is the Keras API of TensorWrap, which aims to offer a similar
API as tf.keras from TensorFlow. It contains neural network modules that are
contained in the original Keras API and aims to simplify computing and prototyping."""

# Integrated Libraries:
import optax as optimizers

# Import Libraries:
from tensorwrap.nn import activations, callbacks, initializers, losses, layers, models


# Path Shorteners:
from .models.base_models import Model, Sequential

# Deprecated Modules:
# from tensorwrap.nn import optimizers