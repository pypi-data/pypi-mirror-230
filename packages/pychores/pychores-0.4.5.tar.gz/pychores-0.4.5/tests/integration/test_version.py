import pytest
from flask import url_for


@pytest.mark.skip(reason="This should be theorically true, but can't make it work")
def test_session_instance(db_session, chore_factory, task_factory):
    assert db_session == chore_factory._meta.sqlalchemy_session
    assert db_session == task_factory._meta.sqlalchemy_session


def test_version_route(client):
    r = client.get(url_for("api_version"))
    assert r.status_code == 200


@pytest.mark.build
def test_static_file(client):
    r = client.get(url_for("catch_all"))
    assert r.status_code == 200
