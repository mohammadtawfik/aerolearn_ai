import pytest
from app.models.metadata_manager import MetadataManager, MetadataSchema, MetadataField

def schema_for_pdf():
    return MetadataSchema([
        MetadataField("title", str, required=True),
        MetadataField("author", str, required=True),
        MetadataField("keywords", str, required=False),
    ])

def schema_for_video():
    return MetadataSchema([
        MetadataField("title", str, required=True),
        MetadataField("author", str, required=True),
        MetadataField("keywords", str, required=False),
    ])

def test_required_fields():
    m = MetadataManager()
    m.register_schema("pdf", schema_for_pdf())
    with pytest.raises(ValueError):
        m.set_metadata("f1", "pdf", {"title": "Only title"})
    meta = {"title": "X", "author": "A"}
    m.set_metadata("f2", "pdf", meta)
    assert m.get_metadata("f2")["data"]["title"] == "X"

def test_inheritance_logic():
    m = MetadataManager()
    m.register_schema("pdf", schema_for_pdf())
    m.set_metadata("p1", "pdf", {"title": "T", "author": "A"})
    m.set_metadata("p2", "pdf", {"title": "T2", "author": "B"})
    m.set_metadata("c1", "pdf", {"title": "CT", "author": "CA"})
    result = m.inherit_metadata(["p1", "p2"], "c1")
    assert result["title"] == "CT"
    assert result["author"] == "CA"

def test_search_and_filter():
    m = MetadataManager()
    m.register_schema("pdf", schema_for_pdf())
    m.register_schema("video", schema_for_video())
    m.set_metadata("a", "pdf", {"title": "Doc", "author": "X", "keywords": "aerodynamics, test"})
    m.set_metadata("b", "video", {"title": "Intro Movie", "author": "Y", "keywords": "video"})
    found = m.filter_by_keyword("aero")
    assert "a" in found
    assert "b" not in found
    found2 = m.search(title="Intro Movie")
    assert found2 == ["b"]
