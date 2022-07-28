from .PluginSystem.server import PluginServer
from pyaudio import PyAudio
import speech_recognition
from speech_recognition import UnknownValueError
from loguru import logger
import pyttsx3

class Laplace(object):
    def __init__(self, recognition_engine="google", hot_word=None,language='en_us',mic_index=None, speaker_index=None, Plugin_path="./Plugins"):

        logger.info("Initializing plugin system")
        self._ps = PluginServer(Plugin_path=Plugin_path)
        self._audio = PyAudio()

        self._mic_index = mic_index if mic_index is not None else self._audio.get_default_input_device_info()['index']
        self._speaker_index = speaker_index if speaker_index is not None else self._audio.get_default_output_device_info()['index']

        self._hot_word = hot_word
        self._language = language
        self._waiting_for_hot_word = True if hot_word is not None else False
        self._recognition_engine = recognition_engine

        logger.info("Initializing speech recognition engine")
        self._recognizer = speech_recognition.Recognizer()
        self._mic = speech_recognition.Microphone(device_index=self._mic_index)
        self._ps.append_event("load")
        logger.info("Laplace initialized successfully!")

    @classmethod
    def get_mic_speaker_device_list(cls) -> 'list[dict]':
        audio = PyAudio()
        device_count = audio.get_device_count()
        device_list = []
        for i in range(0,device_count):
            dev_info = audio.get_device_info_by_index(i)
            device_list.append(dev_info)
            print(f'index:[{dev_info["index"]}] ,name: [{dev_info["name"]}]')
        return device_list

    def _get_recognize(self):
        logger.debug("Starting recognition...")
        with self._mic as source:
            self._recognizer.adjust_for_ambient_noise(source)
            _input_audio = self._recognizer.listen(source)
        result = None
        lang = self._language

        # example
        if self._recognition_engine == "google":
            if self._language == "en_us":
                lang = "en-US"
            try:
                result = self._recognizer.recognize_google(_input_audio,language=lang)
            except UnknownValueError:
                pass
        else:
            logger.warning("Wrong recognition engine specified.")
            raise ValueError("Wrong recognition engine specified.")
            
        return result

    def spin(self):
        while True:
            self.spin_once()
    
    def spin_once(self):
        speechs = ""
        if self._waiting_for_hot_word:
            speechs = self._get_recognize()
            if self._hot_word == speechs:
                self._waiting_for_hot_word = False
        else:
            pyttsx3.speak("Say command to me")
            speechs = self._get_recognize()
            self._ps.append_event("command",speechs)
            self._waiting_for_hot_word = True if self._hot_word is not None else False
        logger.debug(f"recognized [{speechs}]")
