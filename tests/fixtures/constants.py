import uuid
from datetime import datetime

from dynaconf import settings

_valid_status = ['requested', 'pending', 'finished']

UUID4 = str(uuid.uuid4())
NOW = datetime.utcnow().isoformat()

API_URL = settings.API_URL
API_CLIENT = settings.API_CLIENT
API_TOKEN = settings.API_TOKEN
API_CALLBACK = settings.API_CALLBACK

API_INVALID_URL = 'http://localhost/'
API_INVALID_CLIENT = 'invalid_client'
API_INVALID_TOKEN = '1nv4l1d_t0k3n'

API_PAYLOAD_SOURCE_LANGUAGE = settings.API_SOURCE_LANGUAGE
API_PAYLOAD_TARGET_LANGUAGE = settings.API_TARGET_LANGUAGE
API_PAYLOAD_INVALID_LANGUAGE = 'xx'

API_PAYLOAD = {
    'order_number': 38324,
    'price': 6,
    'source_language': 'en',
    'status': 'completed',
    'target_language': 'es',
    'text': 'Hello, world!',
    'text_format': 'text',
    'translatedText': 'Hola Mundo',
    'uid': 'b430e80d32'
}

API_PAYLOAD_STATUS_NEW = 'new'
API_PAYLOAD_STATUS_COMPLETED = 'completed'
