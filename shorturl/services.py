import hashlib
import random
import string
from django.utils import timezone
from django.db import IntegrityError
from .models import ShortURL
from django.core.cache import cache

MAX_CODE_LENGTH = 10
CACHE_TIMEOUT_SECONDS = 60 * 60 * 24

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
    return (base_hash + rand)[:MAX_CODE_LENGTH]

def get_or_create_short_url(original_url: str, user, custom_alias: str | None = None):
    """
    - Idempotent per-user for same URL.
    - Optional custom alias (with collision checks).
    - Retries on collisions for generated codes.
    """
    existing = ShortURL.objects.filter(original_url=original_url, user=user).first()
    if existing:
        if not custom_alias or existing.short_code == custom_alias:
            return existing, False

    if custom_alias:
        custom_alias = custom_alias.strip()
        if len(custom_alias) > MAX_CODE_LENGTH:
            raise ValueError("Custom alias too long (max 10 chars)")

        alias_obj = ShortURL.objects.filter(short_code=custom_alias).first()
        if alias_obj:
            if alias_obj.original_url == original_url and alias_obj.user == user:
                return alias_obj, False
            raise ValueError("Custom alias already in use")

        obj = ShortURL.objects.create(
            original_url=original_url,
            short_code=custom_alias,
            user=user,
        )
        return obj, True

    short_code = generate_short_code(original_url)

    obj = ShortURL.objects.create(
        original_url=original_url,
        short_code=short_code,
        user=user,
    )
    return obj, True


def get_or_create_short_url_alias(original_url: str, user, custom_alias: str | None = None):
    """
    - Idempotent per-user for same URL.
    - Optional custom alias (with collision checks).
    - Retries on collisions for generated codes.
    """
    existing = ShortURL.objects.filter(original_url=original_url, user=user).first()
    if existing and not custom_alias:
        return existing, False

    if custom_alias:
        custom_alias = custom_alias.strip()
        if len(custom_alias) > MAX_CODE_LENGTH:
            raise ValueError("Custom alias too long (max 10 chars)")
        alias_obj = ShortURL.objects.filter(short_code=custom_alias).first()
        if alias_obj:
            if alias_obj.original_url == original_url and alias_obj.user == user:
                return alias_obj, False
            raise ValueError("Custom alias already in use")
        obj = ShortURL.objects.create(
            original_url=original_url,
            short_code=custom_alias,
            user=user,
        )
        return obj, True

    for _ in range(5):
        short_code = generate_short_code(original_url)
        try:
            obj = ShortURL.objects.create(
                original_url=original_url,
                short_code=short_code,
                user=user,
            )
            return obj, True
        except IntegrityError:
            continue

    raise ValueError("Unable to generate unique short code after multiple attempts")


def record_click(short_url_obj):
    """
    Update metadata whenever redirect occurs
    """
    short_url_obj.click_count += 1
    short_url_obj.last_accessed_at = timezone.now()
    short_url_obj.save(update_fields=["click_count", "last_accessed_at"])