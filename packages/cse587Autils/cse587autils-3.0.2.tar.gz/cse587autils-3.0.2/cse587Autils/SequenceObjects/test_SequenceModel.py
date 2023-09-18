import logging
from copy import copy
import pytest
from cse587Autils.SequenceObjects.SequenceModel import SequenceModel


def test_valid_construction():
    site_prior = 0.2
    site_base_probs = [[0.25, 0.25, 0.25, 0.25], [0.1, 0.2, 0.3, 0.4]]
    background_base_probs = [0.25, 0.25, 0.25, 0.25]

    sm = SequenceModel(site_prior, site_base_probs, background_base_probs)

    assert sm.background_prior == 0.8
    assert len(sm) == 2

    sm1 = SequenceModel(1, site_base_probs, background_base_probs)
    assert sm1.background_prior == 0

    sm2 = SequenceModel(0, site_base_probs, background_base_probs)
    assert sm2.background_prior == 1


def test_logging(caplog):
    caplog.set_level(logging.INFO)
    sm = SequenceModel()
    sm.site_prior = 0.3  # This will log a warning

    assert ("Setting site_prior will also set "
            "background_prior to 1 - site_prior" in caplog.text)


def test_invalid_precision_type():
    sm = SequenceModel()
    with pytest.raises(TypeError):
        sm.precision = 'invalid_type'


def test_invalid_tolerance_type():
    sm = SequenceModel()
    with pytest.raises(TypeError):
        sm.tolerance = 'invalid_type'


def test_invalid_site_base_probs_shape():
    sm = SequenceModel()
    with pytest.raises(ValueError):
        sm.site_base_probs = [[0.25, 0.25, 0.25], [0.1, 0.2, 0.3, 0.4]]


def test_invalid_background_base_probs_length():
    sm = SequenceModel()
    with pytest.raises(ValueError):
        sm.background_base_probs = [0.25, 0.25, 0.25]


def test_sequence_model_subtraction():
    sm1 = SequenceModel(0.2,
                        [[0.1, 0.2, 0.5, 0.2], [0.3, 0.4, 0.2, 0.1]],
                        [0.25]*4)
    sm2 = SequenceModel(0.1,
                        [[0.1, 0.1, 0.8, 0.0], [0.2, 0.2, 0.1, 0.5]],
                        [0.25]*4)
    result = sm1 - sm2
    assert result == 0.7414213562373095


def test_copy_method():
    original = SequenceModel(
        site_prior=0.2,
        site_base_probs=[[0.25, 0.25, 0.25, 0.25], [0.1, 0.2, 0.3, 0.4]],
        background_base_probs=[0.25, 0.25, 0.25, 0.25]
    )

    copied = copy(original)

    # Test if the objects are different
    assert original - copied == 0

    # Test if the attributes are the same
    assert original.site_prior == copied.site_prior
    assert original.site_base_probs == copied.site_base_probs
    assert original.background_base_probs == copied.background_base_probs
    assert original.precision == copied.precision
    assert original.tolerance == copied.tolerance

    # Test if modifications to the copy don't affect the original
    copied.site_prior = 0.3
    assert original.site_prior != copied.site_prior
