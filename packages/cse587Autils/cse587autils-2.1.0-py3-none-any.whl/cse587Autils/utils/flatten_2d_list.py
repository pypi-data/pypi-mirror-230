def flatten_2d_list(lst: list[list]) -> list:
    """
    flatten a list of lists into a single list

    :params lst: list of lists
    :type lst: list[list]

    :return: flattened list
    :rtype: list

    :raises TypeError: if lst is not a list

    :Example:

    >>> flatten_2d_list([[1, 2], [3, 4], [5, 6]])
    [1, 2, 3, 4, 5, 6]

    >>> flatten_2d_list([[1], [2], [3]])
    [1, 2, 3]

    >>> flatten_2d_list([])
    []
    """
    if not isinstance(lst, list):
        raise TypeError("lst must be a list")
    return [item for sublist in lst for item in sublist]
