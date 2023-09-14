from typing import Any
import tensorwrap as tw
from tensorwrap.module import Module
from tensorwrap.nn import optimizers
import jax
import copy
from termcolor import colored

# Creating a history management class:
class History(Module):
    def __init__(self) -> None:
        super().__init__()
        self.epoch = 1
        self.dict = {}
        self.decipher_dict = {
            "loss": 0,
            "metrics": 1,
            "val_loss": 2,
            "val_metrics": 3
        }
    
    def get(self, name):
        if name == "epochs":
            return jax.numpy.array(list(self.dict.keys()))
        return jax.numpy.array(list(self.dict.values()))[:, self.decipher_dict[name]]

    def __call__(self, loss_value, metrics_value, val_loss, val_metrics):
        epoch_list = [
            loss_value,
            metrics_value,
            val_loss,
            val_metrics
        ]
        self.dict[self.epoch] = epoch_list
        self.epoch += 1

# Creating a Training Class:
class Train(Module):
    def __init__(self, model, loss_fn, optimizer, metric_fn, copy_model = True) -> None:
        super().__init__()
        self.loss_fn = loss_fn
        self.metric_fn = jax.jit(metric_fn)
        if copy_model:
            self.model = copy.deepcopy(model)
        else:
            self.model = model
        self.optimizer = optimizer
        self.state = self.optimizer.init(self.model.params)
        self.history = History()

        @jax.value_and_grad
        def grad_fn(params, X, y):
            pred = self.model(params, X)
            return self.loss_fn(y, pred)
        self.grad_fn = grad_fn
    
    def train(self, X_train, y_train, epochs = 1, batch_size = 32, validation_data = None, callbacks = [lambda x: x]):
        X_train_batched = tw.experimental.data.Dataset(X_train).batch(batch_size)
        y_train_batched = tw.experimental.data.Dataset(y_train).batch(batch_size)
        if validation_data is not None:
            X_valid, y_valid = validation_data
            compile_val_score = jax.jit(self.val_score)
        else:
            val_loss = None
            val_metrics = None
        compiled_update = jax.jit(self.update)
        for epoch in range(1, epochs+1):
            print(f"Epoch {epoch}/{epochs}")
            for index, (X, y) in enumerate(zip(X_train_batched, y_train_batched)): 
                self.model.params, losses, self.state = compiled_update(self.model.params, self.state, X, y)
                metrics = self.metric_fn(y, self.model(self.model.params, X))
                self.loading_animation(X_train_batched.len(), index+1, losses, metrics)
            if validation_data is not None:
                    val_loss, val_metrics = compile_val_score(self.model.params, X_valid, y_valid)
            self.loading_animation(X_train_batched.len(), index+1, losses, metrics, val_loss=val_loss, val_metric=val_metrics)
            self.history(losses, metrics, val_loss, val_metrics)
            for callback in callbacks:
                callback(self.history)
            print("\n") 
    

    def get_params(self):
        return self.model.params

    def get_model(self):
        return self.model
    
    def get_train_history(self):
        return self.history
    
    def evaluate(self, X_test, y_test):
        self.model.evaluate(X_test, y_test, self.loss_fn, self.metric_fn)
    
    def update(self, params, state, X, y):
        losses, grads = self.grad_fn(params, X, y)
        updates, state = self.optimizer.update(grads, state, params)
        params = optimizers.apply_updates(params, updates)
        return params, losses, state
    
    def val_score(self, params, features_valid, labels_valid):
        pred = self.model(params, features_valid)
        val_metrics = self.metric_fn(labels_valid, pred)
        val_loss = self.loss_fn(labels_valid, pred)
        return val_loss, val_metrics

    def loading_animation(self, total_batches, current_batch, loss, metric, val_loss = None, val_metric = None):
        length = 30
        filled_length = int(length * current_batch // total_batches)
        bar = colored('─', "green") * filled_length + '─' * (length - filled_length)
        if val_loss is None:
            val_loss_str = ""
        else:
            val_loss_str = f"    -    val_loss: {val_loss:.5f}"
        
        if val_metric is None:
            val_met_str = ""
        else:
            val_met_str = f"    -    val_metrics: {val_metric:.5f}"
        print(f'\rBatch {current_batch}/{total_batches} [{bar}]    -    loss: {loss:.5f}    -    metric: {metric:.5f}' + val_loss_str + val_met_str, end='', flush=True)