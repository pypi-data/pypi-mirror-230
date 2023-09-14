import jax.numpy as jnp
from jax import jit
from tensorwrap.nn.losses import Loss

class Accuracy(Loss):
    def __init__(self, from_logits = True) -> None:
        super().__init__()
        self.logits = from_logits
    
    
    def call(self, y_true, y_pred):
        """Computes the accuracy metric.

        Args:
            y_true (jax.numpy.ndarray): The true labels with shape (batch_size,).
            y_pred (jax.numpy.ndarray): The predicted logits or class probabilities with shape (batch_size, num_classes).
            from_logits (bool, optional): Whether the predicted values are logits or class probabilities.
                Defaults to True.

        Returns:
            float: The accuracy value.

        """
        if self.logits:
            y_pred = jnp.expand_dims(jnp.argmax(y_pred, axis=-1), axis=-1)

        correct = jnp.sum(y_true == y_pred)
        total = y_true.shape[0]
        return correct / total * 100
