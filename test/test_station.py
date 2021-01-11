"""Test metar/Station.py."""
from metar import Station


def test_station():
    """Can we build a station object."""
    st = Station.station("KDSM")
    assert st.id == "KDSM"

def test_get_station_distance():
    """define 2 locations and get their great-circle distance
    using the Haversine approximation (i.e. using a spherical Earth"""
    # Amsterdam Airport Schiphol;;Netherlands
    st1 = Station.station(id="EHAM", country="Netherlands",
                          latitude=52.31, # in degrees North
                          longitude=4.76) # in degrees East
    # New York, Kennedy International Airport;NY;United States
    st2 = Station.station(id="KJFK",state="NY", country="United States",
                          latitude=40.64, # in degrees North
                          longitude=-73.78) # in degrees East
    distance = st1.position.getdistance(st2.position)
    distance_vallue_in_m = distance.value()
    print("distance New-York to Amsterdam is: ", distance)
    # Distance should be about: 5847 km

    expected_distance_in_m = 5847.e3 # meters
    distance_error = abs(distance_vallue_in_m - expected_distance_in_m)
    max_allowed_dist_error = 1.e3 # 1 km
    assert distance_error < max_allowed_dist_error
