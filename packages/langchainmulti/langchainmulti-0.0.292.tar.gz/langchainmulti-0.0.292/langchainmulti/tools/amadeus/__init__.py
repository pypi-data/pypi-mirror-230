"""Amadeus tools."""

from langchainmulti.tools.amadeus.closest_airport import AmadeusClosestAirport
from langchainmulti.tools.amadeus.flight_search import AmadeusFlightSearch

__all__ = [
    "AmadeusClosestAirport",
    "AmadeusFlightSearch",
]
