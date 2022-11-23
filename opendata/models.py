import dataclasses
import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Coordinate:
    _type: str
    x: Optional[float] = None
    y: Optional[float] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Station:
    coordinate: Coordinate
    id: Optional[str] = None
    name: Optional[str] = None
    score: Optional[str] = None
    distance: Optional[str] = None

    def update(self):
        pass


class Location(Station):
    pass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Prognosis:
    platform: Optional[str] = None
    arrival: Optional[str] = None
    departure: Optional[str] = None
    capacity1st: Optional[str] = None
    capacity2nd: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Stop:
    station: Station
    prognosis: Prognosis
    location: Location
    departure: Optional[str] = None
    departure_timestamp: Optional[int] = None
    arrival: Optional[str] = None
    arrival_timestamp: Optional[str] = None
    delay: Optional[str] = None
    platform: Optional[str] = None
    realtime_availability: Optional[str] = None
    departure_time: Optional[str] = None

    def update(self):
        if self.departure_timestamp:
            self.departure_time = datetime.fromtimestamp(self.departure_timestamp).strftime("%H:%M")


class PassListItem(Stop):
    pass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class StationboardItem:
    stop: Stop
    category: str
    number: str
    operator: str
    to: str
    pass_list: List[PassListItem]
    name: Optional[str] = None
    subcategory: Optional[str] = None
    category_code: Optional[str] = None
    capacity1st: Optional[str] = None
    capacity2nd: Optional[str] = None

    def update(self):
        self.stop.update()
        [item.update() for item in self.pass_list]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Stationboard:
    station: Station
    stationboard: List[StationboardItem]

    def update(self):
        self.station.update()
        [item.update() for item in self.stationboard]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LocationSearchResponse:
    stations: List[Station]


@dataclasses.dataclass
class Point:
    x: float
    y: float

    def __init__(self, x: str, y: str):
        if not (x and y):
            raise ValueError("x and y have to be set")

        self.x = float(x)
        self.y = float(y)


class QueryType(enum.Enum):
    ALL = "all"
    STATION = "station"
    POINT_OF_INTEREST = "poi"
    ADDRESS = "address"
