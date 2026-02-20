import secrets
import string


def generate_random_name(length: int = 8) -> str:
    alphabet = string.ascii_letters
    return "".join(secrets.choice(alphabet) for _ in range(length))
