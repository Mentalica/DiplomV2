import pyaudio
from consts import *


class AudioRecorder:
    def __init__(self, channels=AUDIO_CHANNELS, rate=AUDIO_SAMPLE_RATE, chunk_size=AUDIO_CHUNK_SIZE):
        self.out_stream = None
        self.in_stream = None
        self.channels = channels
        self.rate = rate
        self.chunk_size = chunk_size
        self.recording = False
        self.audio = pyaudio.PyAudio()
        # self.stream = None

    def in_stream_audio(self):
        self.in_stream = self.audio.open(format=pyaudio.paInt16,
                                         channels=self.channels,
                                         rate=self.rate,
                                         input=True,
                                         frames_per_buffer=self.chunk_size)

    def out_stream_audio(self):
        self.out_stream = self.audio.open(format=pyaudio.paInt16,
                                          channels=self.channels,
                                          rate=self.rate,
                                          output=True,
                                          frames_per_buffer=self.chunk_size)

    def close_in_stream(self):
        self.out_stream.stop_stream()
        self.out_stream.close()
        self.audio.terminate()

    def close_out_stream(self):
        self.in_stream.stop_stream()
        self.in_stream.close()
        self.audio.terminate()
