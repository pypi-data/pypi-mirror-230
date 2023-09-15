import numpy as np
from h2lib._h2lib import H2Lib
import pytest
import os
import h2lib


@pytest.fixture(scope='module')
def h2():
    h2 = H2Lib()
    yield h2
    h2.close()


def test_sqr(h2):
    ret_args, res = h2.sqr2(3)
    assert ret_args[0] == 9


def test_square(h2):
    ret_args, res = h2.getSquare(3., restype=np.float64)
    assert res == 9


def test_version(h2):
    print(h2.version())


def test_hdf5(h2):
    h2.test_hdf5()


def test_mkl(h2):
    h2.test_mkl()


def test_two_in_same_process():
    if os.name == 'posix':
        with pytest.raises(Exception, match='already in use in current process|cannot open shared object file'):
            h2_1 = H2Lib(subprocess=False)
            h2_2 = H2Lib(subprocess=False)
    else:
        with pytest.raises(Exception, match='already in use in current process'):
            h2_1 = H2Lib(subprocess=False)
            h2_2 = H2Lib(subprocess=False)


def test_state(h2):
    h2_2 = H2Lib()
    h2.setState(5)
    assert h2.getState() == 5
    h2_2.setState(6)
    assert h2_2.getState() == 6
    assert h2.getState() == 5


def test_hidden_function(h2):
    with pytest.raises(AttributeError, match="'H2LibThread' object has no attribute 'hidden_function'"):
        h2.hidden_function()


def test_hidden_c_function(h2):
    if os.name == 'posix':
        # functino is not accessible because it is not in  export.txt
        with pytest.raises(AttributeError, match="'H2LibThread' object has no attribute 'hidden_c_function'"):
            h2.hidden_c_function()


def test_hidden_functions_is_hidden():
    if os.name == 'posix':
        # cannot hide function names
        assert 'hidden_c_function' in os.popen(f"nm {os.path.dirname(h2lib.__file__)}/HAWC2Lib.so").read()
        assert 'hidden_function' in os.popen(f"nm {os.path.dirname(h2lib.__file__)}/HAWC2Lib.so").read()
