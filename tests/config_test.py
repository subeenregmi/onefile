import pytest
import sys
sys.path.insert(0, "..")
import backend.config as config


class TestConfig:
    file1 = config.getConfig("temp/test_config_one.yaml")
    file2 = config.getConfig("temp/test_config_two.yaml")

    def test_load_one(self):
        assert self.file1["database"] == "onefile.db"

    def test_load_two(self):
        assert self.file1["loginRequired"]

    def test_load_three(self):
        secret = (
            "7e6dac2a942ba1d025171d1d7d9b9719e003a6c85f599d8a1b0c2fa7d8899af1"
        )
        assert self.file1["secret_key"] == secret

    def test_load_four(self):
        assert len(self.file1) == 3

    def test_secret_generation_one(self):
        assert self.file2["secret_key"]

    def test_secret_generation_two(self):
        value = self.file1.copy()
        config.checkSecret(value)
        assert value["secret_key"] == self.file1["secret_key"]
