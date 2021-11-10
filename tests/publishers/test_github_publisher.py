import tempfile
from pathlib import Path

import pytest

from openpecha.publisher import GithubPublisher


def create_empty_file_in_dir(dir_):
    fn = dir_ / "test.txt"
    fn.write_text("test")


@pytest.mark.skip(reason="external call")
def test_github_publish():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        publisher = GithubPublisher()
        create_empty_file_in_dir(tmpdir)

        publisher.publish(tmpdir, "test repo")

        assert publisher.get_with_path(tmpdir)
        assert publisher.get_with_name(tmpdir.name)

        publisher.remove_with_path(tmpdir)
