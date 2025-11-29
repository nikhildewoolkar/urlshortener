import hashlib
from .models import ShortURL

def generate_short_code(original_url):
    # stable hash ensures idempotency
    code = hashlib.md5(original_url.encode()).hexdigest()[:8]

    # collision handling
    while ShortURL.objects.filter(short_code=code).exists():
        code = hashlib.md5(code.encode()).hexdigest()[:10]

    return code