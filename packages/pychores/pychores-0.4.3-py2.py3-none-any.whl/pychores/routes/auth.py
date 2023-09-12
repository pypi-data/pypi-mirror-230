from flask import Blueprint, current_app, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import create_access_token

from pychores.adapter.provider.hash import check_provider, hash_provider
from pychores.adapter.repository.sqla.user import UserRepo
from pychores.domain.use_cases.create_user import CreateUser
from pychores.domain.use_cases.sign_user_in import SignUserIn

from .. import respond_success

bp = Blueprint("auth", __name__, url_prefix="/api")
CORS(bp, resources={r"/*": {"origins": "*"}})


def serialize_user(user, access_token=None):
    return {
        "username": user.username,
        "email": user.email,
        "id": user.id,
        "access_token": access_token,
    }


@bp.route("/auth/signup", methods=["POST"])
def create_user():
    post_data = request.get_json()
    uc = CreateUser(UserRepo(current_app.db_session), hash_provider)
    user = uc.execute(post_data)
    return respond_success("user", serialize_user(user))


@bp.route("/auth/signin", methods=["POST"])
def signin():
    post_data = request.get_json()
    uc = SignUserIn(UserRepo(current_app.db_session), check_provider)
    user = uc.execute(post_data)
    access_token = create_access_token(identity=user.username)
    return jsonify(serialize_user(user, access_token))
