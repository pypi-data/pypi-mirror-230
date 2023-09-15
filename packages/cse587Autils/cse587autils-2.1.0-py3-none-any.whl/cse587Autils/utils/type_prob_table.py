from typing import List
import pandas as pd


def type_prob_table(experiment_data: List[List[int]], posteriors: List[float]):
    """
    This is a utility function from the mathematica assignments.
        It is not used in the python assignments, but is included here in
        case anyone wants it. This is untested and more of an outline than
        a function.

    :param experiment_data: A list of lists of integers. Each list of integers
        represents the results of a drawing a die, rolling it some number of
        times, and then aggregating how many times each face (represented by
        the index in the list) was rolled.
    :type experiment_data: List[List[int]]
    :param posteriors: A list of floats representing the probability that the
        die used to generate the data
    :type posteriors: List[float]

    :return: A pandas dataframe with the following columns:
        - Trial 1, Trial 2, ... Trial N: The bin counts for each trial
        - Pr(dieType=1|trial): The probability that the die used to generate
            the data was a fair die
        - Pr(dieType=2|trial): The probability that the die used to generate
            the data was a biased die
    :rtype: pandas.DataFrame
    """
    trials = len(experiment_data[0])
    data = experiment_data + [posteriors] + [[1 - p for p in posteriors]]

    df = pd.DataFrame(data).transpose()
    df.columns = ['Trial {}'.format(i+1) for i in range(trials)] +\
        ['Pr(dieType=1|trial)', 'Pr(dieType=2|trial)']

    df.loc['Total', :] = df.sum(axis=0)

    return df
