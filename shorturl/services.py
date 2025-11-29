import hashlib

def generate_short_code(original_url):
    # Create a stable hash to make idempotent short URL
    hash_value = hashlib.md5(original_url.encode()).hexdigest()
    return hash_value[:8]