import pytest
from cse587Autils.utils.flatten_2d_list import flatten_2d_list


def test_flatten_2d_list():
    assert flatten_2d_list([[1, 2], [3, 4], [5, 6]]) == [1, 2, 3, 4, 5, 6]
    assert flatten_2d_list([[1], [2], [3]]) == [1, 2, 3]
    assert flatten_2d_list([]) == []

    with pytest.raises(TypeError):
        flatten_2d_list("not a list")
