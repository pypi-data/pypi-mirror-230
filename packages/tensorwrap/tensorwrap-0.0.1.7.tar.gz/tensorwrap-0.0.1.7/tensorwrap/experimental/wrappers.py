import jax


def function(func, **kwargs):
    """A decorator that compiles a function on graph and optimizes it for performance."""
    def wrapper(*args):
        funct = jax.jit(func, **kwargs)
        return funct(*args)
    return wrapper
