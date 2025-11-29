import hashlib
import random
import string
from django.utils import timezone
from django.db import IntegrityError
from .models import ShortURL
from django.core.cache import cache

CACHE_TIMEOUT_SECONDS = 60 * 60 * 24  # 1 day

def cache_short_url(short_code, url):
    cache_key = f"url:{short_code}"
    cache.set(cache_key, url, timeout=CACHE_TIMEOUT_SECONDS)

def get_cached_url(short_code):
    cache_key = f"url:{short_code}"
    return cache.get(cache_key)

def invalidate_cache(short_code):
    cache_key = f"url:{short_code}"
    cache.delete(cache_key)


def generate_short_code(original_url: str) -> str:
    """
    Generate short code:
    - ≤10 characters
    - deterministic base for idempotent behavior
    - random fallback part for collision resistance
    """
    base_hash = hashlib.sha256(original_url.encode()).hexdigest()[:8]
    rand = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
    return (base_hash + rand)[:10]


def get_or_create_short_url(original_url: str, user):
    """
    Business Logic:
    - Per-user idempotency
    - Collision handling w/ retries
    """
    # Return existing if user already shortened same URL
    existing = ShortURL.objects.filter(original_url=original_url, user=user).first()
    if existing:
        return existing, False

    # Create new mapping
    for _ in range(5):  # retry max 5 times
        short_code = generate_short_code(original_url)
        try:
            obj = ShortURL.objects.create(
                original_url=original_url,
                short_code=short_code,
                user=user,
            )
            return obj, True
        except IntegrityError:
            continue  # regenerate on collision
    raise ValueError("Unable to generate unique short code after multiple attempts")


def record_click(short_url_obj):
    """
    Update metadata whenever redirect occurs
    """
    short_url_obj.click_count += 1
    short_url_obj.last_accessed_at = timezone.now()
    short_url_obj.save(update_fields=["click_count", "last_accessed_at"])