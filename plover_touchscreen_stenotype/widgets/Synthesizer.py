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


_VOLUME_FAC = 0.055
_SAMPLE_RATE = 44100  # Hz
_BASE_FREQUENCY = 440  # Hz
_N_SAMPLES_PER_BUFFER = 1024

_keys_to_ratios = {
    #region Major triads

    # "*": 3,
    # "-F": 1,
    # "-P": 1.25,
    # "-L": 1.5,
    # "-T": 2,
    # "-D": 2.5,

    # "-R": 0.25,
    # "-B": 0.25 * 1.25,
    # "-G": 0.25 * 1.5,
    # "-S": 0.5,
    # "-Z": 0.5 * 1.25,

    
    # "+-": 3,
    # "H-": 1,
    # "P-": 1.25,
    # "T-": 1.5,
    # "#": 2 * 1.25,

    # "R-": 0.25,
    # "W-": 0.25 * 1.25,
    # "K-": 0.25 * 1.5,
    # "S-": 0.5,
    # "^-": 0.5 * 1.25,

    # "A-": 0.5 * 1,
    # "O-": 0.5 * 1.25,
    # "-E": 0.5 * 1.5,
    # "-U": 0.5 * 16/9,

    #endregion


    #region Pentatonic

    "*": 1,
    "-F": 1,
    "-P": 1.125,
    "-L": 1.25,
    "-T": 1.5,
    "-D": 5/3,

    "-R": 0.25,
    "-B": 0.25 * 1.125,
    "-G": 0.25 * 1.25,
    "-S": 0.25 * 1.5,
    "-Z": 0.25 * 5/3,

    
    "+-": 2,
    "H-": 1,
    "P-": 1.125,
    "T-": 1.25,
    "#": 1.5,

    "R-": 0.25,
    "W-": 0.25 * 1.125,
    "K-": 0.25 * 1.25,
    "S-": 0.25 * 1.5,
    "^-": 0.25 * 5/3,

    "A-": 0.5 * 1,
    "O-": 0.5 * 1.25,
    "-E": 0.5 * 1.5,
    "-U": 0.5 * 16/9,

    #endregion



    "*": 1 * 4/3,
    "-F": 1,
    "-P": 1.125,
    "-L": 1.25,
    "-T": 1.5,
    "-D": 5/3,

    "-R": 0.25,
    "-B": 0.25 * 1.125,
    "-G": 0.25 * 1.25,
    "-S": 0.25 * 1.5,
    "-Z": 0.25 * 5/3,

    
    "+-": 2 * 4/3,
    "H-": 1,
    "P-": 1.125,
    "T-": 1.25,
    "#": 1.5,

    "R-": 0.25,
    "W-": 0.25 * 1.125,
    "K-": 0.25 * 1.25,
    "S-": 0.25 * 1.5,
    "^-": 0.25 * 5/3,

    "A-": 0.5 * 1,
    "O-": 0.5 * 1.5,
    "-E": 0.5 * 1.25,
    "-U": 0.5 * 16/9,

}

# _noisy_sine = lambda x: np.sin(2 * np.pi * x) * (np.random.random(len(x)) + 0.5)
# _noisy_sine = (lambda x: np.sin(2 * np.pi * x) * (1/3 * np.sin(4 * np.pi * x) + 1)
#         + 1/5 * np.sin(1.5 * np.pi * x)
#         + 1/7 * np.sin(0.5 * np.pi * x)
#         + 1/7 * np.sin(6.1039 * np.pi * x)
#         + 1/9 * np.sin(15.9504 * np.pi * x))
Voice = Callable[[np.ndarray[float]], np.ndarray[float]]

_sine: Voice = lambda x: np.sin(2 * np.pi * x)
_modified_sine: Voice = lambda x: np.abs(np.sin(2 * np.pi * x - 0.961997179279)) ** 3.5 * 2 - 1 
        # note: abs causes frequency to double
        # phase shift = asin(0.5^(1/3.5)) to make f(x) = 0 @ x = 0
_sawtooth: Voice = lambda x: (2 * x % 2 - 1) * 0.5
_triangle: Voice = lambda x: (np.arcsin(np.sin(2 * np.pi * x)) * 2 / np.pi) ** 3
_square: Voice = lambda x: np.sign(2 * x % 2 - 1) * 0.4

_keys_to_voices = {
    "*": _modified_sine,
    "-F": _modified_sine,
    "-P": _modified_sine,
    "-L": _modified_sine,
    "-T": _modified_sine,
    "-D": _modified_sine,

    "-R": _modified_sine,
    "-B": _modified_sine,
    "-G": _modified_sine,
    "-S": _modified_sine,
    "-Z": _modified_sine,

    "-E": _square,
    "-U": _square,

    
    "+-": _triangle,
    "H-": _triangle,
    "P-": _triangle,
    "T-": _triangle,
    "S-": _triangle,
    "#": _triangle,

    "R-": _triangle,
    "W-": _triangle,
    "K-": _triangle,
    "W-": _triangle,
    "^-": _triangle,

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

        self.__message__update: Queue[tuple[tuple[float], tuple[Voice]]] = Queue()
        self.__message__stop: Queue[bool] = Queue()

        def generate_samples(sample_index: np.ndarray[float], ratios: tuple[float], voices: tuple[Voice]) -> np.ndarray[float]:
            return (
                np.sum(
                    (
                        voice(sample_index * _BASE_FREQUENCY * ratio / _SAMPLE_RATE)
                        / np.sqrt(ratio / 1.5)  # Increase volume of low-pitched voices
                    )
                    for ratio, voice in zip(ratios, voices)
                )
                * _VOLUME_FAC
                / len(ratios)**0.25  # Lower volume of individual voices the more voices are playing
                * (0.75 / (1 + sample_index / (0.25 * _SAMPLE_RATE)) + 0.25)  # Trail off the longer the stroke is held
            )


        # https://stackoverflow.com/questions/8299303/generating-sine-wave-sound-in-python
        # Somewhat similar to how audio worklets work
        def stream_synthesizer():
            n_elapsed_buffers = 0

            while True:
                ratios, voices = self.__message__update.get()  # Blocks until message received

                while True:
                    if len(ratios) > 0:
                        sample_index = np.arange(_N_SAMPLES_PER_BUFFER) + n_elapsed_buffers * _N_SAMPLES_PER_BUFFER
                        samples = generate_samples(sample_index, ratios, voices)
                    else:
                        sample_index = 0
                        samples = np.repeat(0, _N_SAMPLES_PER_BUFFER)

                    output_bytes = samples.astype(np.float32).tobytes()

                    self.__stream.write(output_bytes)  # Blocks for as long as audio plays

                    n_elapsed_buffers += 1

                    if not self.__message__stop.empty():
                        self.__message__stop.get(False)
                            
                        while not self.__message__update.empty():
                            self.__message__update.get(False)

                        if len(ratios) > 0:
                            n_fadeout_samples = _N_SAMPLES_PER_BUFFER * 4
                            sample_index = np.arange(n_fadeout_samples) + n_elapsed_buffers * _N_SAMPLES_PER_BUFFER

                            samples = (generate_samples(sample_index, ratios, voices)
                                    * (1 - np.arange(n_fadeout_samples) / n_fadeout_samples))  # Fade out

                            output_bytes = samples.astype(np.float32).tobytes()

                            self.__stream.write(output_bytes)
                            # something.put(_VOLUME_FAC * samples)

                        n_elapsed_buffers = 0
                        break

                    if not self.__message__update.empty():
                        break


        thread = threading.Thread(target=stream_synthesizer)
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
