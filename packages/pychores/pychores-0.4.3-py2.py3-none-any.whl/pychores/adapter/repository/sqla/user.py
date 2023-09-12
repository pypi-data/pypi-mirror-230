from pychores.domain.entity.user import User
from pychores.domain.use_cases.create_user import ISaveUserRepo
from pychores.domain.use_cases.sign_user_in import IGetUserRepo
from pychores.model import User as DbUser


class UserRepo(ISaveUserRepo, IGetUserRepo):
    def __init__(self, session):
        self.session = session

    def save_user(self, user: User):
        db_user = DbUser(
            username=user.username, email=user.email, password=user.password
        )

        self.session.add(db_user)
        self.session.commit()

    def get_user(self, username: str) -> User:
        db_user = self.session.query(DbUser).filter_by(username=username).first()
        return User(
            username=db_user.username,
            email=db_user.email,
            password=db_user.password,
        )
