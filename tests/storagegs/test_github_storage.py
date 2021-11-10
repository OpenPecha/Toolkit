import tempfile
from pathlib import Path

import pytest

from openpecha.storages import GithubStorage


def create_file_in_dir(dir_):
    fn = dir_ / "test.txt"
    fn.write_text("test")
    return fn


@pytest.mark.skip(reason="external call")
def test_add_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        storage = GithubStorage()
        create_file_in_dir(tmpdir)

        storage.add_dir(tmpdir, "test repo")

        assert storage.get_dir_with_path(tmpdir)
        assert storage.get_dir_with_name(tmpdir.name)

        storage.remove_dir_with_path(tmpdir)


@pytest.mark.skip(reason="external call")
def test_add_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        storage = GithubStorage()
        create_file_in_dir(tmpdir)
        storage.add_dir(tmpdir, "test repo")
        file_path = "test2/test.txt"
        file_content = "test file 2"

        storage.add_file(
            dir_name=tmpdir.name,
            path=file_path,
            content=file_content,
            message="add test file 2 file",
        )

        assert storage.get_file(dir_name=tmpdir.name, path=file_path)

        storage.remove_file(
            dir_name=tmpdir.name, path=file_path, message="delete test2 file"
        )
        storage.remove_dir_with_path(tmpdir)
