"""Classes and functions for the siteEM assignment series"""
import sys
import logging
import copy
from typing import List
from cse587Autils.utils.check_probability import check_probability
from cse587Autils.utils.flatten_2d_list import flatten_2d_list
from cse587Autils.utils.euclidean_distance_lists \
    import euclidean_distance_lists

logger = logging.getLogger(__name__)


class SiteModel:
    """
    A class for storing and managing parameters for a simple probabilistic
    model of transcription factor binding sites in a genome.

    :Example:

    >>> site_prior = 0.2
    >>> site_probs = [[0.25, 0.25, 0.25, 0.25], [0.1, 0.2, 0.3, 0.4]]
    >>> background_probs = [1/4]*4
    >>> sm = SiteModel(site_prior, site_probs, background_probs)
    >>> len(sm)
    2
    """

    def __init__(self,
                 site_prior: float = None,
                 site_probs: List[List[float]] = None,
                 background_probs: List[float] = None,
                 precision: int = sys.float_info.dig,
                 tolerance: float = 1e-10) -> None:
        """
        See the property documentation for details on each parameter.

        Note that if site_prior is set, background_prior is automatically set
            to 1 - site_prior.
        """
        self._precision = precision
        self._tolerance = tolerance
        if site_prior is not None:
            self.site_prior = site_prior
        if site_probs:
            self.site_probs = site_probs
        if background_probs:
            self.background_probs = background_probs

    @property
    def precision(self) -> int:
        """
        Get or set The number of digits which can accurately represent
            floating-point numbers. This is used to round the priors. By
            default, SiteModel objects have precision set to
            sys.float_info.dig, which is the runtime machine's precision.

        :return: Precision for floating-point operations.
        :rtype: int

        :Raises:
            - TypeError: If the precision is not an int.
            - ValueError: If the precision is less than 0.

        :Example:

        >>> sm = SiteModel()
        >>> sm.precision = 15
        >>> sm.precision
        15
        """
        return self._precision

    @precision.setter
    def precision(self, precision: int):
        if not isinstance(precision, int):
            raise TypeError('The precision must be an int.')
        if precision < 0:
            raise ValueError('The precision must be greater than 0.')
        self._precision = precision

    @property
    def tolerance(self) -> float:
        """
        Get or set the tolerance for checking probabilities. Defaults to 1e-10
            if not explicitly provided in constructor.

        :return: Tolerance for checking probabilities.
        :rtype: float

        :Raises:
            - TypeError: If the tolerance is not a float.
            - ValueError: If the tolerance is less than 0 or greater than 1.

        :Example:

        >>> sm = SiteModel()
        >>> sm.tolerance = 1e-10
        >>> sm.tolerance
        1e-10
        """
        return self._tolerance

    @tolerance.setter
    def tolerance(self, tolerance: float):
        if not isinstance(tolerance, (float, int)):
            raise TypeError('The tolerance must be a float.')
        if tolerance < 0 or tolerance > 1:
            raise ValueError('The tolerance must be between 0 and 1.')
        self._tolerance = tolerance

    @property
    def site_prior(self) -> float:
        """
        Prior probability of a bound site, defaults to None if not provided in
            constructor. If site_prior is set, background_prior will be set to
            1 - site_prior. This automatic update of the opposite prior occurs
            when either site_prior or background_prior are updated in an
            instance of SiteModel, also.

        :return: Prior probability of a bound site.
        :rtype: float

        :Example:

        >>> sm = SiteModel()
        >>> sm.site_prior = 0.2
        >>> round(sm.site_prior,1)
        0.2
        >>> round(sm.background_prior,1)
        0.8
        """
        try:
            return self._site_prior
        except AttributeError:
            logger.warning('site_prior not set')
            return None

    @site_prior.setter
    def site_prior(self, prior: float):
        logger.warning('Setting site_prior will also set background_prior to '
                       '1 - site_prior')
        rounded_site_prior = round(prior, self.precision)
        rounded_background_prior = round(1.0 - prior, self.precision)
        check_probability([rounded_site_prior, rounded_background_prior],
                          tolerance=self.tolerance)
        self._site_prior = rounded_site_prior
        self._background_prior = rounded_background_prior

    @property
    def background_prior(self) -> float:
        """
        Get or set the prior probability of a non-bound site. Defaults to None
            if site_prior is not passed in the object constructor. However, if
            site_prior is passed in the constructor, or if background_prior is
            updated, site_prior will be set to 1 - background_prior.

        :return: Prior probability of a non-bound site.
        :rtype: float

        :Example:

        >>> sm = SiteModel()
        >>> sm.background_prior = 0.8
        >>> round(sm.background_prior,1)
        0.8
        >>> round(sm.site_prior,1)
        0.2
        """
        try:
            return self._background_prior
        except AttributeError:
            logger.warning('background_prior not set')
            return None

    @background_prior.setter
    def background_prior(self, prior: float):
        logger.warning('Setting background_prior will also set site_prior to '
                       '1 - background_prior')
        rounded_site_prior = round(1 - prior, self.precision)
        rounded_background_prior = round(prior, self.precision)
        check_probability([rounded_site_prior, rounded_background_prior],
                          tolerance=self.tolerance)
        self._site_prior = rounded_site_prior
        self._background_prior = rounded_background_prior

    @property
    def site_probs(self) -> List[List[float]]:
        """
        List of lists containing probabilities for each base in bound sites.
            Each sublist will be length 4 and represents the probability of
            observing each base (A, C, G, T) at the given position in a bound
            site. Defaults to None if not provided in constructor. The length
            of site_probs is the length of the site sequence and is provided
            by len(SiteModel). If not explicitly passed in the constructor,
            site_probs defaults to `None`.

        :return: A list of lists containing probabilities for each base in
            bound sites.
        :rtype: list[list[float]]

        :Raises:
            - TypeError: If the value is not a list of lists.
            - ValueError: If each sublist is ont length 4.

        :Example:

        >>> sm = SiteModel()
        >>> sm.site_probs = [[0.25, 0.25, 0.25, 0.25], [0.1, 0.2, 0.3, 0.4]]
        >>> sm.site_probs[1]
        [0.1, 0.2, 0.3, 0.4]
        """
        try:
            return self._site_probs
        except AttributeError:
            logger.warning('site_probs not set')
            return None

    @site_probs.setter
    def site_probs(self, site_probs: List[List[float]]):
        if not isinstance(site_probs, list):
            raise TypeError('The value must be a list of lists.')
        for site_prob in site_probs:
            if not isinstance(site_prob, list):
                raise TypeError('Each element in `site_probs` must be a list')
            if not len(site_prob) == 4:
                raise ValueError('Each element in `site_probs` must '
                                 'be length 4.')
            check_probability(site_prob, tolerance=self.tolerance)
        self._site_probs = site_probs

    @property
    def background_probs(self) -> List[float]:
        """
        List containing the background probabilities for each base. This is a
            list of length four, where each element represents the probability
            of observing each base (A, C, G, T) in the background. It is a
            simplifying assumption that the probability of observing each base
            is independent of the position in the genome. Defaults to None if
            `background_probs` is not provided in the constructor.

        :return: A list containing the background probabilities for each base.
        :rtype: list[float]

        :Example:

        >>> sm = SiteModel()
        >>> sm.background_probs = [0.25, 0.25, 0.25, 0.25]
        >>> sm.background_probs
        [0.25, 0.25, 0.25, 0.25]
        """
        try:
            return self._background_probs
        except AttributeError:
            logger.warning('background_probs not set')
            return None

    @background_probs.setter
    def background_probs(self, background_probs: List[float]):
        if not isinstance(background_probs, list):
            raise TypeError('The value must be a list.')
        if not len(background_probs) == 4:
            raise ValueError('The value must be length 4.')
        check_probability(background_probs, tolerance=self.tolerance)
        self._background_probs = background_probs

    def __repr__(self) -> str:
        """
        Generate an unambiguous string representation of the SiteModel
            instance.

        This string representation is intended for debugging and should be
            able to recreate the object if passed to the eval() function.

        :return: A string representation of the SiteModel instance.
        :rtype: str

        :Example:

        >>> site_prior = 0.2
        >>> site_probs = [[0.25, 0.25, 0.25, 0.25], [0.1, 0.2, 0.3, 0.4]]
        >>> background_probs = [1/4]*4
        >>> sm = SiteModel(site_prior, site_probs, background_probs)
        >>> repr(sm)
        'SiteModel(site_prior=0.2, site_probs=[[0.25, 0.25, 0.25, 0.25], [0.1, 0.2, 0.3, 0.4]], background_probs=[0.25, 0.25, 0.25, 0.25])'
        """
        return (f'SiteModel(site_prior={self.site_prior}, '
                f'site_probs={self.site_probs}, '
                f'background_probs={self.background_probs})')

    def __str__(self) -> str:
        """
        Generate a human-readable string representation of the SiteModel
            instance.

        This string representation is intended for end-users and provides an
        easily interpretable description of the SiteModel instance.

        :return: A human-readable string representation of the SiteModel
            instance.
        :rtype: str

        :Example:

        >>> site_prior = 0.2
        >>> site_probs = [[0.25, 0.25, 0.25, 0.25], [0.1, 0.2, 0.3, 0.4]]
        >>> background_probs = [1/4]*4
        >>> sm = SiteModel(site_prior, site_probs, background_probs)
        >>> str(sm)  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
        'SiteModel with site_prior: 0.2, background_prior: 0.8, site_probs: [[0.25, 0.25, 0.25, 0.25], [0.1, 0.2, 0.3, 0.4]], background_probs: [0.25, 0.25, 0.25, 0.25]'
        """
        return (f'SiteModel with site_prior: {self.site_prior}, '
                f'background_prior: {self.background_prior}, '
                f'site_probs: {self.site_probs}, '
                f'background_probs: {self.background_probs}')

    def __len__(self) -> int:
        """Return the number of positions in the site sequence.

        :return: Number of positions in the site sequence.
        :rtype: int

        :Example:

        >>> sm = SiteModel()
        >>> sm.site_probs = [[0.25, 0.25, 0.25, 0.25], [0.1, 0.2, 0.3, 0.4]]
        >>> len(sm)
        2
        """
        try:
            return len(self.site_probs)
        except AttributeError:
            logger.warning('site_probs not set')
            return None

    def __sub__(self, other: 'SiteModel') -> float:
        """
        Calculate the absolute difference between two SiteModels.

        The difference is calculated by taking the sum of the euclidean
        distance between [site_prior, background_prior], the euclidean
        distance between each site probability, and the euclidean distance
        between each background probability.

        :param other: The other SiteModel to compare to.
        :type other: SiteModel

        :raises TypeError: If the other object is not a SiteModel.
        :raises ValueError: If the two SiteModels do not have the same length
            site_probs or if any of the attributes are not set.

        :return: The absolute difference between the two SiteModels.
        :rtype: float

        :Example:

        >>> sm1 = SiteModel(0.2, 
        ...                 [[0.1, 0.2, 0.3, 0.4], [0.3, 0.4, 0.3, 0.0]], 
        ...                 [0.25, 0.25, 0.25, 0.25])
        >>> sm2 = SiteModel(0.1, 
        ...                 [[0.1, 0.1, 0.1, 0.7], [0.2, 0.2, 0.2, 0.4]], 
        ...                 [0.25, 0.25, 0.25, 0.25])
        >>> sm1 - sm2
        0.7414213562373095
        """
        if not isinstance(other, SiteModel):
            raise TypeError(f"Unsupported type {type(other)} for subtraction")

        if not len(self) == len(other):
            raise ValueError("Both SiteModels must have the same "
                             "length site_probs")

        if (self.site_prior is None
            or other.site_prior is None
            or self.background_prior is None
            or other.background_prior is None
            or self.site_probs is None
            or other.site_probs is None
            or self.background_probs is None
                or other.background_probs is None):
            raise ValueError("Both SiteModels must have all parameters set")

        if len(self.site_probs) != len(other.site_probs):
            raise ValueError(
                "Both SiteModels must have the same length site_probs")

        prior_diff = euclidean_distance_lists(
            [self.site_prior, self.background_prior],
            [other.site_prior, other.background_prior]
        )
        # get the abolute difference between each site probability
        site_probs_diff = euclidean_distance_lists(
            flatten_2d_list(self.site_probs),
            flatten_2d_list(other.site_probs)
        )
        # get the absolute difference between each background probability
        background_probs_diff = euclidean_distance_lists(
            self.background_probs,
            other.background_probs
        )
        return (prior_diff
                + site_probs_diff
                + background_probs_diff)

    def __copy__(self):
        """Copy method for SiteModel

        :return: A deep copy of the SiteModel instance.
        :rtype: SiteModel
        """
        new_instance = SiteModel()
        new_instance._precision = self._precision
        new_instance._tolerance = self._tolerance

        # Deep copy the lists so that they are new instances
        new_instance._site_probs = copy.deepcopy(self._site_probs)
        new_instance._background_probs = copy.deepcopy(self._background_probs)

        # Copy the simple float attributes
        new_instance._site_prior = self._site_prior
        new_instance._background_prior = self._background_prior

        return new_instance
