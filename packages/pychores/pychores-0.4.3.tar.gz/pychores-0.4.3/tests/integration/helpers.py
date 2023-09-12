from flask_jwt_extended import create_access_token


def object_match_dict(obj, dictionary, whitelist=[]):
    for k, v in dictionary.items():
        if getattr(obj, k) != v and k not in whitelist:
            return False
    return True


def get_auth_headers(user):
    return {"Authorization": f"Bearer {create_access_token(user.username)}"}
