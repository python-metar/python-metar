"""Test metar/Station.py."""
from metar import Station


def test_station():
    """Can we build a station object."""
    st = Station.station("KDSM")
    assert st.id == "KDSM"
