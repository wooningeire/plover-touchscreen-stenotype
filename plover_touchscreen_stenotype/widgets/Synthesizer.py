from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QWidget,
)

import threading
from queue import Queue

from typing import Callable

import numpy as np
import pyaudio

from .KeyWidget import KeyWidget
from ..util import on


_VOLUME_FAC = 0.08
_SAMPLE_RATE = 44100  # Hz
_BASE_FREQUENCY = 1320  # Hz
_N_SAMPLES_PER_BUFFER = 1024

_keys_to_ratios = {
    "*": 3,
    "-F": 1,
    "-P": 1.25,
    "-L": 1.5,
    "-T": 2,
    "-D": 2.5,

    "-R": 0.25,
    "-B": 0.25 * 1.25,
    "-G": 0.25 * 1.5,
    "-S": 0.5,
    "-Z": 0.5 * 1.5,

    
    "+-": 3,
    "H-": 1,
    "P-": 1.25,
    "T-": 1.5,
    "#": 2,

    "R-": 0.25,
    "W-": 0.25 * 1.25,
    "K-": 0.25 * 1.5,
    "S-": 0.5,
    "^-": 0.5 * 1.5,

    "A-": 0.5 * 1,
    "O-": 0.5 * 1.25,
    "-E": 0.5 * 1.5,
    "-U": 0.5 * 16/9,

    # "*": 2,
    # "-F": 1,
    # "-P": 1.125,
    # "-L": 1.25,
    # "-T": 1.5,
    # "-D": 5/3,

    # "-R": 0.5,
    # "-B": 0.5 * 1.125,
    # "-G": 0.5 * 1.25,
    # "-S": 0.5 * 1.5,
    # "-Z": 0.5 * 5/3,


    
    # "+-": 2,
    # "H-": 1,
    # "P-": 1.125,
    # "T-": 1.25,
    # "#": 1.5,

    # "R-": 0.5,
    # "W-": 0.5 * 1.125,
    # "K-": 0.5 * 1.25,
    # "S-": 0.5 * 1.5,
    # "^-": 0.5 * 5/3,

    # "A-": 0.5 * 1,
    # "O-": 0.5 * 1.25,
    # "-E": 0.5 * 1.5,
    # "-U": 0.5 * 16/9,
}

# _noisy_sine = lambda x: np.sin(2 * np.pi * x) * (np.random.random(len(x)) + 0.5)
_noisy_sine = lambda x: np.sin(2 * np.pi * x) * (1/3 * np.sin(4 * np.pi * x) + 1) + 1/5 * np.sin(5.81 * np.pi * x) + 1/7 * np.sin(10.41 * np.pi * x)
_sawtooth = lambda x: (2 * x % 2 - 1) * 0.5
_square = lambda x: np.sign(2 * x % 2 - 1) * 0.4

_keys_to_voices = {
    "*": _noisy_sine,
    "-F": _noisy_sine,
    "-P": _noisy_sine,
    "-L": _noisy_sine,
    "-T": _noisy_sine,
    "-D": _noisy_sine,

    "-R": _noisy_sine,
    "-B": _noisy_sine,
    "-G": _noisy_sine,
    "-S": _noisy_sine,
    "-Z": _noisy_sine,

    "-E": _square,
    "-U": _square,

    
    "+-": _sawtooth,
    "H-": _sawtooth,
    "P-": _sawtooth,
    "T-": _sawtooth,
    "S-": _sawtooth,
    "#": _sawtooth,

    "R-": _sawtooth,
    "W-": _sawtooth,
    "K-": _sawtooth,
    "W-": _sawtooth,
    "^-": _sawtooth,

    "O-": _square,
    "A-": _square,
}

# https://wiki.python.org/moin/PyQt/Playing%20a%20sound%20with%20QtMultimedia

class Synthesizer(QObject):
    stop_triggered = pyqtSignal()

    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        
        self.__audio_context = pyaudio.PyAudio()

        self.__stream = self.__audio_context.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=_SAMPLE_RATE,
            frames_per_buffer=_N_SAMPLES_PER_BUFFER,
            output=True,
        )

        # something = Queue()

        # def callback(in_data, frame_count: int, time_info: dict, status_flags):
        #     data = something.get()
        #     return (data.tobytes(), pyaudio.paContinue)
        
        # non_blocking_stream = self.__audio_context.open(
        #     format=pyaudio.paFloat32,
        #     channels=1,
        #     rate=_SAMPLE_RATE,
        #     frames_per_buffer=_N_SAMPLES_PER_BUFFER,
        #     output=True,
        #     stream_callback=callback
        # )
        # non_blocking_stream.start_stream()

        self.__message__update: Queue[tuple[tuple[float], tuple[Callable[[float], float]]]] = Queue()
        self.__message__stop: Queue[bool] = Queue()

        # https://stackoverflow.com/questions/8299303/generating-sine-wave-sound-in-python
        # Somewhat similar to how audio worklets work
        def generate_samples():
            t = 0

            while True:
                ratios, voices = self.__message__update.get()  # Blocks until message received

                while True:
                    if len(ratios) > 0:
                        samples = np.sum(
                            (
                                voice(
                                    (np.arange(_N_SAMPLES_PER_BUFFER) + t * _N_SAMPLES_PER_BUFFER)
                                    * _BASE_FREQUENCY * ratio / _SAMPLE_RATE,
                                )
                                / np.sqrt(len(ratios))
                                / (np.sqrt(ratio) if ratio < 1 else 1)
                            ).astype(np.float32)
                            for ratio, voice in zip(ratios, voices)
                        )
                    else:
                        samples = np.repeat(0, _N_SAMPLES_PER_BUFFER)

                    output_bytes = (_VOLUME_FAC * samples).tobytes()

                    self.__stream.write(output_bytes)  # Blocks for as long as audio plays

                    t += 1

                    if not self.__message__stop.empty():
                        self.__message__stop.get(False)

                        if len(ratios) > 0:
                            n_fadeout_samples = _N_SAMPLES_PER_BUFFER * 4

                            samples = np.sum(
                                (
                                    voice(
                                        (np.arange(n_fadeout_samples) + t * _N_SAMPLES_PER_BUFFER)
                                        * _BASE_FREQUENCY * ratio / _SAMPLE_RATE
                                    )
                                    * (1 - np.arange(n_fadeout_samples) / n_fadeout_samples)
                                    / np.sqrt(len(ratios))
                                    / (np.sqrt(ratio) if ratio < 1 else 1)
                                ).astype(np.float32)
                                for ratio, voice in zip(ratios, voices)
                            )

                            output_bytes = (_VOLUME_FAC * samples).tobytes()

                            self.__stream.write(output_bytes)
                            # something.put(_VOLUME_FAC * samples)
                            
                        break

                    if not self.__message__update.empty():
                        break


        thread = threading.Thread(target=generate_samples)
        thread.start()

    def update(self, current_touched_keys: set[str]):
        ratios = tuple(
            ratio
            for key, ratio in _keys_to_ratios.items()
            if key in current_touched_keys
        )

        voices = tuple(
            voice
            for key, voice in _keys_to_voices.items()
            if key in current_touched_keys
        )

        self.__message__update.put((ratios, voices))


    def stop(self):
        self.__message__stop.put(True)

    def __del__(self):
        self.__stream.stop_stream()
        self.__stream.close()

        self.__audio_context.terminate()
