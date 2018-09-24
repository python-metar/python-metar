"""Test metar/Station.py."""
import unittest

from metar import Station


class StationTest(unittest.TestCase):
    """Unittests."""

    def test_station(self):
        """Can we build a station object."""
        st = Station.station('KDSM')
        assert st.id == 'KDSM'
