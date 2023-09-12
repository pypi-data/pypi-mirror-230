import pytest

from pychores.configmodule import Config, Production


class TestConfigModule:
    def test_get_dev_config(self):
        config = Config.get_config("development")
        assert config.DEBUG

    def test_get_prod_config_raise_if_no_db_uri_is_set(self):
        with pytest.raises(ValueError):
            Config.get_config("production")

    def test_get_prod_config_raise_if_secret_is_unchanged(self, monkeypatch):
        old_db_uri = Config.SQLALCHEMY_DATABASE_URI
        Config.SQLALCHEMY_DATABASE_URI = "fake_uri"
        with pytest.raises(ValueError):
            Config.get_config("production")
        Config.SQLALCHEMY_DATABASE_URI = old_db_uri

    def test_default_config_is_prod_config(self):
        with pytest.raises(ValueError):
            config = Config.get_config("anything")
            assert isinstance(config, Production)
