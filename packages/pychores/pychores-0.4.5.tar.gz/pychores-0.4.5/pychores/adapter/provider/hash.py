from flask_bcrypt import check_password_hash, generate_password_hash


def hash_provider(raw_string: str) -> str:
    return generate_password_hash(raw_string).decode("utf-8")


def check_provider(encoded_string: str, raw_string: str) -> bool:
    return check_password_hash(encoded_string, raw_string)
