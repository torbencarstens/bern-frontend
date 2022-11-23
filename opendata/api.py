import sys
import time
import urllib.parse
from functools import lru_cache
from typing import Optional, List

import requests

from .models import Point, QueryType, Station, LocationSearchResponse, Stationboard


def assemble_url(*parts):
    return "/".join([part.lstrip("/").rstrip("/") for part in parts])


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)


@lru_cache
def get(endpoint: str, *, base_url: str = "https://transport.opendata.ch", api_version: str = "v1", ttl_hash=None):
    url = assemble_url(base_url, api_version, endpoint)

    return requests.get(url)


def search_location(query: Optional[str], point: Optional[Point], _type: QueryType = QueryType.ALL) \
        -> Optional[List[Station]]:
    location_query = "?"

    if _type:
        # noinspection PyTypeChecker
        # .value is correct for getting the value from an enum instance, it's not of type `() -> Any`
        _type = urllib.parse.quote_plus(_type.value)
        location_query += f"type={_type}&"

    if query:
        query = urllib.parse.quote_plus(query)
        location_query += f"query={query}"
    elif point:
        location_query += f"x={point.x}&y={point.y}"
    if location_query == "?":
        raise ValueError("search_location requires either `query` or `point` to be passed")

    endpoint = "locations" + location_query

    response = get(endpoint, ttl_hash=get_ttl_hash())
    if response.ok:
        return LocationSearchResponse.from_json(response.text)
    else:
        print(f"failed to retrieve from backend: {response.text}", file=sys.stderr)


def get_stationboard(station_id: str, limit: int = 10) -> Optional[Stationboard]:
    endpoint = f"stationboard?id={station_id}&limit={limit}"
    response = get(endpoint, ttl_hash=get_ttl_hash())
    if response.ok:
        board = Stationboard.from_json(response.text)
        board.update()
        return board
