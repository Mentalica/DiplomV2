import pyaudio
from consts import *


class AudioRecorder:
    def __init__(self, channels=AUDIO_CHANNELS, rate=AUDIO_SAMPLE_RATE, chunk_size=AUDIO_CHUNK_SIZE):
        self.channels = channels
        self.rate = rate
        self.chunk_size = chunk_size
        self.recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)

    def in_stream_audio(self):
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)

    def out_stream_audio(self):
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=self.channels,
                                      rate=self.rate,
                                      output=True,
                                      frames_per_buffer=self.chunk_size)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
