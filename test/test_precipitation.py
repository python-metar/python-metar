"""Test precipitation."""
from metar.Datatypes import precipitation


def test_trace():
    """How do we handle trace reports"""
    assert precipitation("0000", "IN").string() == "Trace"
    assert precipitation("0000", "IN").istrace()
    assert not precipitation("0010", "IN").istrace()
