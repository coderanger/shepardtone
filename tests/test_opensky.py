import json
from pathlib import Path

import httpx
import pytest

from shepardtone.opensky import get_states


@pytest.mark.asyncio
async def test_get_states(respx_mock):
    mock_data = json.load(
        Path(__file__).joinpath("../fixtures/opensky_switzerland.json").resolve().open()
    )
    respx_mock.get("https://opensky-network.org/api/states/all").mock(
        return_value=httpx.Response(200, json=mock_data)
    )

    resp = await get_states(lamin=45.8389, lomin=5.9962, lamax=47.8229, lomax=10.5226)
    assert resp.time == 1712290049
    assert resp.states[1].callsign == "SWR17K  "
