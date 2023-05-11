UDP_SERVER_PORT = 2000
MAIN_TCP_SERVER_PORT = 2002
MAIN_SERVER_ADDRESS_CL = '127.0.0.1'
MAIN_SERVER_ADDRESS = ''
MAX_CLIENTS_COUNT = 10
MAX_BYTES_UDP = 50000
MAX_BYTES_TCP = 4096 # ВОЗМОЖНО НЕ НУЖНО
AUDIO_CHUNK_SIZE = 1024
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 2
AUDIO_BITRATE = '128k'
AUDIO_CODEC = 'mp3'
# SERVER_ADDRESS = '192.168.0.0'


# Class color
NETWORK_MANAGER = '\033[91m' + 'NetworkManager:' + '\033[0m'
SERVER = '\033[91m' + 'Server:' + '\033[0m'
CLIENT = '\033[91m' + 'Client:' + '\033[0m'
MESSAGE = '\033[91m' + 'Message:' + '\033[0m'


# FLAGS
START_FLAG = b'start'
STOP_FLAG = b'stop'
OK_FLAG = b'ok'
ERROR_FLAG = b'error'

FIRST_PORT = 4000
LAST_PORT = 5000

#DB
DB_HOST = '127.0.0.1'
DB_USERNAME = 'root'
DB_PASSWORD = '1234'
DB_DATABASE = 'mydb'