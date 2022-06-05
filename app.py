import requests
from flask import *

from json.decoder import JSONDecodeError

app = Flask(__name__)

JSON_Edwardpoint = "http://web.archive.org/web/20190810013707if_/https://theartistunion.com/api/v3/tracks/%s.json"

@app.route("/")
async def slash():
    return """<form action=/Thingy method=GET><input name="id" id="id"><label for="id">Identifier (last bit of the URL, e.g. for https://theartistunion.com/tracks/900b3a it would be 900b3a)</label><br><button type="submit">Submit</button></form>"""

@app.route("/JSON")
async def get():
    if not request.args.get("id"):
        abort(400)
    return requests.get(JSON_Edwardpoint % request.args["id"]).json()

@app.route("/Thingy")
async def alsoget():
    try:
        json = await get()
        j = json["audio_source"], 302
    except JSONDecodeError:
        return "Failed to get track information. Does it exist?", 404
    return redirect(*j)
