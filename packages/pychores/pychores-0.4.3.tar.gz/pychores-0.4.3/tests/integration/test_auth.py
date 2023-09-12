import json

from flask import url_for

from pychores.adapter.provider.hash import hash_provider
from pychores.model import User

from .helpers import object_match_dict


class TestAuth:
    def test_signup_should_create_user(self, db_session, client, headers):
        user_to_post = {
            "username": "test_a",
            "password": "pass_test_a",
            "email": "test_a@example.com",
        }

        r = client.post(
            url_for("auth.create_user"), data=json.dumps(user_to_post), headers=headers
        )

        assert r.status_code == 200
        user = db_session.query(User).filter_by(username=user_to_post["username"]).one()
        assert object_match_dict(user, user_to_post, ["password"])

    def test_signin_should_return_token(
        self, client, user_factory, headers, db_session
    ):
        password = hash_provider("password")
        user_factory(username="user", password=password)
        signin = {"username": "user", "password": "password"}

        r = client.post(
            url_for("auth.signin"), data=json.dumps(signin), headers=headers
        )

        assert r.status_code == 200
        assert r.json["access_token"]
        assert r.json["username"] == "user"
