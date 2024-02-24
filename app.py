import requests
from flask import *

import aiohttp

from json.decoder import JSONDecodeError

app = Flask(__name__)

TRACK_METADATA_ENDPOINT = "http://web.archive.org/web/20190810013707if_/https://theartistunion.com/api/v3/tracks/%s.json"

@app.route("/")
async def slash():
    return render_template("index.html")

async def get(id):
    async with aiohttp.ClientSession() as session:
        async with session.get(TRACK_METADATA_ENDPOINT % id) as response:
            return await response.json()

@app.route("/get")
async def alsoget():
    if not request.args.get("track"):
        abort(400)
    a = request.args.get("track")
    try:
        json = await get(a)
        j = json["audio_source"]
    except JSONDecodeError:
        return "Failed to get track information. Does it exist?", 404
    return render_template("fin.html", r=j)
