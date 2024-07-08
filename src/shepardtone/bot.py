import asyncio
import os
from datetime import datetime, timedelta

import attrs
import discord
from async_lru import alru_cache

from shepardtone.adsbdb import Aircraft, FlightRoute, get_aircraft, get_callsign

from .gis import Point, box_from_point_and_distance, haversine_distance
from .opensky import State, get_states

intents = discord.Intents.default()

client = discord.Client(intents=intents)


@attrs.define
class RecentSeen:
    last_seen: datetime
    last_posted: datetime | None


_recents: dict[str, RecentSeen] = {}


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await client.get_channel(int(os.environ["CHANNEL_ID"])).send("Shepard Tone online")
    asyncio.create_task(_check_sky_loop())


async def _null() -> None:
    return None


# Post about a single aircraft no more than once every 10 minutes.
_POST_FREQUENCY_MINUTES = 10

# Recency expiration, how long things can live in _recents without being seen.
_RECENT_EXPIRATION_MINUTES = 30


_HEADINGS = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
]


def _format_heading(degrees: float) -> str:
    return _HEADINGS[int(((degrees + 11.25) // 22.5) % 16)]


def _format_altitude(altitude: float | None, on_ground: bool) -> str:
    if on_ground or altitude <= 0:
        return "Ground"
    if altitude is None:
        return "?"
    feet = int(altitude * 3.28084)
    # If over FL050, show in flight level form, otherwise just feet.
    if feet >= 5000:
        return f"FL{feet // 100:03d}"
    return f"{feet}ft"


@alru_cache(maxsize=500)
async def _get_state_info(state: State) -> tuple[Aircraft | None, FlightRoute | None]:
    resp1, resp2 = await asyncio.gather(
        get_aircraft(state.icao24),
        get_callsign(state.callsign.strip()) if state.callsign else _null(),
        return_exceptions=True,
    )
    return (
        (
            None
            if isinstance(resp1, BaseException) or isinstance(resp1.response, str)
            else resp1.response.aircraft
        ),
        (
            None
            if isinstance(resp2, BaseException) or isinstance(resp2.response, str)
            else resp2.response.flightroute
        ),
    )


async def _format_aircraft(state: State, home: Point) -> None:
    ac, fr = await _get_state_info(state)
    dist = haversine_distance(home, Point(lat=state.latitude, lon=state.longitude))
    em = discord.Embed(
        title=f"{state.callsign.strip() if state.callsign else state.icao24}",
        description=f"{dist:.2}km away {_format_heading(state.true_track)} @ {_format_altitude(state.geo_altitude, state.on_ground)}",
    )
    if ac is not None:
        if ac.url_photo_thumbnail:
            # print(repr(ac.url_photo_thumbnail))
            em.set_thumbnail(url=ac.url_photo_thumbnail)
        em.add_field(name="type", value=ac.type, inline=False)
    if fr is not None:
        em.add_field(name="airline", value=fr.airline.name, inline=False)
    if state.callsign:
        em.add_field(
            name="links",
            value=f"[FlightAware](https://www.flightaware.com/live/flight/{state.callsign.strip()}) | [FlightRadar](https://www.flightradar24.com/{state.callsign.strip()}/)",
            inline=False,
        )
    await client.get_channel(int(os.environ["CHANNEL_ID"])).send(embed=em)


async def _check_sky():
    now = datetime.now()
    # Compute the bounding box.
    home = Point(*[float(s) for s in os.environ["BOX_CENTER"].split(",")])
    box = box_from_point_and_distance(home, float(os.environ["BOX_SIZE"]) / 2)
    # Query OpenSky.
    sky = await get_states(
        lamin=box.top_left.lat,
        lomin=box.top_left.lon,
        lamax=box.bottom_right.lat,
        lomax=box.bottom_right.lon,
    )
    states = sky.states or []
    for st in states:
        recent = _recents.get(st.icao24)
        if recent is None:
            recent = RecentSeen(last_seen=now, last_posted=None)
            _recents[st.icao24] = recent
        else:
            recent.last_seen = now

        # Check if we've posted about this recently.
        if recent.last_posted is not None and (now - recent.last_posted) < timedelta(
            minutes=_POST_FREQUENCY_MINUTES
        ):
            continue
        await _format_aircraft(st, home)
        recent.last_posted = now
    # Clean up _recents.
    for icao24, recent in _recents.items():
        if (now - recent.last_seen) > timedelta(minutes=_RECENT_EXPIRATION_MINUTES):
            _recents.pop(icao24)


async def _check_sky_loop() -> None:
    while True:
        await _check_sky()
        await asyncio.sleep(60)


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     if message.content.startswith("$hello"):
#         await message.channel.send("Hello!")


def main():
    client.run(os.environ["DISCORD_TOKEN"])
