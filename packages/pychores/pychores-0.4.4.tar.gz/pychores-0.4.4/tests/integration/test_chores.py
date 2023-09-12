import json
from datetime import date

from flask import url_for

from pychores.model import Chore

from .helpers import get_auth_headers, object_match_dict


class TestChores:
    def test_get_chore_should_return_list_of_chores(self, client, chore_factory):
        chore1 = chore_factory()
        chore2 = chore_factory(user=chore1.user)

        r = client.get(url_for("chores.chores"), headers=get_auth_headers(chore1.user))

        assert r.status_code == 200
        chores = r.json
        assert "chores" in chores
        assert chores["chores"][0]["name"] == chore1.name
        assert chores["chores"][1]["name"] == chore2.name

    def test_chore_should_be_empty_after_insert_in_previous_test(self, db_session):
        chores = db_session.query(Chore).all()
        assert len(chores) == 0

    def test_post_chores_should_add_a_chore(self, client, headers, user, db_session):
        chore_to_post = {
            "name": "a new chore",
            "description": "description of the new chore",
            "period": 9,
        }
        headers.update(get_auth_headers(user))
        r = client.post(
            url_for("chores.chores"), data=json.dumps(chore_to_post), headers=headers
        )

        assert r.status_code == 200
        chore = db_session.query(Chore).filter_by(name=chore_to_post["name"]).one()
        assert object_match_dict(chore, chore_to_post)

    def test_post_chore_should_return_400_on_invalid_payload(
        self, client, headers, user, db_session
    ):
        chore_to_post = {
            "name": "a new chore",
            "description": "description of the new chore",
            "period": "invalid",
        }
        headers.update(get_auth_headers(user))
        r = client.post(
            url_for("chores.chores"), data=json.dumps(chore_to_post), headers=headers
        )

        assert r.status_code == 400

    def test_chore_should_be_empty(self, db_session):
        chores = db_session.query(Chore).all()
        assert len(chores) == 0


class TestChore:
    def test_get_should_return_chore(self, client, chore):
        r = client.get(
            url_for("chores.chore", chore_id=chore.id),
            headers=get_auth_headers(chore.user),
        )
        assert chore.name == r.json["name"]

    def test_put_should_change_chore(self, client, headers, chore):
        chore_to_change = {
            "name": "a new chore",
            "description": "description of the new chore",
            "period": 9,
        }
        headers.update(get_auth_headers(chore.user))
        r = client.put(
            url_for("chores.chore", chore_id=chore.id),
            data=json.dumps(chore_to_change),
            headers=headers,
        )
        assert r.status_code == 200
        assert object_match_dict(chore, chore_to_change)

    def test_delete_chore_should_delete_chore(self, client, chore, db_session):
        r = client.delete(
            url_for("chores.chore", chore_id=chore.id),
            headers=get_auth_headers(chore.user),
        )

        assert r.status_code == 204
        assert db_session.get(Chore, chore.id) is None

    def test_post_should_add_task_with_default(self, client, chore, headers):
        headers.update(get_auth_headers(chore.user))
        r = client.post(
            url_for("chores.chore", chore_id=chore.id),
            headers=headers,
            data=json.dumps({}),
        )

        assert r.status_code == 200
        assert len(chore.tasks) == 1
        assert chore.tasks[0].execution_date == date.today()

    def test_get_wrong_chore_should_abort(self, client, chore_factory):
        chore1 = chore_factory()
        chore2 = chore_factory()

        r = client.get(
            url_for("chores.chore", chore_id=chore1.id),
            headers=get_auth_headers(chore2.user),
        )

        assert r.status_code == 401
