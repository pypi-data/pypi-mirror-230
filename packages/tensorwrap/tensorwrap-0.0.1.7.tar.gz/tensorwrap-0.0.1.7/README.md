# TensorWrap

![](https://github.com/Impure-King/base-tensorwrap/blob/main/Images/TensorWrap.gif)

# TensorWrap - A full-fledged Deep Learning Library based on JAX and TensorFlow.

![PyPI version](https://img.shields.io/pypi/v/tensorwrap)

| [**Install guide**](#installation)


## What is TensorWrap?

TensorWrap is high performance neural network library that acts as a wrapper around [JAX](https://github.com/google/jax) (another high performance machine learning library), bringing the familiar elements of the [TensorFlow](https://tensorflow.org) (2.x.x). This is currently aimed towards prototyping over deployment, in the current state. 

TensorWrap works by creating a layer of abstraction over JAX's low level api and introducing similar TensorFlow-like component's while supporting its own explicit and magic free design philosophy. This allows TensorWrap to be fast and efficient, while remaining nearly fully compatible with all custom operations and other tools from the JAX ecosystem. Additionally, this library adds additional features and leverages JAX's optimizations, making it more friendly towards research and educational audiences.

This is a personal project, not professionally affliated with Google in any way. Expect bugs and several incompatibilities/difference from the original libraries.
Please help by trying it out, [reporting
bugs](https://github.com/Impure-King/base-tensorwrap/issues), and letting me know what you
think!

### Contents
* [Examples](#Examples)
* [Current gimmicks](#current-gimmicks)
* [Installation](#installation)
* [Neural net libraries](#neural-network-libraries)
* [Citations](#citations)
* [Reference documentation](#reference-documentation)


### Examples

1) Custom Layers
```python
import tensorwrap as tf
from tensorwrap import nn

class Dense(nn.layers.Layer):
    def __init__(self, units) -> None:
        super().__init__() # Needed for tracking trainable_variables.
        self.units = units # Defining the output shape
  
    def build(self, input_shape: tuple) -> None:
        super().build() # Required for letting model know that layer is built.
        input_shape = tf.shape(input_shape) # Getting appropriate input shape
        
        # Naming each parameter to later access from model.trainable_variables
        self.kernel = self.add_weights([input_shape, self.units],
                                       initializer = 'glorot_uniform',
                                       name='kernel')
        self.bias = self.add_weights([self.units],
                                     initializer = 'zeros',
                                     name='bias')
        
    
    # Use call not __call__ to define the flow. To support JIT compilation, we use staticmethod.
    @staticmethod
    @tf.function
    def call(params, inputs):
        return inputs @ params['kernel'] + params['bias'] # Using params as an input, allows use to pass in the model.trainable_variables later.
 ```

2) Just In Time Compiling with tf.function
```python
import tensorwrap as tf
from tensorwrap import nn
tf.test.is_device_available(device_type = 'cuda')

@tf.function
def mse(y_pred, y_true):
    return tf.mean(tf.square(y_pred - y_true))

print(mse(100, 102))
```
3) Custom Models
```python 
import tensorwrap as tf
from tensorwrap import nn

class Sequential(nn.Model):
    def __init__(self, layers: list) -> None:
        super().__init__(name = "Sequential") # Starts the tracking of internal variables. Allows for name definition.
        self.layers = layers

    def __call__(self, inputs):
        x = inputs
        for layer in self.layers:
            x = layer(x)
        return x

model = Sequential([
    nn.layers.Dense(100),
    nn.layers.Dense(10)
])
```


### Current Gimmicks
1. Current models are all compiled by JAX's internal jit, so any error may remain a bit more cryptic than PyTorchs. However, this problem is still being worked on.

2. Also, using ``tensorwrap.Module`` is currently not recommended, since other superclasses offer more functionality and ease of use.

3. Graph execution is currently not available, which means that all exported models can only be deployed within a python environment.



### Installation

The device installation of TensorWrap depends on its backend, being JAX. Thus, our normal install will be covering only the cpu version. For gpu version, please check [JAX](https://github.com/google/jax)'s documentation.

```bash
pip install --upgrade pip
pip install --upgrade tensorwrap
```

On Linux, it is often necessary to first update `pip` to a version that supports
`manylinux2014` wheels. Also note that for Linux, we currently release wheels for `x86_64` architectures only, other architectures require building from source. Trying to pip install with other Linux architectures may lead to `jaxlib` not being installed alongside `jax`, although `jax` may successfully install (but fail at runtime). 
**These `pip` installations do not work with Windows, and may fail silently; see
[above](#installation).**

**Note**

If any problems occur with cuda installation, please visit the [JAX](https://github.com/google/jax#installation) github page, in order to understand the problem with lower API installation.

## Citations

This project have been heavily inspired by __TensorFlow__ and once again, is built on the open-source machine learning XLA framework __JAX__. Therefore, I recognize the authors of JAX and TensorFlow for the exceptional work they have done and understand that my library doesn't profit in any sort of way, since it is merely an add-on to the already existing community.

```
@software{jax2018github,
  author = {James Bradbury and Roy Frostig and Peter Hawkins and Matthew James Johnson and Chris Leary and Dougal Maclaurin and George Necula and Adam Paszke and Jake Vander{P}las and Skye Wanderman-{M}ilne and Qiao Zhang},
  title = {{JAX}: composable transformations of {P}ython+{N}um{P}y programs},
  url = {http://github.com/google/jax},
  version = {0.3.13},
  year = {2018},
}
```
## Reference documentation

For details about the TensorWrap API, see the
[main documentation] (coming soon!)

For details about JAX, see the
[reference documentation](https://jax.readthedocs.io/).

For documentation on TensorFlow API, see the
[API documentation](https://www.tensorflow.org/api_docs/python/tf)
