import math


def euclidean_distance_lists(list1: list, list2: list):
    """calculate the euclidean distance between two lists of numbers

    :param list1: first list of numbers
    :type list1: list
    :param list2: second list of numbers
    :type list2: list

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
    if not isinstance(list1, list) or not isinstance(list2, list):
        raise TypeError("Both input values must be lists")
    if len(list1) != len(list2):
        raise ValueError("Both lists must have the same length")

    sum_of_squares = sum((x - y)**2 for x, y in zip(list1, list2))
    return math.sqrt(sum_of_squares)
