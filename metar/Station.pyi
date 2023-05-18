from typing import Dict, Optional

from metar.Datatypes import position

class station:
    id: str
    name: str
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    position: position

    def __init__(
        self,
        id: str,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        latitude: Optional[str] = None,
        longitude: Optional[str] = None,
    ): ...

stations: Dict[str, station]
