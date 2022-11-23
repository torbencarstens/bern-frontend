import time
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
    if query:
        location_query += f"query={query}"
    elif point:
        location_query += f"x={point.x}&y={point.y}"
    if location_query == "?":
        raise ValueError("search_location requires either `query` or `point` to be passed")

    if _type:
        location_query += f"&type={_type}"

    endpoint = "locations" + location_query
    response = get(endpoint, ttl_hash=get_ttl_hash())
    if response.ok:
        return LocationSearchResponse.from_json(response.text)


def get_stationboard(station_id: str, limit: int = 10) -> Optional[Stationboard]:
    endpoint = f"stationboard?id={station_id}&limit={limit}"
    response = get(endpoint, ttl_hash=get_ttl_hash())
    if response.ok:
        board = Stationboard.from_json(response.text)
        board.update()
        return board
