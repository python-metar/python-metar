"""Test direction."""
import pytest
from metar.Datatypes import direction


def test_usage():
    """Test basic usage."""
    assert direction("90").value() == 90.0
    assert direction(90).value() == 90.0
    assert direction(90.0).value() == 90.0
    assert direction("90").string() == "90 degrees"
    assert direction("E").compass() == "E"


def test_error_checking():
    """Test that exceptions are raised."""
    with pytest.raises(ValueError):
        direction("North")
    with pytest.raises(ValueError):
        direction(-10)
    with pytest.raises(ValueError):
        direction("361")


def test_conversion():
    """Test conversion of str direction to numeric and back."""
    assert direction("N").value() == 0.0
    assert direction("NNE").value() == 22.5
    assert direction("NE").value() == 45.0
    assert direction("ENE").value() == 67.5
    assert direction("E").value() == 90.0
    assert direction("ESE").value() == 112.5
    assert direction("SE").value() == 135.0
    assert direction("SSE").value() == 157.5
    assert direction("S").value() == 180.0
    assert direction("SSW").value() == 202.5
    assert direction("SW").value() == 225.0
    assert direction("WSW").value() == 247.5
    assert direction("W").value() == 270.0
    assert direction("WNW").value() == 292.5
    assert direction("NW").value() == 315.0
    assert direction("NNW").value() == 337.5

    assert direction("0").compass() == "N"
    assert direction("5").compass() == "N"
    assert direction("355").compass() == "N"
    assert direction("20").compass() == "NNE"
    assert direction("60").compass() == "ENE"
    assert direction("247.5").compass() == "WSW"
