from typing import List
import logging
from numpy import isclose, ndarray

logger = logging.getLogger(__name__)


def check_probability(probability_vector: List[float],
                      tolerance: float = 1e-10) -> List[float]:
    """
    Check that a list of probabilities is valid.

    :param probability_vector: The probabilities to check.
    :type probability_vector: list of float
    :return: The validated probability_vector.
    :rtype: list of float
    :raises TypeError: If the probability_vector is not a list or the
      elements are not floats.
    :raises ValueError: If the probability_vector elements are not
      between 0 and 1 or the sum of probability_vector is not 1.

    :Examples:

    >>> check_probability([0.5, 0.5])
    [0.5, 0.5]

    An invalid list of probabilities (sum is not 1):

    >>> check_probability([0.1, 0.1])
    Traceback (most recent call last):
    ...
    ValueError: The sum of the values must be 1.

    An invalid list of probabilities (contains a non-float):

    >>> check_probability([0.5, '0.5'])
    Traceback (most recent call last):
    ...
    TypeError: The value must be a list of floats.
    """
    logger.debug('checking probability vector %s', probability_vector)
    # Check that the value is a list
    if not isinstance(probability_vector, (ndarray, list)):
        raise TypeError("The value must be a list.")
    # Check that each element of the list is a float
    for i in probability_vector:
        if not isinstance(i, (float, int)):
            raise TypeError("The value must be a list of floats.")
        if i < 0 or i > 1:
            raise ValueError("The value must be between 0.0 and 1.0")
    # Check that the sum of the values is 1
    if not isclose(sum(probability_vector), 1, atol=tolerance):
        raise ValueError("The sum of the values must be 1.0")
    # Return the value
    logger.debug('probability vector %s is valid', probability_vector)
    return probability_vector
