import enum

import attrs
import cattrs
import httpx

_CLIENT = httpx.AsyncClient(base_url="https://opensky-network.org/api")


class PositionSource(enum.IntEnum):
    ADS_B = 0
    ASTERIX = 1
    MLAT = 2
    FLARM = 3


class Category(enum.IntEnum):
    NO_INFORMATION_AT_ALL = 0
    NO_ADS_B_EMITTER_CATEGORY_INFORMATION = 1
    LIGHT = 2
    SMALL = 3
    LARGE = 4
    HIGH_VORTEX_LARGE = 5
    HEAVY = 6
    HIGH_PERFORMANCE = 7
    ROTORCRAFT = 8
    GLIDER = 9
    LIGHTER_THAN_AIR = 10
    ULTRALIGHT = 12
    RESERVED = 13
    UNMANNED_AERIAL_VEHICLE = 14
    SPACE = 15
    SURFACE_EMERGENCY_VEHICLE = 16
    SURFACE_SERVICE_VEHICLE = 17
    POINT_OBSTACLE = 18
    CLUSTER_OBSTACLE = 19
    LINE_OBSTACLE = 20


@attrs.define
class State:
    icao24: str
    callsign: str | None
    origin_country: str
    time_position: int | None
    last_contact: int
    longitude: float | None
    latitude: float | None
    baro_altitude: float | None
    on_ground: bool
    velocity: float | None
    true_track: float
    vertical_rate: float
    sensors: list[int] | None
    geo_altitude: float | None
    squawk: str | None
    spi: bool
    position_source: PositionSource
    category: Category | None = None


def structure_state(state_vector: list, cl: type) -> State:
    return State(*state_vector)


cattrs.register_structure_hook(State, structure_state)


@attrs.define
class Response:
    time: int
    states: list[State]


async def get_states(
    *, lomin: float, lomax: float, lamin: float, lamax: float
) -> Response:
    resp = await _CLIENT.get(
        "states/all",
        params={
            "lomin": lomin,
            "lomax": lomax,
            "lamin": lamin,
            "lamax": lamax,
        },
    )
    resp.raise_for_status()
    return cattrs.structure(resp.json(), Response)
