""" This is the activation's module for TensorWrap"""

import tensorwrap as tf
from tensorwrap.module import Module

__all__ = ["Activation", "ReLU"]

# Base Activation Class:

class Activation(Module):
    """A superclass for defining custom activation functions.
    
    Instructions:
        This class serves as the base for implementing custom activation functions.
        Subclasses should override the `call` method to define control flow of 
        the activation function.
    """
    
    # Tracks Name with some id
    __layer_tracker = 0
    
    def __init__(self, name:str = "Activation"):
        """
        Arguments:
            name (string, Optional): The name of the activation function. Defaults to "Activation".
        
        NOTE: Include ``super().__init__()``
        """
        # Creating a name for the layer.
        self.name = name + ':' + str(Activation.__layer_tracker)
        Activation.__layer_tracker += 1
    
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        # overriding __call__ function for conventions:
        cls.__call__ = cls.call

    def call(self, params, inputs):
        """
        This method should be overriden by subclasses to define the control flow
        of the activation function.

        Arguments:
            params (dict): Any trainable variables that the activation function requires.
            inputs (Array): tensors to which the activation function is applied.
        
        Returns:
            outputs (Array): The outputs of the activation function.
        """
        # Ensuring implementation of the call function:
        raise NotImplementedError(
            "Originated from ``Activation.call()``"
            "Please implement the call function to define control flow."
            )

# Rectified Linear Unit:

class ReLU(Activation):
    
    """Rectified Linear Unit (ReLU) activation function.

    ReLU is a common activation function that returns non-negative values.

    Instructions:
        Creating an instance and use in a ``tensorwrap.nn.Model`` subclass, in combination of
        other layers.
    """

    def __init__(self, 
                 max_value=None,
                 negative_slope = 0,
                 threshold = 0,
                 name = "ReLU"):
        """
        Arguments:
            max_value (int, optional): [description]. Defaults to None.
            negative_slope (int, optional): [description]. Defaults to 0.
            threshold (int, optional): [description]. Defaults to 0.
            name (str, optional): [description]. Defaults to "ReLU".

        Raises:
            ValueError: [description]
        """
        super().__init__(name = name)
        self.max_value = max_value
        self.slope = negative_slope
        self.threshold = threshold
        if self.max_value is not None and self.max_value < 0:
            raise ValueError("Max_value cannot be negative.")
    

    def call(self, params, inputs):
        part1 = tf.maximum(0, inputs - self.threshold)
        if self.max_value is not None:
            return tf.minimum(part1, self.max_value)
        else:
            return part1
        
# Inspection Fixes:
Activation.__module__ = "tensorwrap.nn.activations"
ReLU.__module__ = "tensorwrap.nn.activations"