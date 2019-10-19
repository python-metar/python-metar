"""Test distance."""
import pytest
from metar.Datatypes import distance, UnitsError


def test_defaults():
    """Test defaults for units."""
    assert distance("10").value() == 10.0
    assert distance("1000").value("M") == 1000.0
    assert distance("1500").string() == "1500 meters"
    assert distance("1500", None).string() == "1500 meters"
    assert distance("5", "SM").string() == "5 miles"


def test_inputs():
    """Test various inputs to distance(."""
    assert distance("10").value() == 10.0
    assert distance(10).value() == 10.0
    assert distance(10.0).value() == 10.0
    assert distance(10.0, None).value() == 10.0
    assert distance("1/2").value() == 0.5
    assert distance("1 1/2").value() == 1.5
    assert distance("11/2").value() == 1.5
    assert distance("10", gtlt=">").value() == 10.0
    assert distance("10", None, "<").value() == 10.0


def test_error_checking():
    """Test exception raising."""
    with pytest.raises(ValueError):
        distance("10SM")
    with pytest.raises(ValueError):
        distance("M1/2SM")
    with pytest.raises(ValueError):
        distance("1000", "M", "=")
    with pytest.raises(ValueError):
        distance("1000", "M", "gt")
    with pytest.raises(UnitsError):
        distance("10", "NM")
    with pytest.raises(UnitsError):
        distance(distance("1000").value, "furlongs")
    with pytest.raises(UnitsError):
        distance(distance("500").string, "yards")


def test_conversions():
    """Test conversions."""
    assert distance("5", "SM").value("SM") == 5.0
    assert distance("5", "SM").value("MI") == 5.0
    assert abs(distance("5", "SM").value("M") - 8046.7) < 0.1
    assert abs(distance("5", "SM").value("KM") - 8.05) < 0.01
    assert abs(distance("5", "SM").value("FT") - 26400.0) < 0.1

    assert distance("5000", "M").value("M"), 5000.0
    assert distance("5000", "M").value("KM"), 5.0
    assert abs(distance("5000", "M").value("SM") - 3.1) < 0.1
    assert abs(distance("5000", "M").value("MI") - 3.1) < 0.1
    assert distance("5000", "M").value("FT") == 16404.2

    assert distance("5", "KM").value("KM") == 5.0
    assert distance("5", "KM").value("M") == 5000.0
    assert abs(distance("5", "KM").value("SM") - 3.1) < 0.1
    assert distance("5", "KM").value("FT") == 16404.2

    assert distance("5280", "FT").value("FT") == 5280.0
    assert abs(distance("5280", "FT").value("SM") - 1.0) < 0.00001
    assert abs(distance("5280", "FT").value("MI") - 1.0) < 0.00001
    assert abs(distance("5280", "FT").value("KM") - 1.609) < 0.001
    assert abs(distance("5280", "FT").value("M") - 1609.34) < 0.01

    assert abs(distance("1 1/2", "SM").value("FT") - 7920.0) < 0.01
    assert abs(distance("1/4", "SM").value("FT") - 1320.0) < 0.01

    assert abs(distance("10.5", "IN").value("M") - 0.27) < 0.01
    assert abs(distance("0.066", "KM").value("IN") - 2598.43) < 0.01

    assert distance("1 1/2", "SM").string("SM") == "1 1/2 miles"
    assert distance("3/16", "SM").string("SM") == "3/16 miles"
    assert distance("1/4", "SM").string("FT") == "1320 feet"
    assert distance("1/4", "SM", "<").string("SM") == "less than 1/4 miles"
    assert distance("5280", "FT").string("KM") == "1.6 km"
    assert distance("10000", "M", ">").string("M") == "greater than 10000 meters"
