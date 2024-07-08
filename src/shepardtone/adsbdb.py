import attrs
import cattrs
import httpx

_CLIENT = httpx.AsyncClient(base_url="https://api.adsbdb.com/v0/")


@attrs.define(frozen=True)
class Aircraft:
    type: str
    icao_type: str
    manufacturer: str
    mode_s: str
    registration: str
    registered_owner_country_iso_name: str
    registered_owner_country_name: str
    registered_owner_operator_flag_code: str
    registered_owner: str
    url_photo: str | None
    url_photo_thumbnail: str | None


@attrs.define(frozen=True)
class Airline:
    name: str
    icao: str
    iata: str | None
    country: str
    country_iso: str
    callsign: str | None


@attrs.define(frozen=True)
class Airport:
    country_iso_name: str
    country_name: str
    elevation: str
    iata_code: str
    icao_code: str
    latitude: float
    longitude: float
    municipality: str
    name: str


@attrs.define(frozen=True)
class FlightRoute:
    callsign: str
    callsign_icao: str | None
    callsign_iata: str | None
    airline: Airline
    origin: Airport
    destination: Airport


@attrs.define(frozen=True)
class AircraftResponse:
    aircraft: Aircraft


@attrs.define(frozen=True)
class AircraftResponseWrapper:
    response: AircraftResponse | str


@attrs.define(frozen=True)
class CallsignResponse:
    flightroute: FlightRoute


@attrs.define(frozen=True)
class CallsignResponseWrapper:
    response: CallsignResponse | str


def structure_aircraft_response_or_str(
    obj: dict | str, cl: type
) -> AircraftResponse | str:
    if isinstance(obj, str):
        return obj
    else:
        return cattrs.structure(obj, AircraftResponse)


def structure_flightroute_response_or_str(
    obj: dict | str, cl: type
) -> CallsignResponse | str:
    if isinstance(obj, str):
        return obj
    else:
        return cattrs.structure(obj, CallsignResponse)


cattrs.register_structure_hook(
    AircraftResponse | str, structure_aircraft_response_or_str
)

cattrs.register_structure_hook(
    CallsignResponse | str, structure_flightroute_response_or_str
)


async def get_aircraft(aircraft: str) -> AircraftResponseWrapper:
    resp = await _CLIENT.get(
        f"aircraft/{aircraft}",
    )
    resp.raise_for_status()
    return cattrs.structure(resp.json(), AircraftResponseWrapper)


async def get_callsign(callsign: str) -> CallsignResponseWrapper:
    resp = await _CLIENT.get(
        f"callsign/{callsign}",
    )
    resp.raise_for_status()
    return cattrs.structure(resp.json(), CallsignResponseWrapper)
