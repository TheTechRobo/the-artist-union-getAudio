import requests, dataclasses, re, aiohttp
from urllib.parse import unquote
from flask import *

from json.decoder import JSONDecodeError

app = Flask(__name__)

TRACK_METADATA_ENDPOINT = "https://web.archive.org/web/20190810013707id_/https://theartistunion.com/api/v3/tracks/%s.json"

@app.route("/")
async def slash():
    return render_template("index.html")

POTENTIAL_MATCHES = (
        (re.compile(r"(^https?://content\.theartistunion\.com/tracks/audio/stream_encode/[^/]+/)([^/]+)"), ("stream_encode", ":original")),
        (re.compile(r"(^https?://d2tml28x3t0b85\.cloudfront\.net/tracks/stream_files/[^/]+/[^/]+/[^/]+/original/)([^/]+/?)$"), ("stream_files", "original_files")),
        (re.compile(r"(^https?://d2tml28x3t0b85\.cloudfront\.net/tracks/original_files/[^/]+/[^/]+/[^/]+/original/)([^/]+)/?$"), None),
)

async def get(id):
    results = []
    warn = True
    async with aiohttp.ClientSession() as session:
        async with session.get(TRACK_METADATA_ENDPOINT % id) as response:
            try:
                data = await response.json()
                url = unquote(data['audio_source'])
                results.append((url, False))
            except (KeyError, JSONDecodeError):
                return []
        for match, action in POTENTIAL_MATCHES:
            nurl = url
            if match.match(nurl):
                warn = False
                nurl = match.sub(r"\1", nurl)
                if action: nurl = nurl.replace(*action, 1)
                params = {
                        "url": nurl,
                        "matchType": "prefix",
                        "fl": "original",
                        "filter": "statuscode:200"
                }
                async with session.get("https://web.archive.org/cdx/search/cdx", params=params) as response:
                    a = (await response.text()).split("\n")
                    for i in a:
                        if not i: continue
                        # Extremely hacky but I don't particularly care
                        # Workaround for when original URL is the same as track URL
                        # We could just skip this whole charade, but there might be
                        # more than one original URL, so might as well try
                        if (i, True) in results:
                            results.remove((i, True))
                        if (i, False) in results:
                            results.remove((i, False))
                        results.append((i, True))
    return results, warn

@app.route("/get")
async def alsoget():
    if not request.args.get("track"):
        abort(400)
    a = request.args.get("track")
    results, warn = await get(a)
    return render_template("fin.html", r=results, warn=warn, len=len)

