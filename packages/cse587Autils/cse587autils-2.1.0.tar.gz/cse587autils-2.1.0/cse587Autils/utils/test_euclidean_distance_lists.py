import pytest
from cse587Autils.utils.euclidean_distance_lists import euclidean_distance_lists # noqa: E402

def test_euclidean_distance_lists():
    assert euclidean_distance_lists([1, 2, 3], [1, 2, 3]) == 0.0
    assert euclidean_distance_lists([1, 2, 3], [4, 5, 6]) == \
        pytest.approx(5.196152422706632)

    with pytest.raises(ValueError):
        euclidean_distance_lists([1, 2], [1, 2, 3])

    with pytest.raises(TypeError):
        euclidean_distance_lists([1, 2, 'a'], [1, 2, 3])

    with pytest.raises(TypeError):
        euclidean_distance_lists("not a list", [1, 2, 3])

    with pytest.raises(TypeError):
        euclidean_distance_lists([1, 2, 3], "not a list")