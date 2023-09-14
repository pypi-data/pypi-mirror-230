"""The former optimizer class has been depracated in favor of """

import jax
from ...module import Module
from jaxtyping import Array

__all__ = ["Optimizer", "gradient_descent"]

class Optimizer(Module):
    def __init__(self, lr=0.01):
        self.lr = lr
        if not NotImplemented:
            raise NotImplementedError("Implement the init function for the learning rate.")
        
    def call(self):
        pass

# Change the naming to conventions:
class gradient_descent(Optimizer):
    def __init__(self, learning_rate=0.01):
        super().__init__(lr=learning_rate)


    def call(self, weights: Array, grad: Array):
        return weights - self.lr * grad 

    def apply_gradients(self, weights: dict, gradients: dict):
        weights = jax.tree_map(self.call, weights, gradients)
        return weights

# Inspection fixes:
Optimizer.__module__ = "tensorwrap.nn.optimizers"