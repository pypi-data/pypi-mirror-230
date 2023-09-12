from datetime import date

from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    scoped_session,
    sessionmaker,
)


class DeferedSession:
    db_uri = None
    session_local = None

    @classmethod
    def get_session_local(cls, db_uri=None):
        if db_uri is None and cls.db_uri is None:
            raise ValueError("No engine !!")
        elif db_uri is not None and cls.db_uri is not None and cls.db_uri != db_uri:
            raise ValueError(f"different engine !!! {cls.db_uri=}, {db_uri=}")
        if cls.db_uri is None:
            cls.db_uri = db_uri
            engine = create_engine(db_uri)
            cls.session_local = scoped_session(sessionmaker(engine))

        return cls.session_local


class Base(DeclarativeBase):
    pass


class Chore(Base):
    __tablename__ = "chore"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship("User", back_populates="chores")
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    period: Mapped[int]
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="chore")


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    chore_id: Mapped[int] = mapped_column(ForeignKey("chore.id"))
    chore: Mapped[Chore] = relationship("Chore", back_populates="tasks")
    execution_date: Mapped[date]


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(60))
    email: Mapped[str] = mapped_column(String(50))
    chores: Mapped[list[Chore]] = relationship(Chore, back_populates="user")
