# Unstable Populations
#
# Mar 2022, Marcel Haas, datascience@marcelhaas.com
#
################################################

"""
Unstable Populations: has your data drifted?

Measuring whether your data has drifted through:
- UPI: the Unstable Population Indicator: upi()
- PSI: the Population Stability Index: psi()

When two populations are supplied (see help of the functions for 
more details), a (in)stability index is returned. Very low numbers
(rule of thumb! Test for yourself!) of <~0.1 indicate that the 
distributions in both populations are the same, while larger 
numbers indicate larger difference between the two distributions.

Version 0.2.1, Aug 2022, Marcel Haas (datascience@marcelhaas.com)
"""

import numpy as np
import pandas as pd
import pytest
import os

################################################


def upi(pop1, pop2, bin_data=False, bins=10, verbose=False):
    """Calculate the Unstable Population Indicator,
    which is based on counts of entities in a population divided over
    either categories or bins (the bins can be made by the function).

    Comparison can be weighted by number, such that
    bins with many elements are weighted heavier.

    Parameters
    ----------
    pop1, pop2
        list, numpy.ndarray, dict, pandas.Series or pandas.DataFrame
        containing the first and population, respectively.
        They need to be of the same type. When they are:
        - list/numpy.ndarray: either the full population (ints or floats)
            that need to be binned (bin_data=True) or an ordered sequence of
            (unnamed) categories/bins with bin counts or fractions of the
            population in the bin or category.
        - dict: dictionary with category names or bin values as keys and count
            or fractions in those categories/bins as values. The two populations
            will be matched based on keys and non-existing categories in either
            population will be added with value 0.
        - pandas.Series: Series with category names or bin values as index and
            count or fractions in those categories/bins as values. The two
            populations will be matched based on index and non-existing
            categories in either population will be added with value 0.
        - pandas.DataFrame: need to have only one column, will be converted to
            Series, see definition of Series above.
        All values that indicate a count or fraction are taken as is (no
        consistency check on data type and normalization) and will be normalized
        to sum to 1 (i.e. converted into fractions)

    weight, optional
        Boolean indicating whether weighting by bin values is done,
        by default True
    bin_data, optional
        Boolean indicating whether data should be binned first,
        by default False
    bins, optional
        When bin_data=True, this keyword indicates how binning is done, as
        performed by numpy.histogram. It accepts an integer (number of bins),
        list/numpy.ndarray with bin edges, a string indicating the method
        (see numpy.histogram_bin_edges for documentation), by default 10
    verbose, optional
        Boolean indicating whether extra information should be printed,
        by default False

    Returns
    -------
        UPI, a floating point number indicating the instability of the
        population, going from one to the other (it is symmetric).
        Rule of thumb: UPI<0.1 indicates a similar distribution.
    """

    return _indicator(
        pop1,
        pop2,
        plus1=True,
        bin_data=bin_data,
        bins=bins,
        verbose=verbose,
    )


################################################


def psi(pop1, pop2, bin_data=False, bins=10, verbose=False):
    """Calculate the Population Stability Index,
    which is based on counts of entities in a population divided over
    either categories or bins (the bins can be made by the function).

    Parameters
    ----------
    pop1, pop2
        list, numpy.ndarray, dict, pandas.Series or pandas.DataFrame
        containing the first and population, respectively.
        They need to be of the same type. When they are:
        - list/numpy.ndarray: either the full population (ints or floats)
            that need to be binned (bin_data=True) or an ordered sequence of
            (unnamed) categories/bins with bin counts or fractions of the
            population in the bin or category.
        - dict: dictionary with category names or bin values as keys and count
            or fractions in those categories/bins as values. The two populations
            will be matched based on keys and non-existing categories in either
            population will be added with value 0.
        - pandas.Series: Series with category names or bin values as index and
            count or fractions in those categories/bins as values. The two
            populations will be matched based on index and non-existing
            categories in either population will be added with value 0.
        - pandas.DataFrame: need to have only one column, will be converted to
            Series, see definition of Series above.
        All values that indicate a count or fraction are taken as is (no
        consistency check on data type and normalization) and will be normalized
        to sum to 1 (i.e. converted into fractions)

    bin_data, optional
        Boolean indicating whether data should be binned first,
        by default False
    bins, optional
        When bin_data=True, this keyword indicates how binning is done, as
        performed by numpy.histogram. It accepts an integer (number of bins),
        list/numpy.ndarray with bin edges, a string indicating the method
        (see numpy.histogram_bin_edges for documentation), by default 10
    verbose, optional
        Boolean indicating whether extra information should be printed,
        by default False

    Returns
    -------
        PSI, a floating point number indicating the instability of the
        population, going from one to the other (it is symmetric).
        Rule of thumb: PSI<0.1 indicates a similar distribution.
    """

    return _indicator(
        pop1,
        pop2,
        plus1=False,
        bin_data=bin_data,
        bins=bins,
        verbose=verbose,
    )


################################################


def KL(pop1, pop2, bin_data=False, bins=10, verbose=False):
    """
    Utility function (quite naive) to calculate the measured KL-divergence between
    two probability mass distributions in pop1 and pop2. Note that this returns
    infinties for empty bins in either populations.

    Parameters
    ----------
    pop1, pop2
        list, numpy.ndarray, dict, pandas.Series or pandas.DataFrame
        containing the first and population, respectively.
        They need to be of the same type. When they are:
        - list/numpy.ndarray: either the full population (ints or floats)
            that need to be binned (bin_data=True) or an ordered sequence of
            (unnamed) categories/bins with bin counts or fractions of the
            population in the bin or category.
        - dict: dictionary with category names or bin values as keys and count
            or fractions in those categories/bins as values. The two populations
            will be matched based on keys and non-existing categories in either
            population will be added with value 0.
        - pandas.Series: Series with category names or bin values as index and
            count or fractions in those categories/bins as values. The two
            populations will be matched based on index and non-existing
            categories in either population will be added with value 0.
        - pandas.DataFrame: need to have only one column, will be converted to
            Series, see definition of Series above.
        All values that indicate a count or fraction are taken as is (no
        consistency check on data type and normalization) and will be normalized
        to sum to 1 (i.e. converted into fractions)
    bin_data, optional
        Boolean indicating whether data should be binned first,
        by default False
    bins, optional
        When bin_data=True, this keyword indicates how binning is done, as
        performed by numpy.histogram. It accepts an integer (number of bins),
        list/numpy.ndarray with bin edges, a string indicating the method
        (see numpy.histogram_bin_edges for documentation), by default 10
    verbose, optional
        Boolean indicating whether extra information should be printed,
        by default False


    Returns
    -------
        KL-divergence of pop1 -> pop2: float
            Note that this is in general an assymetric measure.
    """
    a, b = _prepare_data(pop1, pop2, bin_data=bin_data, bins=bins, verbose=verbose)

    # Normalize
    a = a.astype(float) / a.sum()
    b = b.astype(float) / b.sum()

    return (a * np.log(a / b)).sum()


################################################


def _indicator(pop1, pop2, plus1=True, bin_data=False, bins=10, verbose=False):
    """Versatile code to calculate any measure we
    enable: psi, upi, weihgted or not, etc.

    For definitions, see docstring of upi/psi.
    """

    a, b = _prepare_data(pop1, pop2, bin_data=bin_data, bins=bins, verbose=verbose)

    atot = a.sum()
    btot = b.sum()

    ntot = atot + btot

    # Make fractions
    fa = a / atot
    fb = b / btot

    if plus1:
        fal = fa + (1 / ntot)
        fbl = fb + (1 / ntot)
    else:
        fal = fa
        fbl = fb

    return np.sum((fa - fb) * np.log(fal / fbl))


################################################


def _prepare_data(pop1, pop2, bin_data=False, bins=10, verbose=False):
    """
    Check the contents of pop1 and pop2 and decide
    what to do. Return two np.arrays with the binned
    data that _indicator() is going to use.

    We want to allow:
    np.array, dict, list, pd.DataFrame, pd.Series,
    But same for both!

    If dict/df/Series, check if all indices/keys exist
    in both populations, otherwise add empty category


    If bin_data is not False, _bin_data() is used.
    If False, check consistency.

    """

    # Check on file types, consistency of pop1/pop2 etc
    # Convert to numpy array

    # Type consistency check
    tp1 = type(pop1)
    if not (type(pop2) is tp1):
        raise TypeError("Both populations must be supplied in same type!")

    if bin_data:
        if tp1 in (np.ndarray, list):
            a, b = _bin_data(pop1, pop2, bins=bins, verbose=verbose)
        else:
            raise TypeError("Data to be binned should be an np.ndarray or list!")
    else:
        if tp1 in (np.ndarray, list):
            if len(pop1) != len(pop2):
                raise ValueError(
                    "Populations without category indicator need to be of same size, unless _bin_data != False"
                )

        # Adapt data type when necessary
        if tp1 is np.ndarray:
            a = pop1
            b = pop2

        elif tp1 is list:
            a = np.array(pop1)
            b = np.array(pop2)
            if verbose:
                print("Constructing arrays from population lists.")
                print(
                    "Assuming that the order of the elements in the lists is the same."
                )

        elif tp1 is dict:
            categories1 = set(pop1.keys())
            categories2 = set(pop2.keys())

            categories = list(categories1.union(categories2))
            a = np.array(
                [pop1[k] if k in pop1 else 0.0 for k in categories], np.float64
            )
            b = np.array(
                [pop2[k] if k in pop2 else 0.0 for k in categories], np.float64
            )
            if verbose:
                print(
                    f"Found the following categories in the populations: {categories}"
                )
                print(f"Values in population 1: {a}")
                print(f"Values in population 2: {b}")

        elif tp1 is pd.Series:
            # Merge the two populations in a DF and extract the two arrays
            df = pd.DataFrame(pop1, columns=["pop1"])
            df = df.merge(
                pd.DataFrame(pop2, columns=["pop2"]),
                how="outer",
                left_index=True,
                right_index=True,
            ).fillna(0)
            a = df.pop1.values
            b = df.pop2.values
            if verbose:
                print("The two populations in one DataFrame:\n", df)

        elif tp1 is pd.DataFrame:
            if pop1.shape[1] > 1:
                raise ValueError(
                    "Unclear which column of the DataFrame of pop1 to use!"
                )
            df = pop1.rename(columns={pop1.columns[0]: "pop1"})
            df = df.merge(
                pop2.rename(columns={pop2.columns[0]: "pop2"}),
                how="outer",
                left_index=True,
                right_index=True,
            ).fillna(0)
            a = df.pop1.values
            b = df.pop2.values
            if verbose:
                print("The two populations in one DataFrame:\n", df)

    return a, b


################################################


def _bin_data(aa, bb, bins=10, verbose=False):
    """
    If unbinned data has come in, do something smart
    with it here.

    Uses numpy.histogram for binning.

    bins can be:
    - int: number of bins
    - list or array: bin boundaries, from min to max, half open on right,
        like numpy, when bins=[1, 2, 3, 4], the bin edges will be [1,2), [2,3)
        and [3,4]. Note that min and max of data can fall out of this!
    - str: name of binning method recognized by np.histogram_bin_edges, one of:
        auto, fd, doane, scott, stone, rice, sturges, sqrt,
        see docs of numpy.histogram_bin_edges

    The bins will be the same for both populations.
    """

    data = np.array(list(aa) + list(bb))

    # First determine bin edges on all data if necessary, then bin.
    _, bin_edges = np.histogram(data, bins)

    bin_a, _ = np.histogram(aa, bin_edges)
    bin_b, _ = np.histogram(bb, bin_edges)

    if verbose:
        print(f"Bin edges that will be used: {np.round(bin_edges, decimals=2)}")
        print("Bin values for population1:", bin_a)
        print("Bin values for population2:", bin_b)

    return bin_a, bin_b


# For now:

if __name__ == "__main__":
    pytest.main()
