import pytest

from pychores.model import DeferedSession


class TestDeferdSession:
    def test_should_raise_if_no_engine_has_ever_been_set(self):
        session_value = DeferedSession.session_local
        uri_value = DeferedSession.db_uri
        DeferedSession.session_local = None
        DeferedSession.db_uri = None
        with pytest.raises(ValueError):
            DeferedSession.get_session_local()
        DeferedSession.session_local = session_value
        DeferedSession.db_uri = uri_value

    def test_should_raise_if_different_engine_is_requested(self):
        with pytest.raises(ValueError):
            DeferedSession.get_session_local(db_uri="dumy uri")
