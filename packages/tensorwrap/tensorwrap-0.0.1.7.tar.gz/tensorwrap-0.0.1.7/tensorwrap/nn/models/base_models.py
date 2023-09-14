# Stable Modules:
from typing import Any, Tuple, final, Dict, Optional

import jax
import optax
from jax import numpy as jnp
from jaxtyping import Array
from termcolor import colored

# Custom built Modules:
import tensorwrap as tw
from tensorwrap.module import Module
from tensorwrap.nn.layers.base_layers import Layer
from tensorwrap.nn.losses.base import Loss

__all__ = ["Model", "Sequential"]


class Model(Module):
    """A Module subclass that can be further subclasses for more complex models that don't
    work with Sequential class.

    Arguments:
        - name (string): The name of the model.
    
    Returns:
        - Model: An empty Model class that has prebuilt methods like compile, fit, predict, evaluate, and etc.
    
    NOTE: Recommended only for subclassing use.
    """

    # Used for tracking Model names.
    _name_tracker = 0

    def __init__(self, name:str = "Model") -> None:

        # Trainable Variables are tracked across all subclasses.
        self.params = {}

        # Name Tracking Handling:
        self.name = f"{name}:{Model._name_tracker}"
        Model._name_tracker += 1

        # Private attributes that track the state of each method:
        self._init = False
        self._compiled = False

    def __init_subclass__(cls) -> None:
        """Registers all subclasses as Pytrees and changes ``call`` conventions.
        Requires no arguments.

        NOTE: Private Method for internal uses.
        """
        super().__init_subclass__()
        cls.__call__ = cls.call
    
    def __check_attributes(self, obj: Any):
        """A recursive trainable_variable gatherer.

        Checks each attribute of the object to gather all trainable variables.

        Arguments:
            - obj (Any): The object whose attributes are to be checked.

        NOTE: Private Method for internal uses.
        """

        if isinstance(obj, tw.nn.layers.Layer):
            self.params[obj.name] = obj.params[obj.name]
        elif isinstance(obj, list):
            for item in obj:
                if self.__check_attributes(item):
                    return True
        elif isinstance(obj, dict):
            for value in obj.values():
                if self.__check_attributes(value):
                    return True
        elif hasattr(obj, '__dict__'):
            for attr_name, attr_value in obj.__dict__.items():
                if self.__check_attributes(attr_value):
                    return True
        return False

    def init_params(self, inputs: jax.Array) -> Dict[str, Dict[str, jax.Array]]:
        """An method that initiates all the trainable_variables and sets up all the layer inputs.
        
        Arguments:
            - inputs (jax.Array): Jax arrays that are used to determine the input shape and parameters.
        
        Returns:
            - Dict[str, ...]: A dictionary with names and trainable_variables of each trainable_layer.

        Example::
            >>> model = SubclassedModel() # a subclassed ``Model`` instance
            >>> array = tensorwrap.tensor([...]) # An array with same input shape as the inputs.
            >>> params = model.init_params(array) # Initializes the parameters and input shapes
            >>> # Asserting the equivalence of the returned value and parameters.
            >>> print(params == model.trainable_variables)
            True
        """
        
        self._init = True
        self.__check_attributes(self)

        # Prevents any problems during setup.
        with jax.disable_jit():
            self.call(self.params, inputs)
        
        self.__check_attributes(self)
        return self.params
    

    def predict(self, inputs: jax.Array) -> jax.Array:
        """Returns the predictions, when given inputs for the model.
        
        Arguments:
            - inputs: Proprocessed JAX arrays that can be used to calculate an output."""
        return self.__call__(self.params, inputs)
    

    def evaluate(self, x, y, loss_fn, metric_fn):
        pred = self.predict(x)
        metric = metric_fn(y, pred)
        loss = loss_fn(y, pred)
        self.__show_loading_animation(1, 1, loss, metric)


    def call(self, params = None, *args, **kwargs) -> Any:
        if not self._init:
            raise NotImplementedError("The model is not initialized using ``self.init_params``.")

        

    def __show_loading_animation(self, total_batches, current_batch, loss, metric):
        """Helper function that shows the loading animation, when training the model.
        
        NOTE: Private method.
        """
        length = 30
        filled_length = int(length * current_batch // total_batches)
        bar = colored('─', "green") * filled_length + '─' * (length - filled_length)
        print(f'\r{current_batch}/{total_batches} [{bar}]    -    loss: {loss}    -    metric: {metric}', end='', flush=True)

    # def compile(self,
    #             loss:Loss,
    #             optimizer,
    #             metrics:Optional[Loss] = None) -> None:
    #     """An instance method that compiles the model's prebuilt fit method.
        
    #     Given the loss function, optimizer, metrics, it creates the Optax opt_state and the gradient based loss function as well.

    #     Arguments:
    #         - loss: A function or ``tensorwrap.nn.losses.Loss`` subclass that has the arguments (y_true, y_pred) to compute the loss.
    #         - optimizer: An optax optimizer that have been initialized with learning_rate.
    #         - metrics: A function or ``tensorwrap.nn.losses.Loss`` subclass that has arguments (y_true, y_pred) to compute the metric.

    #     Example::
    #         >>> model = SubclassedModel() # a subclassed ``Model`` instance
    #         >>> array = tensorwrap.tensor([...]) # An array with same input shape as the inputs.
    #         >>> params = model.init_params(array) # Initializes the parameters and input shapes
    #         >>> # Compiling:
    #         >>> import optax
    #         >>> model.compile(
    #             loss = tensorwrap.nn.losses.mse, # Any loss function available.
    #             optimizer = optax.adam(learning_rate = 1e-2), # Any optax optimizer available.
    #             metrics = tensorwrap.nn.losses.mae # Any loss function or custom function needed.
    #         )
    #     """

    #     # Checks in Model is initiated.
    #     if not self._init:
    #         raise NotImplementedError(
    #             "Originated from ``model.compile``"
    #             "The model has not been initialized using ``model.init_params``."
    #         )

    #     # Getting the best
    #     self.loss_fn = loss
    #     self.optimizer = optimizer
    #     self.metrics = metrics if metrics is not None else loss
        
    #     # Handling compilation state:
    #     self._compiled = True

    #     # Prepping the optimizer:
    #     self.__opt_state = self.optimizer.init(self.trainable_variables)
        
    #     def compute_grad(params, x, y):
    #         y_pred = self.__call__(params, x)
    #         losses = self.loss_fn(y, y_pred)
    #         return losses

    #     self._value_and_grad_fn = jax.value_and_grad(compute_grad)

    # def train_step(self,
    #                x_train: jax.Array,
    #                y_train: jax.Array) -> Tuple[dict, Tuple[int, jax.Array]]:
    #     """A prebuilt method that computes loss and grads while updating 
    #     the trainable variables.

    #     Arguments:
    #         - params (Dict[str, ...]): A dictionary of trainable_variables.
    #         - x_train: The inputs or features.
    #         - y_train: The outputs or labels.
        
    #     Returns:
    #         - params (Dict[str, ...]): The dictionary of updated variables.
    #         - losses (int): A integer value of the losses.
    #         - y_pred (jax.Array): An array of predictions.
        
    #     NOTE: Private method for internal use.
    #     """
    #     losses, grads = self._value_and_grad_fn(self.trainable_variables, x_train, y_train)
    #     updates, self.__opt_state = self.optimizer.update(grads, self.__opt_state, self.trainable_variables)
    #     self.trainable_variables = optax.apply_updates(self.trainable_variables, updates)
    #     return losses


    # def fit(self,
    #         x_train,
    #         y_train,
    #         epochs:int = 1,
    #         batch_size:int = 32):
    #     """ Built-in in training method that updates gradients with minimalistic setup.
        
    #     Arguments:
    #         - x_train: The labels array.
    #         - y_train: The targets array.
    #         - epochs: Number of repetition for gradient updates.
    #         - batch_size: The size of batches for the training data.

    #     NOTE: Doesn't support validation and requires initiating of parameters and compilation of loss function
    #     and optimizers.
    #     """
    #     if epochs < 1:
    #         raise ValueError(
    #             "Originated from ``model.fit``"
    #             "Epochs must be a positive value."
    #         )
        
    #     if not self._compiled:
    #         raise NotImplementedError(
    #             "Originated from ``model.fit``."
    #             "The model has not been compiled using ``model.compile``."
    #         )

    #     # Batching the data:
    #     X_train_batched, y_train_batched = tw.experimental.data.Dataset(x_train).batch(batch_size), tw.experimental.data.Dataset(y_train).batch(batch_size)

    #     batch_num = len(x_train)//batch_size
    #     for epoch in range(1, epochs + 1):
    #         print(f"Epoch {epoch}/{epochs}")
    #         prev = self.trainable_variables
    #         for index, (x_batch, y_batch) in enumerate(zip(X_train_batched, y_train_batched)):
    #             loss = self.train_step(x_batch, y_batch)
    #             pred = self.predict(x_batch)
    #             metric = self.metrics(y_batch, pred)
    #             self.__show_loading_animation(batch_num, index + 1, loss, metric)
    #         print('\n')

    # def loading_animation(self, total_batches, current_batch, loss, metric, val_loss = None, val_metric = None):
    #     length = 30
    #     filled_length = int(length * current_batch // total_batches)
    #     bar = '=' * filled_length + '>' + '-' * (length - filled_length - 1)
    #     if val_loss is None:
    #         val_loss_str = ""
    #     else:
    #         val_loss_str = f"    -    val_loss: {val_loss:.5f}"
        
    #     if val_metric is None:
    #         val_met_str = ""
    #     else:
    #         val_met_str = f"    -    val_loss: {val_metric:.5f}"
    #     print(f'\r{current_batch}/{total_batches} [{bar}]    -    loss: {loss:.5f}    -    metric: {metric:.5f}' + val_loss_str + val_met_str, end='', flush=True)

    def __repr__(self) -> str:
        return f"<tf.{self.name}>"


# Sequential models that create Forward-Feed Networks:
class Sequential(Model):
    def __init__(self, layers: list = [], name = "Sequential") -> None:
        super().__init__(name=name)
        self.layers = layers


    def add(self, layer: Layer) -> None:
        self.layers.append(layer)

    def call(self, params: dict, x: Array) -> Array:
        super().call()
        for layer in self.layers:
            x = layer(params, x)
        return x


# Inspection Fixes:
Model.__module__ = "tensorwrap.nn.models"
Sequential.__module__ = "tensorwrap.nn.models"