"""Test configuration and shared fixtures."""

import numpy as np
import pytest


@pytest.fixture
def sample_coordinates():
    """Sample coordinate array for testing."""
    rng = np.random.default_rng(42)
    return rng.uniform(low=[5.0, 58.0], high=[15.0, 65.0], size=(100, 2))


@pytest.fixture
def sample_element_mask():
    """Sample boolean element presence mask."""
    rng = np.random.default_rng(42)
    mask = np.zeros(100, dtype=bool)
    mask[rng.choice(100, 20, replace=False)] = True
    return mask


@pytest.fixture
def sample_signal():
    """Sample continuous signal values."""
    rng = np.random.default_rng(42)
    return rng.normal(500, 200, size=100)  # e.g., elevation
