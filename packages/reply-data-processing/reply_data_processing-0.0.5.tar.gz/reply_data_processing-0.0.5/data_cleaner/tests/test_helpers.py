import pytest
import os
from spacy import tokens
from data_cleaner.helpers import TextValidator


def test_run_setup():
    path_to_file = os.path.join("README.md")
    with open(path_to_file, "r", encoding="utf-8") as file:
        long_description = file.read()
    assert long_description is not None


class TestTextValidator:
    @pytest.mark.parametrize(
        "text, is_empty",
        [
            ("", True),
            ("just some text", False),
        ],
    )
    def test_is_empty_text(self, text, is_empty):
        assert TextValidator.is_empty_text(text) == is_empty

    def test_get_sentence_boundary_check(self):
        text = "Some text"
        doc = TextValidator.get_sentence_boundary_check(text)
        assert isinstance(doc, tokens.doc.Doc)

    @pytest.mark.parametrize(
        "text, char_limit",
        [("Some text", 3), ("Some text", 15)],
    )
    def test_has_exceeded_length(self, text, char_limit):
        expected = len(text) > char_limit
        actual = TextValidator.has_exceeded_length(text, char_limit)
        assert expected == actual
