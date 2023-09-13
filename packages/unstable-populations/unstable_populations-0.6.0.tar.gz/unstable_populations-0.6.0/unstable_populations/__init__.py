"""
unstable_populations

A python package to calculate the Unstable Population Indicator
"""

from .unstable_populations import upi
from .unstable_populations import psi
from .unstable_populations import KL

from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass  # package is not installed
