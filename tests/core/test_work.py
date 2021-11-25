from openpecha.core.work import Work


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
    print(work)

    assert work.title == "title"


def test_work_model_without_default_attrs():
    work = Work(title="title")

    assert not work.bdrc_id
