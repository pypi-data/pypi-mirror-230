from typing import Union

import pytest

from prism._prismcomponent.abstract_prismcomponent import _AbstractPrismComponent
from prism._utils.validate_utils import _validate_args
from prism._utils.exceptions import PrismTypeError, PrismValueError


@_validate_args
def fillna(self, value: Union[str, float, int, _AbstractPrismComponent] = None, method: str = None, n: int = None):
    return True


def test_fillna_with_value():
    assert fillna(None, "string")
    assert fillna(None, 2.1)
    assert fillna(None, 1)
    assert fillna(None, _AbstractPrismComponent(children=[], component_args='a', component_name='b', component_type=None))


def test_fillna_with_wrong_value():
    with pytest.raises(PrismTypeError):
        assert fillna(None, value=["a", "b"])

    with pytest.raises(PrismTypeError):
        assert fillna(None, value={"key": "val"})


def test_fillna_with_method():
    assert fillna(None, method='backfill')
    assert fillna(None, method='bfill')
    assert fillna(None, method='pad')
    assert fillna(None, method='ffill')


def test_fillna_wrong_method():
    with pytest.raises(PrismValueError):
        assert fillna(None, method='unknwon method')


def test_fillna_wrong_signature():
    with pytest.raises(PrismValueError):
        assert fillna(None, method=None)

    # "value" and "method" arguement coexists
    with pytest.raises(PrismValueError):
        assert fillna(None, value=1, method='pad')

    with pytest.raises(PrismValueError):
        assert fillna(None, value=1, method='random_method')
