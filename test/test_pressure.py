"""Test pressure."""

import pytest
from metar.Datatypes import pressure, UnitsError


def test_defaults():
    """Test basic usage."""
    assert pressure("1000").value() == 1000.0
    assert pressure("1000", "HPA").value() == 1000.0
    assert pressure("30", "in").value() == 30.0
    assert pressure("30", "in").string() == "30.00 inches"
    assert pressure("1000").value("MB") == 1000
    assert pressure("1000").string() == "1000.0 mb"
    assert pressure("1000", "HPA").string() == "1000.0 hPa"


def test_inputs():
    """Test various inputs."""
    assert pressure("1000").value() == 1000.0
    assert pressure("1000.0").value() == 1000.0
    assert pressure(1000).value() == 1000.0
    assert pressure(1000.0).value() == 1000.0

    assert pressure("1000", "mb").value() == 1000.0
    assert pressure("1000", "hPa").value() == 1000.0
    assert pressure("30.00", "in").value() == 30.0

    assert pressure("1000", "MB").value("MB") == 1000.0
    assert pressure("1000", "MB").value("HPA") == 1000.0
    assert pressure("1000", "HPA").value("mb") == 1000.0


def test_error_checking():
    """Test exception raising."""
    with pytest.raises(ValueError):
        pressure("A2995")
    with pytest.raises(UnitsError):
        pressure("1000", "bars")
    with pytest.raises(UnitsError):
        pressure(pressure("30.00").value, "psi")
    with pytest.raises(UnitsError):
        pressure(pressure("32.00").string, "atm")


def test_conversions():
    """Test unit conversions."""
    assert pressure("30", "in").value("in") == 30.0
    assert abs(pressure("30", "in").value("mb") - 1015.92) < 0.01
    assert abs(pressure("30", "in").value("hPa") - 1015.92) < 0.01

    assert pressure("30", "in").string("in"), "30.00 inches"
    assert pressure("30", "in").string("mb"), "1015.9 mb"
    assert pressure("30", "in").string("hPa"), "1015.9 hPa"

    assert pressure("1000", "mb").value("mb"), 1000.0
    assert pressure("1000", "mb").value("hPa"), 1000.0
    assert abs(pressure("1000", "mb").value("in") - 29.5299) < 0.0001
    assert abs(pressure("1000", "hPa").value("in") - 29.5299) < 0.0001
