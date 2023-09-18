# Joker API SDK
`JokerSDK` is an ~~asynchronous~~ python library to wrap around the [JokerAPI](https://jokerapi.co/) Voice API.

## Features
 -  Basic Number class integration to properly format the Numbers.
 -  Dial class to dial a phone number quickly.

## Requirements
 -  Python >= 3.10
 -  *httpx
   
Install JokerSDK
----------------
JokerSDK via PyPi:
``` console
$ pip install JokerSDK
```
Or, if you wish to download it directly from this repository:
``` console
$ python setup.py install
```

Initiation
----------
```python
from JokerAPI import JokerMethod

# Joker Initiatior
JokerInstance = JokerMethod()

# Set API Key
JokerInstance.api_key = "API_KEY"
```
Initiate the SDK Class and set a api key, this may also be done by:
```python
JokerInstance = JokerMethod(api_key="API_KEY")
```

Simple Outbound Call
-------------------------
```python
from JokerAPI import JokerMethod, Number

# Joker Initiatior
JokerInstance = JokerMethod()

# Set API Key
JokerInstance.api_key = "API_KEY"

# Dial '+111111111' from '+111111111'.
sid: str | None = JokerInstance.dial(dial_to = Number("+111111111"), dial_from = Number("111111111")) 
```
Run the function `dial`, a part of the `JokerInstance` object.

Simple Outbound Call & Playing Audio
--------------------------------------
```python
from JokerAPI import JokerMethod, Number

# Joker Initiatior
JokerInstance = JokerMethod()

# Set API Key
JokerInstance.api_key = "API_KEY"

# Dial '+111111111' from '+111111111'.
call_sid: str | None = JokerInstance.dial(dial_to = Number("+111111111"), dial_from = Number("111111111")) 

# Play audio into the live channel
JokerInstance.play(call_sid, "https://my.callbackserver.xyz/audio.wav")
```
Run the function `dial` to create an outbound call, and then use the SID to play audio into it.

Class Integration
-----------------
```python
import JokerAPI

class JokerClass(JokerAPI.JokerMethod):
    def __init__(self, **kwargs) -> None:
        super().__init__(kwargs)

    def set_key(self, key) -> None:
        self.api_key = key

    def create_outbound_call(self, *args, **kwargs) -> asyncio.run:
        return self.dial(args, kwargs)
```
Integrate the `JokerMethod` class a part of the `JokerAPI` library and use it in a custom class.

Callback server example
-----------------------
```python
import flask
from typing import Any

app: flask.Flask = flask.Flask(__name__)

@app.route("/your_project/callback", methods=["POST"])
async def callbacks() -> Any[flask.Response, flask.jsonify, str]:
    status: dict[str] = {flask.request.json['callsid']: flask.request.json['status']}

    print(f"The CallSID ({flask.request.json['callsid']}) is {flask.request.json['status'].split('.')[1]}")

    return "Any Response."

app.run("0.0.0.0", port=8080)
# Example output for when callback 'call.ringing' is sent.
#> The CallSID ('e074a38cc9a4e77ec') is ringing
```
Create a flask web app to recieve and read callback webhooks from JokerAPI proxy nodes.
