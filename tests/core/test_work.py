import tempfile
from datetime import datetime

import pytest

from openpecha.core.layer import InitialCreationEnum
from openpecha.core.work import Instance, InstanceMetadata, Work


@pytest.fixture(scope="module")
def instance():
    metadata = InstanceMetadata(
        source_id="source_id",
        initial_creation_type=InitialCreationEnum.ocr,
        title="title",
        author="author",
        organization="https://bdrc.io",
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
    )
    instance_ = Instance(id="instance_id", metadata=metadata)
    return instance_


def test_instance_metadata_model():
    metadata = InstanceMetadata(
        source_id="source_id",
        initial_creation_type=InitialCreationEnum.ocr,
        title="title",
        author="author",
        organization="https://bdrc.io",
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
    )

    assert metadata.source_id == "source_id"


def test_instance_model():
    metadata = InstanceMetadata(
        source_id="source_id",
        initial_creation_type=InitialCreationEnum.ocr,
        title="title",
        author="author",
        organization="https://bdrc.io",
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
    )
    instance = Instance(id="instance_id", metadata=metadata)

    assert instance.id == "instance_id"


def test_work_model_with_all_attrs():
    work = Work(
        bdrc_work_id="bdrc_work_id",
        title="title",
        alternative_titles=["alternative_titles"],
        author="authors",
        isRoot=True,
        Language="http://purl.bdrc.io/resource/LangBo",
        type_defination="http://purl.bdrc.io/ontology/core/Work",
        wikidata_id="wikidata_id",
        instances={"instance_id": {"title": "title"}},
    )

    assert work.title == "title"


def test_work_model_without_default_attrs():
    work = Work(title="title")

    assert not work.bdrc_id


def test_add_instance(instance):
    work = Work(title="title")
    work.add_instance(instance)

    assert instance.id in work.instances


def test_remove_instance(instance):
    work = Work(title="title")
    work.add_instance(instance)
    work.remove_instance(instance.id)

    assert instance.id not in work.instances


def test_save_work_to_yml(instance):
    work = Work(title="title")
    work.add_instance(instance)

    with tempfile.TemporaryDirectory() as tmpdirname:
        work_fn = work.save_to_yaml(tmpdirname)
        assert work_fn.is_file()


def test_create_work_from_yaml(instance):
    work = Work(title="title")
    work.add_instance(instance)

    with tempfile.TemporaryDirectory() as tmpdirname:
        work_fn = work.save_to_yaml(tmpdirname)
        loaded_work = Work.from_yaml(fn=work_fn)

        assert loaded_work.id == work.id
        assert loaded_work.title == work.title
        assert loaded_work.instances == work.instances
