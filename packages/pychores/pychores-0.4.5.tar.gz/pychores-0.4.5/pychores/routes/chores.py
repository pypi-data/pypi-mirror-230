from datetime import date

from flask import Blueprint, abort, current_app, jsonify, request, url_for
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, jwt_required

from pychores.adapter.repository.sqla.chore import ChoreRepo
from pychores.adapter.repository.sqla.task import TaskRepo
from pychores.domain.use_cases.add_task import AddTask
from pychores.domain.use_cases.create_chore import CreateChore, InvalidChorePayload
from pychores.domain.use_cases.delete_chore import DeleteChore
from pychores.domain.use_cases.edit_chore import EditChore
from pychores.domain.use_cases.get_chore import GetChore
from pychores.domain.use_cases.get_user_chores import GetUserChores

from .. import respond_success
from ..model import Chore, User
from .tasks import respond_task

bp = Blueprint("chores", __name__, url_prefix="/api")
CORS(bp, resources={r"/*": {"origins": "*"}})


def serialize_chore(chore):
    return {
        "id": chore.id,
        "name": chore.name,
        "description": chore.description,
        "period": chore.period,
        "last_execution_date": chore.last_execution,
        "next_execution_date": chore.next_execution,
        "is_overdue": chore.is_overdue,
    }


def respond_chore(chore):
    response = jsonify(serialize_chore(chore))
    response.headers["Location"] = url_for(".chore", chore_id=chore.id)
    return response


@bp.route("/chore", methods=["GET", "POST"])
@jwt_required()
def chores():
    current_username = get_jwt_identity()

    if request.method == "POST":
        post_data = request.get_json()
        uc = CreateChore(ChoreRepo(current_app.db_session), date.today)
        try:
            chore = uc.execute(username=current_username, payload=post_data)
        except InvalidChorePayload:
            return "Invalid chore payload", 400
        return respond_chore(chore)

    # get

    uc = GetUserChores(ChoreRepo(current_app.db_session))
    chores = uc.execute(current_username)
    serialized_chores = [serialize_chore(chore) for chore in chores]
    return respond_success("chores", serialized_chores)


@bp.route("/chore/<int:chore_id>", methods=["GET", "PUT", "DELETE", "POST"])
@jwt_required()
def chore(chore_id):
    username = get_jwt_identity()
    current_user = (
        current_app.db_session.query(User)
        .filter_by(username=get_jwt_identity())
        .first()
    )
    chore = current_app.db_session.get(Chore, chore_id)
    if chore.user_id != current_user.id:
        abort(401)
    if request.method == "PUT":
        uc = EditChore(ChoreRepo(current_app.db_session))
        chore = uc.execute(
            username=username, chore_id=chore_id, payload=request.get_json()
        )
        return respond_chore(chore)

    if request.method == "DELETE":
        uc = DeleteChore(ChoreRepo(current_app.db_session))
        uc.execute(username, chore_id=chore_id)
        return "", 204
    if request.method == "POST":
        uc = AddTask(
            task_repo=TaskRepo(current_app.db_session),
            chore_repo=ChoreRepo(current_app.db_session),
        )
        task = uc.execute(username, chore_id, payload=request.get_json() or dict())
        return respond_task(task)
    #  get
    uc = GetChore(ChoreRepo(current_app.db_session))
    chore = uc.execute(username=username, chore_id=chore_id)
    return respond_chore(chore)
