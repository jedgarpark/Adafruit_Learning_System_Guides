# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
This example will access the Hackaday.io API, grab a number like hackaday skulls,
and display it on a screen
If you can find something that spits out JSON data, we can display it!
Note that you need a hackaday API key to access the API!
"""

from os import getenv
import time
import board
from adafruit_pyportal import PyPortal

# Get WiFi details, ensure these are setup in settings.toml
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")

if None in [ssid, password]:
    raise RuntimeError(
        "WiFi settings are kept in settings.toml, "
        "please add them there. The settings file must contain "
        "'CIRCUITPY_WIFI_SSID', 'CIRCUITPY_WIFI_PASSWORD', "
        "at a minimum."
    )

# Some data sources and JSON locations to try out
CAPTION="hackaday.io/project/163309-circuitpython-hackaday"
DATA_SOURCE = "https://api.hackaday.io/v1/projects/163309?api_key="+getenv('hackaday_token')
DATA_LOCATION = ["skulls"]

# the current working directory (where this file is)
cwd = ("/"+__file__).rsplit('/', 1)[0]
pyportal = PyPortal(url=DATA_SOURCE, json_path=DATA_LOCATION,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=cwd+"/had_background.bmp",
                    text_font=cwd+"/fonts/Checkbook-50.bdf",
                    text_position=(210, 110),
                    text_color=0xFFFFFF,
                    caption_text=CAPTION,
                    caption_font=cwd+"/fonts/Arial.bdf",
                    caption_position=(10, 220),
                    caption_color=0xFFFFFF)

# track the last value so we can play a sound when it updates
last_value = 0

while True:
    try:
        value = pyportal.fetch()
        print("Response is", value)
        if last_value < value:  # ooh it went up!
            print("New skull!")
            pyportal.play_file(cwd+"/coin.wav")
        last_value = value
    except RuntimeError as e:
        print("Some error occured, retrying! -", e)
    time.sleep(60)
