import dill
from tensorwrap.module import Module

def save_model(model:Module , filepath:str):
    """Loads model with classes and variables.
    Args:
     - model: The model that you want to save.
     - filepath: The path to save the model. It doesn't have to exist."""
    with open(filepath, "wb") as writer:
        dill.dump(model, writer)

def load_model(filepath:str) -> Module:
    """Loads model with classes and variables.
    Args:
     - filepath: The path containing the model."""
    with open(filepath, "rb") as reader:
        model = dill.load(reader)
    return model