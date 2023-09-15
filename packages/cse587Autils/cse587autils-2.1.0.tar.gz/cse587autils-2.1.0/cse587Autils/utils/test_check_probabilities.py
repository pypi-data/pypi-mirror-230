import logging
import pytest
from cse587Autils.utils.check_probability import check_probability

def test_check_probability():
    # Test with valid input
    assert check_probability([0.5, 0.5]) == [0.5, 0.5]
    # Test with zero probabilities
    assert check_probability([0.0, 1.0]) == [0.0, 1.0]
    # Test with values not between 0 and 1
    with pytest.raises(ValueError, match=r"The value must be between 0.0 and 1.0"):
        check_probability([1.5, -0.5])
    # Test with a non-float
    with pytest.raises(TypeError, match=r"The value must be a list of floats."):
        check_probability([0.5, "0.5"])
    # Test with a non-list
    with pytest.raises(TypeError, match=r"The value must be a list."):
        check_probability("not a list")

def test_check_probability_logging(caplog):
    caplog.set_level(logging.DEBUG)
    check_probability([0.5, 0.5])
    assert "checking probability vector [0.5, 0.5]" in caplog.text
    assert "probability vector [0.5, 0.5] is valid" in caplog.text
