from os import mkdir
import pytest
import numpy as np
import pandas as pd
import os

from unstable_populations import psi, upi


@pytest.fixture
def flat():
    return [10, 10, 10, 10]


@pytest.fixture
def empty():
    return [1, 1, 1, 1]


@pytest.fixture
def noise():
    return [9, 11, 9, 11]


@pytest.fixture
def noise_big():
    return [99, 101, 99, 101]


@pytest.fixture
def different():
    return [1, 2, 5, 10]


@pytest.fixture
def flat_rd():
    data = np.random.uniform(0, 10, size=100)
    return data


@pytest.fixture
def large_flat_rd():
    return np.random.uniform(0, 10, size=1000)


@pytest.fixture
def gauss_rd():
    return np.random.normal(5, 1, size=100)


def make_dict(pop):
    return {i: v for i, v in enumerate(pop)}


def make_series(pop):
    return pd.Series(pop)


def make_df(pop):
    return pd.DataFrame({"x": pop})


def test_upi(flat, empty, noise, noise_big, different):
    assert upi(flat, empty) == 0
    assert upi(flat, noise) < 0.1
    assert upi(flat, noise_big) < 0.1
    assert upi(flat, noise) > upi(noise, noise_big)
    assert upi(flat, flat) == 0
    assert upi(noise, noise_big) == pytest.approx(upi(noise_big, noise))
    assert upi(flat, different) > 0.1
    assert upi(flat, noise_big) < psi(flat, noise_big)


def test_upi_containers(flat, empty, noise, noise_big, different):
    assert upi(np.array(flat), 2 * np.array(flat)) == 0
    assert upi(np.array(flat), np.array(empty)) == 0
    assert upi(np.array(flat), np.array(noise)) == upi(flat, noise)

    assert upi(make_dict(flat), make_dict(empty)) == 0
    assert upi(make_dict(flat), make_dict(noise)) == upi(flat, noise)
    assert upi(make_dict(different), {0: 1, 1: 2, 2: 5, 4: 10}) > 0.1

    assert upi(make_series(flat), make_series(empty)) == 0
    assert upi(make_series(flat), make_series(noise)) == upi(flat, noise)
    assert upi(make_series(different), pd.Series(different, index=[0, 1, 2, 4])) > 0.1

    assert upi(make_df(flat), make_df(empty)) == 0
    assert upi(make_df(flat), make_df(noise)) == upi(flat, noise)
    assert (
        upi(make_df(different), pd.DataFrame({"x": different}, index=[0, 1, 2, 4]))
        > 0.1
    )


def test_upi_binning(flat_rd, large_flat_rd, gauss_rd):
    assert upi(flat_rd, flat_rd, bin_data=True) == 0
    assert upi(flat_rd, flat_rd, bin_data=True, bins=5) == 0
    assert upi(flat_rd, flat_rd, bin_data=True, bins=[2, 4, 6, 8]) == 0
    assert (
        upi(flat_rd, large_flat_rd, bin_data=True, bins=np.array([1, 3, 5, 7, 9])) < 0.1
    )
    assert upi(flat_rd, gauss_rd, bin_data=True) > 0.1


def test_upi_errors_types(flat):
    with pytest.raises(Exception):
        upi(np.array(flat), flat)
    with pytest.raises(Exception):
        upi(make_dict(flat), flat)
    with pytest.raises(Exception):
        upi(make_series(flat), flat)
    with pytest.raises(Exception):
        upi(make_df(flat), flat)
    with pytest.raises(Exception):
        upi(make_df(flat), make_dict(flat))
    with pytest.raises(Exception):
        upi(make_df(flat), make_series(flat))
    with pytest.raises(Exception):
        upi(make_dict(flat), make_dict(flat), bin_data=True)


def test_upi_errors_data(flat):
    with pytest.raises(Exception):
        upi(flat, [5, 6, 7], bin_data=False)
    with pytest.raises(Exception):
        upi(np.array(flat), np.array([5, 6, 7]), bin_data=False)


def test_psi(flat, empty, noise, noise_big, different):
    assert psi(flat, empty) == 0
    assert psi(flat, noise) < 0.1
    assert psi(flat, noise_big) < 0.1
    assert psi(flat, noise) > psi(noise, noise_big)
    assert psi(flat, flat) == 0
    assert psi(noise, noise_big) == pytest.approx(psi(noise_big, noise))
    assert psi(flat, different) > 0.1
