# Stable Modules:
import jax
import jax.numpy as jnp

# Custom Built Modules:
from tensorwrap.nn.layers import Layer
from tensorwrap.nn.initializers import Initializer
from tensorwrap.nn.initializers import GlorotUniform, Zeros

__all__ = ["ConvND","Conv2D"]

# Borrowed Function:
def _convert_to_lax_conv_dimension_numbers(
    num_spatial_dims,
    data_format="channels_last",
    transpose=False,
):
    """Create a `lax.ConvDimensionNumbers` for the given inputs."""
    num_dims = num_spatial_dims + 2

    if data_format == "channels_last":
        spatial_dims = tuple(range(1, num_dims - 1))
        inputs_dn = (0, num_dims - 1) + spatial_dims
    else:
        spatial_dims = tuple(range(2, num_dims))
        inputs_dn = (0, 1) + spatial_dims

    if transpose:
        kernel_dn = (num_dims - 2, num_dims - 1) + tuple(range(num_dims - 2))
    else:
        kernel_dn = (num_dims - 1, num_dims - 2) + tuple(range(num_dims - 2))

    return jax.lax.ConvDimensionNumbers(
        lhs_spec=inputs_dn, rhs_spec=kernel_dn, out_spec=inputs_dn
    )

# Private Convolutional Implementation

class ConvND(Layer):
    def __init__(self,
                 rank:int, 
                 filter_no, 
                 filter_shape,
                 strides, 
                 padding="valid",
                 kernel_initializer: Initializer = GlorotUniform(),
                 bias_initializer: Initializer = Zeros(),
                 groups = 1, 
                 name: str = "Conv"):
        """Initializes a N-D Convolutional Layer that convolves the input.
        Arguments:
            - filter_no: The number of filters applied.
            - filter_shape: The size of each filter. It's dimensions are analogous to the rank.
            - strides: The incrementation of filter positioning. It's dimensions are analogous to the rank.
            - rank (int): The dimensionality of the convolutions.
            - name (Optional): Name of the layer.
        NOTE: Private Implementation of convolutions.
            """
        super().__init__(name + str(rank) + "D")
        self.rank = rank
        self.filter_no = filter_no
        self.filter_shape = filter_shape
        self.strides = strides
        self.padding = padding.upper()
        self.kernel_initializer = kernel_initializer
        self.bias_initializer = bias_initializer
        self.groups = 1
        self.check_parameters()
    
    def check_parameters(self):
        """Used to test all the values in the init function are valid.
        NOTE: For private use only.
        """
        pass

    def build(self, inputs):
        in_shape = jnp.shape(inputs)

        # Checking input shape validity:
        if len(in_shape) != self.rank + 2:
            raise ValueError(f"Data dimension doesn't equal to {self.rank + 2}.\n"
                             f"Data dimensions should be (batch_size, ..., depth).\n Current Image Shape: {in_shape}")
        
        if not jnp.array(jnp.array(in_shape) > 0).any():
            raise ValueError(f"Data shape isn't positive. Please reshape to have positive data shapes.")
        
        # Checking parameter validity:
        if in_shape[-1] % self.groups != 0:
            raise ValueError(
                "The input shape must be divisible by ``self.groups``."
                f"Current input shape {in_shape}."
                f"Current groups: {self.groups}"
            )

        kernel_shape = self.filter_shape + (
            in_shape[-1]//self.groups,
            self.filter_no
        )

        self.kernel = self.add_weights(shape=kernel_shape,
                                       initializer=self.kernel_initializer,
                                       name="kernel")
        self.bias = self.add_weights(shape=[self.filter_no],
                                     initializer=self.bias_initializer,
                                     name="bias")
        
        self.dn = _convert_to_lax_conv_dimension_numbers(inputs.ndim - 2)
        self.column = (1,) * (len(in_shape) - 2)

    
    def convolve(self, params, inputs):
        """Basic Convolution Operator."""
        return jax.lax.conv_general_dilated(
            inputs,
            params["kernel"],
            self.strides,
            self.padding,
            self.column,
            self.column,
            self.dn
        )
    
    @jax.jit
    def call(self, params, inputs):
        out = self.convolve(params, inputs)
        bias_shape = (1,) * (self.rank + 1) + (self.filter_no,)    
        return out + params["bias"].reshape(bias_shape)

# Some Daily Conv Uses:


class Conv1D(ConvND):
    def __init__(self, filter_no, filter_shape, strides = (1, 1), padding="VALID", kernel_initializer: Initializer = GlorotUniform(), bias_initializer: Initializer = Zeros(), groups=1, name: str = "Conv"):
        super().__init__(rank=1, 
                         filter_no=filter_no, 
                         filter_shape=filter_shape, 
                         strides=strides, 
                         padding=padding, 
                         kernel_initializer=kernel_initializer, 
                         bias_initializer=bias_initializer, 
                         groups=groups, 
                         name=name)

class Conv2D(ConvND):
    def __init__(self, filter_no, filter_shape, strides = (1, 1), padding="VALID", kernel_initializer: Initializer = GlorotUniform(), bias_initializer: Initializer = Zeros(), groups=1, name: str = "Conv"):
        super().__init__(rank=2, 
                         filter_no=filter_no, 
                         filter_shape=filter_shape, 
                         strides=strides, 
                         padding=padding, 
                         kernel_initializer=kernel_initializer, 
                         bias_initializer=bias_initializer, 
                         groups=groups, 
                         name=name)


# Depracated Convolutional Layer:

# class Conv2D(Layer):
#     def __init__(self, filter_no, filter_shape, strides = (1, 1), name: str = "Conv2D") -> None:
#         """Initializes a 2-D Convolutional Layer that convolves the input.
#         Arguments:
#             - filter_no: The number of filters applied.
#             - filter_shape: The size of each filter. It is two dimensional.
#             - strides: The incrementation of filter positioning. It is two dimensional
#             - name (Optional): Name of the layer. Defaults to "Conv2D"."""
#         super().__init__(name=name)
#         self.filter_no = filter_no
#         self.shape = filter_shape
#         self.strides = strides

#     def build(self, inputs):
#         in_shape = jnp.shape(inputs)
#         if len(in_shape) != 4:
#             raise ValueError(f"Data dimension doesn't equal to 4.\n"
#                              f"Data Dimensions should be (batch_size, length, width, depth).\n Current Image Shape: {in_shape}")
#         if in_shape[1] < self.shape[0] or in_shape[2] < self.shape[1]:
#             raise ValueError("Image size cannot be smaller than filter size.")
        
#         self.out_shape = [in_shape[0], 0, 0]
#         for i in range(1, 3):
#             self.out_shape[i] = int((lambda x, y, z: (x - y)/z + 1) (in_shape[i], self.shape[i-1], self.strides[i-1]))
        
#         for i in range(self.filter_no):
#             self.kernel = self.add_weights(self.shape, name="filter:"+str(i))

#     @staticmethod
#     def convolve(feature_map, inputs, filters, out_shape, filter_shape, strides):
#         for i in range(out_shape[1]):
#             for y in range(out_shape[2]):
#                 segment = inputs[inputs.shape[0], i:filter_shape[0] + strides[0]*i, y: filter_shape[1] + strides[1]*y, -1]
#                 product = segment * filters
#                 sum = jnp.sum(product)
#                 feature_map = feature_map.at[-1, i, y].set(sum)
#         return feature_map
    
#     @jax.jit
#     def call(self, params, inputs):
#         maps = []
#         for filters in range(len(params.values())):
#             feature_map = jnp.zeros(self.out_shape)
#             feature_map = self.convolve(feature_map, inputs, params["filter:"+str(filters)], self.out_shape, self.shape, self.strides)
#             maps.append(feature_map)
#         return jnp.stack(maps, axis=3)