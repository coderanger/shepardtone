import attrs
import cattrs
import httpx

_CLIENT = httpx.AsyncClient(base_url="https://api.adsbdb.com/v0/")


@attrs.define
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
    url_photo: str
    url_photo_thumbnail: str


@attrs.define
class Airline:
    name: str
    icao: str
    iata: str
    country: str
    country_iso: str
    callsign: str


@attrs.define
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


@attrs.define
class FlightRoute:
    callsign: str
    callsign_icao: str
    callsign_iata: str
    airline: Airline
    origin: Airport
    destination: Airport


@attrs.define
class AircraftResponse:
    aircraft: Aircraft


@attrs.define
class AircraftResponseWrapper:
    response: AircraftResponse | str


def structure_aircraft_response_or_str(
    obj: dict | str, cl: type
) -> AircraftResponse | str:
    if isinstance(obj, str):
        return obj
    else:
        return cattrs.structure(obj, AircraftResponse)


cattrs.register_structure_hook(
    AircraftResponse | str, structure_aircraft_response_or_str
)


@attrs.define
class CallsignResponse:
    flightroute: FlightRoute


async def get_aircraft(*, aircraft: str) -> AircraftResponseWrapper:
    resp = await _CLIENT.get(
        f"aircraft/{aircraft}",
    )
    resp.raise_for_status()
    return cattrs.structure(resp.json(), AircraftResponseWrapper)


async def get_callsign(*, callsign: str) -> CallsignResponse:
    resp = await _CLIENT.get(
        f"callsign/{callsign}",
    )
    resp.raise_for_status()
    return cattrs.structure(resp.json(), CallsignResponse)
