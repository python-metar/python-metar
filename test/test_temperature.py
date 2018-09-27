"""Test temperature."""

import pytest
from metar.Datatypes import temperature, UnitsError


def test_defaults():
    """Test basic usage."""
    assert temperature("32").value() == 32.0
    assert temperature("32").value("C") == 32.0
    assert temperature("32").string() == "32.0 C"
    assert temperature("32", "F").string() == "32.0 F"


def test_inputs():
    """Test various inputs."""
    assert temperature("32").value() == 32.0
    assert temperature(32).value() == 32.0
    assert temperature(32.0).value() == 32.0

    assert temperature("32", "c").value() == 32.0
    assert temperature("32", "f").value() == 32.0
    assert temperature("32", "k").value() == 32.0

    assert temperature("50", "F").value("c") == 10.0
    assert temperature("50", "f").value("C") == 10.0


def test_error_checking():
    """Test exception raising."""
    with pytest.raises(ValueError):
        temperature("32C")
    with pytest.raises(ValueError):
        temperature("M10F")
    with pytest.raises(UnitsError):
        temperature("32", "J")
    with pytest.raises(UnitsError):
        temperature(temperature("32").value, "J")
    with pytest.raises(UnitsError):
        temperature(temperature("32").string, "J")


def test_conversions():
    """Test unit conversions."""
    assert temperature("32", "F").value("F") == 32.0
    assert temperature("32", "F").value("C") == 0.0
    assert temperature("50", "F").value("C") == 10.0
    assert temperature("32", "F").value("K") == 273.15

    assert temperature("20", "C").value("C") == 20.0
    assert temperature("M10", "C").value("F") == 14.0
    assert temperature("M0", "C").value("F") == 32.0
    assert temperature("20", "C").value("K") == 293.15
    assert temperature("20", "C").value("F") == 68.0
    assert temperature("30", "C").value("F") == 86.0

    assert temperature("263.15", "K").value("K") == 263.15
    assert temperature("263.15", "K").value("C") == -10.0
    assert temperature("263.15", "K").value("F") == 14.0

    assert temperature("10", "C").string("C") == "10.0 C"
    assert temperature("10", "C").string("F") == "50.0 F"
    assert temperature("10", "C").string("K") == "283.1 K"
