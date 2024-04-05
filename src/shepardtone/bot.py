import os

import discord

from .gis import Point, box_from_point_and_distance
from .opensky import get_states

intents = discord.Intents.default()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await client.get_channel(int(os.environ["CHANNEL_ID"])).send("Shepard Tone online")
    await _check_sky()


async def _check_sky():
    # Compute the bounding box.
    home = Point(*[float(s) for s in os.environ["BOX_CENTER"].split(",")])
    box = box_from_point_and_distance(home, float(os.environ["BOX_SIZE"]) / 2)
    await client.get_channel(int(os.environ["CHANNEL_ID"])).send(repr(box))
    # Query OpenSky.
    sky = await get_states(
        lamin=box.top_left.lat,
        lomin=box.top_left.lon,
        lamax=box.bottom_right.lat,
        lomax=box.bottom_right.lon,
    )
    await client.get_channel(int(os.environ["CHANNEL_ID"])).send(repr(sky))


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     if message.content.startswith("$hello"):
#         await message.channel.send("Hello!")


def main():
    client.run(os.environ["DISCORD_TOKEN"])
