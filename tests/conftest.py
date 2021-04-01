"""
This file is found by pytest and contains fixtures that can be used for all tests.
"""
import pytest

# Check if optional packages are available
try:
    from matplotlib import pyplot as plt

    m_needs_pyplot = pytest.mark.skipif(False, reason="matplotlib.pyplot can be imported.")

except (ImportError, ModuleNotFoundError):
    m_needs_pyplot = pytest.mark.skip(reason="matplotlib.pyplot is not supported in this setup.")
