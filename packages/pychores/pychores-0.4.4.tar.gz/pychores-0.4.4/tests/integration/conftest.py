from pytest import fixture


@fixture(autouse=True)
def enable_transactional(db_session):
    pass
