import numpy as np
import math


def euclidean_distance_lists(list1: (list, np.ndarray), 
                             list2: (list, np.ndarray)):
    """calculate the euclidean distance between two lists of numbers

    :param list1: first list of numbers
    :type list1: list or numpy.ndarray
    :param list2: second list of numbers
    :type list2: list or numpy.ndarray

    :return: euclidean distance between the two lists
    :rtype: float

    :raises TypeError: if either list is not a list
    :raises ValueError: if the lists are not the same length

    :Example:
    
    >>> euclidean_distance_lists([1, 2, 3], [1, 2, 3])
    0.0

    >>> euclidean_distance_lists([1, 2, 3], [4, 5, 6])
    5.196152422706632
    """
    if isinstance(list1, np.ndarray) and isinstance(list2, np.ndarray):
        euclidean_dist =  np.linalg.norm(list1-list2)
    elif isinstance(list1, list) and isinstance(list2, list):
        if len(list1) != len(list2):
            raise ValueError("Both lists must have the same length")
        euclidean_dist =  math.sqrt(sum((x - y)**2
                                        for x, y in zip(list1, list2)))
    else:
        raise TypeError("list1 and list2 must both be list, "
                        "or must both be numpy arrays")
    return euclidean_dist
