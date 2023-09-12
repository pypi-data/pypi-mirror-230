from datetime import date

from flask import url_for

from pychores.model import Task

from .helpers import get_auth_headers


class TestTask:
    def test_get_should_return_task(self, client, task_factory):
        task = task_factory(execution_date=date(2020, 5, 1))
        r = client.get(
            url_for("tasks.task", task_id=task.id),
            headers=get_auth_headers(task.chore.user),
        )
        assert r.json["task"]["execution_date"] == "Fri, 01 May 2020 00:00:00 GMT"
        assert r.json["task"]["chore_id"] == task.chore_id

    def test_delete_should_erase_task(self, client, task, db_session):
        r = client.delete(
            url_for("tasks.task", task_id=task.id),
            headers=get_auth_headers(task.chore.user),
        )
        assert r.status_code == 204
        assert db_session.get(Task, task.id) is None
