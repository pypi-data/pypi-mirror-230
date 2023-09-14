import tensorwrap as tw
import pytest
import numpy as np

# Prerequisite Data Types:
@pytest.fixture
def array():
    array = tw.tensor([1, 2, 3, 4])
    return array

@pytest.fixture
def tuple_gen():
    tup = (1, 2, 3)
    return tup

# Tests:

def test_last_dim_array(array):
    assert tw.last_dim(array) == array.shape[-1]

def test_last_dim_tuple(tuple_gen):
    assert tw.last_dim(tuple_gen) == np.shape(tuple_gen)[-1]

def test_randu():
    array = tw.randu((1, 2))
    assert array.shape == np.shape(array)

def test_randn():
    array = tw.randn((1, 2))
    assert array.shape == np.shape(array)