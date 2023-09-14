import json
import requests
import gtts
import time
from pygame import mixer


class NuclearSolver:
    def __init__(self, nuclear_url: str, nuclear_text: str):
        self.nuclear_url = nuclear_url
        self.nuclear_text = nuclear_text

    def fnc_check(self):
        r = requests.get(self.nuclear_url).text
        if self.nuclear_text in r:
            return True
        else:
            return False


class VoiceSolver:
    def __init__(self, lang: str = "es", translate: str = None, slow: bool = False):
        self.lang = lang
        self.translate = translate
        self.slow = slow

    def fnc_say_to_file(self, text: str, filename: str):
        tts = gtts.gTTS(text, lang=self.lang, slow=self.slow)
        tts.save(filename)

    def fnc_say_to_speaker(self, text: str):
        mixer.init()
        tmpfile = ".tmp_tts.mp3"
        self.fnc_say_to_file(text, tmpfile)
        mixer.music.load(tmpfile)
        mixer.music.play()
        while mixer.music.get_busy():  # wait for music to finish playing
            time.sleep(1)
