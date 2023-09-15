import json
import requests
import gtts
from pygame import mixer
from time import sleep
import pychromecast
from pychromecast import quick_play


def nuclear_check(nuclear_url: str, nuclear_text: str):
    r = requests.get(nuclear_url).text
    if nuclear_text in r:
        return True
    else:
        return False


def say_tofile(
    text: str, filename: str, lang: str = "es", slow: bool = False
):
    tts = gtts.gTTS(text, lang=lang, slow=slow)
    tts.save(filename)


def say_local(text: str):
    mixer.init()
    tmpfile = ".tmp_tts.mp3"
    say_tofile(text, tmpfile)
    mixer.music.load(tmpfile)
    mixer.music.play()
    while mixer.music.get_busy():  # wait for music to finish playing
        sleep(0.3)


def cast_url(name, url):
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[
                                                               name])
    if not chromecasts:
        print(f'No chromecast with name "{name}" discovered')
        raise Exception(f'No chromecast with name "{name}" discovered')
    print(f'Found chromecast with name "{name}"')
    cast = list(chromecasts)[0]
    browser.stop_discovery()
    media_url = url
    cast.wait()

    app_name = "default_media_receiver"
    app_data = {
        "media_id": media_url,
    }
    quick_play.quick_play(cast, app_name, app_data)

    sleep(0.25)
