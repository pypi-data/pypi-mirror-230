from math import prod
import numpy as np
from numpy.testing import assert_allclose
from cse587Autils.DiceObjects.Die import Die
from cse587Autils.DiceObjects.BagOfDice import BagOfDice


def test_bag_of_dice_constructor():
    die_priors = [0.5, 0.5]
    dice = [Die([1 / 6] * 6), Die([0.9, 0.1])]
    my_bag = BagOfDice(die_priors, dice)
    assert my_bag.die_priors == die_priors
    assert my_bag.dice == dice


def test_bag_of_dice_die_priors_setter():
    die_priors = [0.5, 0.5]
    my_bag = BagOfDice()
    my_bag.die_priors = die_priors
    assert my_bag.die_priors == die_priors


def test_bag_of_dice_dice_setter():
    dice = [Die([1 / 6] * 6), Die([0.9, 0.1])]
    my_bag = BagOfDice()
    my_bag.dice = dice
    assert my_bag.dice == dice


def test_bag_of_dice_repr():
    die_priors = [0.5, 0.5]
    dice = [Die([1 / 6] * 6), Die([0.9, 0.1])]
    my_bag = BagOfDice(die_priors, dice)
    assert repr(my_bag) == f"BagOfDice(die_priors={die_priors}, dice={dice})"


def test_bag_of_dice_len():
    die_priors = [0.5, 0.5]
    dice = [Die([1 / 6] * 6), Die([0.9, 0.1])]
    my_bag = BagOfDice(die_priors, dice)
    assert len(my_bag) == 2


def test_bag_of_dice_getitem():
    die_priors = [0.5, 0.5]
    dice = [Die([1 / 6] * 6), Die([0.9, 0.1])]
    my_bag = BagOfDice(die_priors, dice)
    assert my_bag[0] == (0.5, dice[0])
    assert my_bag[0][0] == 0.5
    assert my_bag[0][1] == dice[0]


def test_bag_of_dice_subtraction_diff():
    fair_die = Die([1 / 6] * 6)
    biased_die = Die([0.9, 0.1])
    my_bag = BagOfDice([0.5, 0.5], [fair_die, biased_die])
    other_bag = BagOfDice([0.4, 0.6], [fair_die, biased_die])
    actual = my_bag - other_bag
    expected = abs(0.5 - 0.4) + abs(0.5 - 0.6)
    assert actual == expected


def test_bag_of_dice_subtraction_same():
    """Bags are the same. Diff should be 0"""
    fair_die = Die([1 / 6] * 6)
    my_bag = BagOfDice([0.5, 0.5], [fair_die, fair_die])
    actual = my_bag - my_bag
    expected = 0
    assert actual == expected


def test_bag_of_dice_iteration():
    fair_die = Die([1 / 6] * 6)
    biased_die = Die([0.9, 0.1])
    my_bag = BagOfDice([0.5, 0.5], [fair_die, biased_die])
    for i, die_info in enumerate(my_bag):
        assert die_info == (0.5, my_bag.dice[i])


def test_bag_of_dice_draw():
    seed = 42
    fair_die = Die([1 / 6] * 6)
    biased_die = Die([0.9, 0.1])
    my_bag = BagOfDice([0.5, 0.5], [fair_die, biased_die])
    result = my_bag.draw(5, seed)
    assert sum(result) == 5


def test_bag_of_dice_likelihood():
    fair_die = Die([1 / 6] * 6)
    biased_die = Die([0.9, 0.1])
    my_bag = BagOfDice([0.5, 0.5], [fair_die, biased_die])
    observed_data = [np.array([1, 2, 3, 4, 5, 6]), np.array([1, 2])]
    likelihood = my_bag.likelihood(observed_data)
    expected_likelihood = 1.0684028233559576e-24
    assert_allclose(likelihood, expected_likelihood)


def test_likelihood_manual():
    # Set up the bag of dice with two types: fair dice and biased dice
    fair_die = Die([1/6] * 6)
    fair_die_prob = 0.4
    biased_die = Die([0.1, 0.1, 0.1, 0.1, 0.1, 0.5])
    biased_die_prob = 0.6
    bag_of_dice = BagOfDice([fair_die_prob, biased_die_prob],
                            [fair_die, biased_die])

    # Set up the observed bin counts

    sample_rolls = [np.array([0, 0, 0, 0, 0, 0]),
                       np.array([0, 0, 0, 0, 0, 1])]

    expected = 1.0
    # calculate the probabilities of each trial's bin count given the fair die
    # multiplied by the probability of drawing that die
    fair_die_probabilty_trial_1 = \
        fair_die.likelihood(sample_rolls[0]) * fair_die_prob
    fair_die_probabilty_trial_2 = \
        fair_die.likelihood(sample_rolls[1]) * fair_die_prob

    biased_die_probabilty_trial_1 = \
        biased_die.likelihood(sample_rolls[0]) * biased_die_prob
    biased_die_probabilty_trial_2 = \
        biased_die.likelihood(sample_rolls[1]) * biased_die_prob

    expected = prod([fair_die_probabilty_trial_1,
                     fair_die_probabilty_trial_2,
                     biased_die_probabilty_trial_1,
                     biased_die_probabilty_trial_2])

    # Calculate the likelihood
    actual = bag_of_dice.likelihood(sample_rolls)

    # Assert that the likelihood is 0
    assert np.isclose(actual, expected, atol=1e-10), \
        f"Expected {expected}, but got {actual}"


def test_likelihood_1():
    # Define the observed data
    observed_data = [np.zeros(6), 
                     np.zeros(6)]

    # Create the bag of dice with known probabilities
    fair_die = Die([1.0])
    bag_of_dice = BagOfDice([1.0], [fair_die])

    # Calculate the likelihood
    likelihood = bag_of_dice.likelihood(observed_data)

    # Assert that the likelihood is equal to 1
    assert likelihood == 1.0


def test_calculate_likelihood_diff_length_dice():
    fair_die = Die([1/6]*6)
    biased_die = Die([0.9, 0.1])
    bag_of_dice = BagOfDice([0.5, 0.5], [fair_die, biased_die])
    sample_rolls = [np.array([1, 2, 3, 4, 5, 6]), np.array([1, 2])]

    expected = 1
    for bin_counts in sample_rolls:
        for die_info in bag_of_dice:
            die_prior, die = die_info
            expected *= die.likelihood(bin_counts) * die_prior

    actual = bag_of_dice.likelihood(sample_rolls)

    assert np.isclose(actual, expected, atol=1e-10), \
        f"Expected {expected}, but got {actual}"