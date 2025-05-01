from app.core.prompts.parser import ResponseParser

def test_parse_valid_json():
    parser = ResponseParser()
    result = parser.parse('{"answer": 42}', expected_format="json")
    assert result["answer"] == 42

def test_parse_invalid_json():
    parser = ResponseParser()
    res = parser.parse("{not a valid}", expected_format="json")
    assert "error" in res

def test_parse_qa_pairs():
    parser = ResponseParser()
    llm_output = "Q1: What is AI?\nA1: Artificial Intelligence\nQ2: Define ML: Machine Learning"
    parsed = parser.parse(llm_output, expected_format="qa")
    assert parsed["Q1"] == "What is AI?"
    assert parsed["A1"] == "Artificial Intelligence"
    assert parsed["Q2"] == "Define ML"
    assert parsed["Machine Learning"] == ""

def test_parse_raw_fallback():
    parser = ResponseParser()
    txt = "freeform output"
    res = parser.parse(txt)
    assert res["raw"] == "freeform output"