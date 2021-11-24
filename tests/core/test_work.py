from openpecha.work import Work


def test_work_model():
    work = Work(
        bdrc_work_id="bdrc_work_id",
        title="title",
        alternative_titles=["alternative_titles"],
        authors=["authors"],
        isRoot=True,
        Language="http://purl.bdrc.io/resource/LangBo",
        type_defination="http://purl.bdrc.io/ontology/core/Work",
        wikidata_id="wikidata_id",
        isinstances={"instance_id": {"title": "title"}},
    )

    assert work
