"""Fixtures for Events Calendar integration tests."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integration loading in Home Assistant pytest harness."""
    yield
