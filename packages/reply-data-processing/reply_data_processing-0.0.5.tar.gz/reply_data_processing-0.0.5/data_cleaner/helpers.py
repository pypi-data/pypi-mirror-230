from spacy.lang.en import English


class TextValidator:
    @staticmethod
    def is_empty_text(text):
        return text.strip() == ""

    @staticmethod
    def get_sentence_boundary_check(text):
        nlp = English()
        nlp.add_pipe("sentencizer")
        return nlp(text)

    @staticmethod
    def has_exceeded_length(text, char_limit) -> bool:
        return len(str(text)) > char_limit
