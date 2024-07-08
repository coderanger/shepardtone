import json
from pathlib import Path

import httpx
import pytest

from shepardtone.adsbdb import get_aircraft, get_callsign


@pytest.mark.asyncio
async def test_get_aircraft(respx_mock):
    mock_data = json.load(
        Path(__file__).joinpath("../fixtures/adsbdb_aircraft.json").resolve().open()
    )
    respx_mock.get("https://api.adsbdb.com/v0/aircraft/foo").mock(
        return_value=httpx.Response(200, json=mock_data)
    )

    resp = await get_aircraft(aircraft="foo")
    assert resp.response.aircraft.type == "EMB-195 LR"


@pytest.mark.asyncio
async def test_get_callsign(respx_mock):
    mock_data = json.load(
        Path(__file__).joinpath("../fixtures/adsbdb_callsign.json").resolve().open()
    )
    respx_mock.get("https://api.adsbdb.com/v0/callsign/RYR7NW").mock(
        return_value=httpx.Response(200, json=mock_data)
    )
    resp = await get_callsign("RYR7NW")
    assert resp.response.flightroute.airline.name == "Ryanair"
    assert resp.response.flightroute.origin.country_iso_name == "GB"
    assert resp.response.flightroute.destination.country_iso_name == "PL"
