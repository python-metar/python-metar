"""Test speed."""

import pytest
from metar.Datatypes import speed, UnitsError


def test_defaults():
    """Test basic usage."""
    assert speed("10").value() == 10.0
    assert speed("5").string() == "5 mps"
    assert speed("10", "KT").value() == 10.0
    assert speed("5", "KT").string() == "5 knots"
    assert speed("5", "KMH").string() == "5 km/h"
    assert speed("5", "MPH").string() == "5 mph"
    assert speed("5", None).string() == "5 mps"


def test_inputs():
    """Test inputs."""
    assert speed("10").value() == 10.0
    assert speed(10).value() == 10.0
    assert speed(10.0).value() == 10.0
    assert speed(10.0, None).value() == 10.0
    assert speed("10", gtlt=">").value() == 10.0
    assert speed("10", None, "<").value() == 10.0


def test_error_checking():
    """Test exception raising."""
    with pytest.raises(ValueError):
        speed("10KT")
    with pytest.raises(ValueError):
        speed("10", "MPS", "=")
    with pytest.raises(ValueError):
        speed("60", "KT", "gt")
    with pytest.raises(UnitsError):
        speed("10", "NM")
    with pytest.raises(UnitsError):
        speed(speed("10").value, "furlongs per fortnight")
    with pytest.raises(UnitsError):
        speed(speed("5").string, "fps")


def test_conversions():
    """Test unit conversions."""
    assert speed("10", "MPS").value("MPS") == 10.0
    assert speed("10", "MPS").value("KMH") == 36.0
    assert abs(speed("10", "MPS").value("MPH") - 22.4) < 0.1
    assert abs(speed("10", "MPS").value("KT") - 19.4) < 0.1

    assert speed("10", "KT").value("KT") == 10.0
    assert abs(speed("10", "KT").value("MPH") - 11.5) < 0.1
    assert abs(speed("10", "KT").value("MPS") - 5.1) < 0.1
    assert abs(speed("10", "KT").value("KMH") - 18.5) < 0.1

    assert speed("10", "MPH").value("MPH") == 10.0
    assert abs(speed("10", "MPH").value("KT") - 8.7) < 0.1
    assert abs(speed("10", "MPH").value("MPS") - 4.5) < 0.1
    assert abs(speed("10", "MPH").value("KMH") - 16.1) < 0.1

    assert speed("10", "KMH").value("KMH") == 10.0
    assert abs(speed("10", "KMH").value("KT") - 5.4) < 0.1
    assert abs(speed("10", "KMH").value("MPS") - 2.8) < 0.1
    assert abs(speed("10", "KMH").value("MPH") - 6.2) < 0.1
