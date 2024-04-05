import json
from pathlib import Path

import httpx
import pytest

from shepardtone.adsbdb import get_aircraft


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
    pass
