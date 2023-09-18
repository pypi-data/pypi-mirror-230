import os
import math

import pytest
from bs4 import BeautifulSoup

from data_cleaner.configs import (
    conclusion_phrases,
    unwanted_phrases,
    history_tag_definers,
)
from data_cleaner.services import TextParser, EmailsProcessor, HTMLParser
import spacy
from spacy.cli import download

download('en_core_web_sm')
NER = spacy.load('en_core_web_sm')


def read_file(file_type, file_name_connector="with"):
    filename = f"email_{file_name_connector}_" + file_type
    path_to_file = os.path.join("data_cleaner", "tests", "emails_bodies", filename + ".txt")
    with open(path_to_file, "r") as email_file:
        return email_file.read()


class TestTextParser:
    def test_add_empty_lines_in_the_end(self):
        actual_result = TextParser.add_empty_lines_in_the_end("some text", 5)
        expected_result = "some text\n\n\n\n\n"
        assert actual_result == expected_result

        actual_result = TextParser.add_empty_lines_in_the_end("some text", 1)
        expected_result = "some text\n"
        assert actual_result == expected_result

    def test_get_numbers_in_string(self):
        text = "Some 7text9 16"
        numbers = TextParser.get_numbers_in_string(text)
        assert isinstance(numbers, list)
        assert isinstance(numbers[0], str)
        assert isinstance(int(numbers[0]), int)

    def test_get_first_occurred_number(self):
        text = "Some 7text9 16"
        number = TextParser.get_first_occurred_number(text)
        assert isinstance(number, int)

    def test_get_removed_punctuation(self):
        text = "Some.! #(text"
        result = TextParser.get_removed_punctuation(text)
        assert result == "Some text"

    def test_get_removed_quotes(self):
        text_list = ['"Some text"', "", "Some text"]
        for text in text_list:
            result = TextParser.get_removed_quotes(text)
            assert result == text.replace('"', "")

        # special case
        text = '"Some" text"'
        result = TextParser.get_removed_quotes(text)
        assert result == 'Some" text'


class TestEmailsProcessor:
    @pytest.fixture
    def text_placeholder(self):
        return " \n\r\n\nSome  \n  text \n\n\n\xa0\n"

    @pytest.fixture
    def ending(self):
        return "\nAnna"

    @pytest.mark.parametrize(
        "file_type",
        [
            "blockquote",
            "div_border",
            "div_gmail_quote",
            "hr_id",
            "hr_line",
            "hr_width",
            "original",
        ],
    )
    def test_get_preprocessed_input_field_text(self, file_type):
        text = read_file(file_type)
        preprocessed_text = EmailsProcessor.get_preprocessed_input_field_text(text)

        assert isinstance(preprocessed_text, str)
        assert "\xa0" not in preprocessed_text
        assert "<br" not in preprocessed_text

    @pytest.mark.parametrize(
        "file_type",
        [
            "blockquote",
            "blockquote_with_signature",
            "div_border",
            "div_gmail_quote",
            "hr_id",
            "hr_line",
            "hr_width",
            "original",
        ],
    )
    def test_get_clean_html_body(self, file_type):
        email = read_file(file_type)
        cleaned_email = EmailsProcessor.get_clean_html_body(email)

        assert "\r" not in cleaned_email
        assert "\n\n\n" not in cleaned_email
        assert "\xa0" not in cleaned_email
        assert "\n " not in cleaned_email
        assert "  " not in cleaned_email
        # signature presence checking
        assert "elyaz+ai3105 dev" not in cleaned_email

    def test_get_processed_json_email_body(self):
        initial_json = '{ "subject": "s"\\n "body": "some body" some" }'
        processed_json = EmailsProcessor.get_processed_json_email_body(initial_json)
        assert processed_json == '{ "subject": "s",\n  "body": "some body\\" some" }'

    @pytest.mark.parametrize(
        "history_definer, definer_position",
        [
            ("blockquote", 412),
            ("div_border", 6005),
            ("div_gmail_quote", 4893),
            ("hr_id", 491),
            ("hr_line", 370),
            ("hr_width", 3340),
            ("original", 530),
        ],
    )
    def test_get_email_without_history(self, history_definer, definer_position):
        email = read_file(history_definer)
        email_without_history = EmailsProcessor.get_email_without_history(
            email, history_definer, definer_position
        )

        assert isinstance(email_without_history, str)

    @pytest.mark.parametrize(
        "file_type, expected_positions",
        [
            ("blockquote", {"blockquote": 412}),
            ("div_border", {"div_border": 6005}),
            (
                "div_gmail_quote",
                {"div_gmail_quote": 4893, "blockquote": 5086},
            ),
            ("hr_id", {"hr_id": 491}),
            ("hr_line", {"hr_line": 370}),
            (
                "hr_width",
                {"hr_width": 3340, "blockquote": 5483},
            ),
            (
                "original",
                {"original": 530},
            ),
        ],
    )
    def test_get_history_tag_positions(self, file_type, expected_positions):
        email = read_file(file_type)
        positions_dict = EmailsProcessor.get_history_tag_positions(email)
        assert positions_dict == expected_positions

    def test_remove_new_line_sign(self):
        assert "\n" not in EmailsProcessor.remove_new_line_sign("\nsome\n\n\ntext\n\n")

    @pytest.mark.parametrize("text", ["  Some  \n  text \n", "", "     "])
    def test_get_removed_extra_whitespaces(self, text):
        cleaned_text = EmailsProcessor.get_removed_extra_whitespaces(text)
        assert "  " not in cleaned_text

    @pytest.mark.parametrize("text", ["Some \n\n\n text \n\n", "", "\n\n\n\n\n"])
    def test_get_reduces_new_lines_to_two(self, text):
        cleaned_text = EmailsProcessor.get_reduces_new_lines_to_two(text)
        assert "\n\n\n" not in cleaned_text

    @pytest.mark.parametrize("text", ["Some \r\n\n text \r\n", "", "\r\r\r\r"])
    def test_get_removed_carriage_returns(self, text):
        cleaned_text = EmailsProcessor.get_removed_carriage_returns(text)
        assert "\r" not in cleaned_text

    @pytest.mark.parametrize("text", ["\n Some \n \n\n text \n \n", "", "\n "])
    def test_get_removed_whitespaces_at_the_beginning_of_the_line(self, text):
        cleaned_text = (
            EmailsProcessor.get_removed_whitespaces_at_the_beginning_of_the_line(text)
        )
        assert "\n " not in cleaned_text

    @pytest.mark.parametrize(
        "text", ["\n Some \xa0 \n\xa0\n text \n\xa0\n", "", "\xa0\xa0\xa0"]
    )
    def test_get_removed_non_breaking_spaces(self, text):
        cleaned_text = EmailsProcessor.get_removed_non_breaking_spaces(text)
        assert "\xa0" not in cleaned_text

    @pytest.mark.parametrize("conclusion", conclusion_phrases)
    def test_get_email_without_conclusion_phrase(
        self, text_placeholder, conclusion, ending
    ):
        cleaned_text = EmailsProcessor.get_email_without_conclusion_phrase(
            text_placeholder + conclusion + ending
        )
        assert conclusion + ending not in cleaned_text

    def test_remove_unwanted_phrases_from_body(self):
        text = "I hope this email finds you well. Hello, how are you? I hope this email finds you well."
        result = EmailsProcessor.remove_unwanted_phrases_from_body(text)
        for phrase in unwanted_phrases:
            assert phrase not in result

    def test_get_processed_generated_email(self):
        text = 'Your result: \n{\n"subject": "some subject", \n"body": "some body",}\n Here is your output'
        result = EmailsProcessor.get_processed_generated_email(text)
        assert isinstance(result, dict)

    def test_get_processed_generated_result(self):
        text = 'Your result: \n{\n"result": "some text"\n}\n Here is your output'
        result = EmailsProcessor.get_processed_generated_result(text)
        assert isinstance(result, str)
        assert result == "some text"

        # special cases
        text = "your result:"
        result = EmailsProcessor.get_processed_generated_result(text)
        assert result is None

        text = "{}"
        with pytest.raises(Exception):
            result = EmailsProcessor.get_processed_generated_result(text)

    def test_get_extracted_email_text(self):
        result = "some result"
        assert EmailsProcessor.get_extracted_email_text(result) == result

        result = {"email": "some email", "to": "to someone"}
        assert EmailsProcessor.get_extracted_email_text(result) == result["email"]

    def test_get_cleaned_html(self):
        text = "<p>  Some  text</p>\n|&nbsp;"
        result = EmailsProcessor.get_cleaned_html(text)
        assert "<p>" not in result
        assert "</p>" not in result
        assert "  " not in result
        assert "\n|&nbsp;" not in result

    def test_get_dropped_reply_variables(self):
        text = "{{First Name}} Text with variables {Company Name}"
        actual = EmailsProcessor.get_dropped_reply_variables(text)
        assert actual == " Text with variables "

        text = "Text without reply variables"
        actual = EmailsProcessor.get_dropped_reply_variables(text)
        assert actual == actual

    def test_get_processed_reply_variables(self):
        body = "{{First Name}} Text with variables {Company Name}"
        actual = EmailsProcessor.get_processed_reply_variables(body, ["{{", "}}"])
        assert actual == " Text with variables {Company Name}"

        actual = EmailsProcessor.get_processed_reply_variables(actual, ["{", "}"])
        assert actual == " Text with variables "

    def test_get_detected_spam_words(self):
        text = "We offer you new open opportunity. Cancel at any time"
        spam_words = EmailsProcessor.get_detected_spam_words(text)
        assert "offer" in spam_words
        assert "open" in spam_words
        assert "cancel at any time" in spam_words

    def test_get_filtered_spam_words(self):
        text = "bulk email some text PUNCT  click here"
        spam_words = ["here", "bulk email", "click here", "click"]
        resulting_spam_words = EmailsProcessor.get_filtered_spam_words(text, spam_words)
        assert ["bulk email", "click here"] == resulting_spam_words

    def test_get_extracted_websites(self):
        text = "some text https://www.google.com/somerequest some text"
        result = EmailsProcessor.get_extracted_websites(text)
        assert len(result) == 1
        assert "https://www.google.com/somerequest" in result

    @pytest.mark.parametrize(
        "file_type",
        [
            "signature_name",
            "signature_name_company",
            "signature_your_name",
            "signature_dots_separator",
            "signature_blank_space_ending",
            "signature_little_tokens"
        ],
    )
    def test_get_email_without_name_signature(self, file_type):
        email = read_file(file_type)
        if "little_tokens" in email:
            # the reason why rounding with int is extended with if-clause
            assert int(len(email.split(".")) * 0.3) == 0
            assert math.ceil(len(email.split(".")) * 0.3) == 1
        resulting_email = EmailsProcessor.get_email_without_name_signature(email)
        expected_resulting_email = read_file(file_type, file_name_connector="without")
        assert resulting_email == expected_resulting_email

    def test_clean_email_ending(self):
        email_with_spaces = "Hi, John Doe. I'm writing to remind you of our last call. See you.  "
        actual_result = EmailsProcessor.clean_email_ending(email_with_spaces)
        expected_result = email_with_spaces[:-2]
        assert actual_result == expected_result

        email_with_line_break = "Hi, John Doe. Write back to me, \n"
        actual_result = EmailsProcessor.clean_email_ending(email_with_line_break)
        expected_result = email_with_line_break[:-2]
        assert actual_result == expected_result

        email_with_special_chars = "Hi, John Doe\n. Empty body.\n{}"
        actual_result = EmailsProcessor.clean_email_ending(email_with_special_chars)
        expected_result = "Hi, John Doe\n. Empty body."
        assert actual_result == expected_result

        email_with_break_tags = "Hi, John Doe\n. Empty body.\n<br/><br/>"
        assert EmailsProcessor.clean_email_ending(email_with_break_tags) == email_with_break_tags


class TestHTMLParser:
    @pytest.mark.parametrize(
        "file_type, expected_position",
        [
            ("div_border", 6005),
            ("div_gmail_quote", 4893),
            ("hr_id", 491),
            ("hr_line", 370),
            ("hr_width", 3340),
        ],
    )
    def test_get_tag_position(self, file_type, expected_position):
        email = read_file(file_type)
        tag, attribute, attribute_value = history_tag_definers[file_type]
        tag_position = HTMLParser.get_tag_position(
            email, tag, attribute, attribute_value
        )

        assert tag_position == expected_position

    @pytest.mark.parametrize(
        "file_type",
        ["blockquote", "hr_width"],
    )
    def test_get_body_without_history_using_blockquote_tag(self, file_type):
        email = read_file(file_type)
        email_without_history = (
            HTMLParser.get_body_without_history_using_blockquote_tag(email)
        )

        assert "<blockquote" not in email_without_history
        assert "<br" not in email_without_history
        assert "opt-out" not in email_without_history

    @pytest.mark.parametrize(
        "file_type, remove_parent, remove_siblings",
        [
            ("div_border", True, True),
            ("div_gmail_quote", False, False),
            ("hr_id", False, True),
            ("hr_line", False, True),
            ("hr_width", False, True),
        ],
    )
    def test_get_body_without_history_using_tag_parameter(
        self, file_type, remove_parent, remove_siblings
    ):
        tag_name, attr, attr_value = history_tag_definers[file_type]

        def _manual_check_tag_presence(test_email):
            soup = BeautifulSoup(test_email, "html.parser")

            for tag in soup.find_all(tag_name):
                try:
                    test_is_tag_present = (
                        tag
                        and tag.get(attr)
                        and attr_value in str(tag.get(attr)).replace(" ", "")
                    )
                    if test_is_tag_present:
                        return True
                except AttributeError:
                    pass

            return False

        email = read_file(file_type)
        email_without_history = HTMLParser.get_body_without_history_using_tag_parameter(
            email, tag_name, attr, attr_value, remove_parent, remove_siblings
        )

        is_tag_present = _manual_check_tag_presence(email_without_history)

        assert not is_tag_present

    @pytest.mark.parametrize(
        "file_type, split_string, expected_position",
        [
            ("blockquote", "<blockquote", 412),
            ("original", "- Original", 530),
        ],
    )
    def test_get_position_by_split(self, file_type, split_string, expected_position):
        email = read_file(file_type)
        position = HTMLParser.get_position_by_split(email, split_string)

        assert expected_position == position

    @pytest.mark.parametrize(
        "file_type",
        ["blockquote", "original"],
    )
    def test_get_removed_blockquote_tags(self, file_type):
        email = read_file(file_type)
        email_parser = BeautifulSoup(email, "html.parser")
        cleaned_email = HTMLParser.get_removed_blockquote_tags(email_parser)

        assert "<blockquote" not in cleaned_email

    @pytest.mark.parametrize(
        "file_type",
        ["blockquote", "original"],
    )
    def test_get_removed_br_tags_from_bs4_parser(self, file_type):
        email = read_file(file_type)
        email_parser = BeautifulSoup(email, "html.parser")
        cleaned_email = HTMLParser.get_removed_br_tags_from_bs4_parser(email_parser)
        assert "<br" not in cleaned_email

    def test_get_removed_br_tags_from_bs4_parser_paragraph_case(self):
        html_text = "<div><p>Some text</p></div>"
        bs4_parser = BeautifulSoup(html_text)
        processed_text = HTMLParser.get_removed_br_tags_from_bs4_parser(bs4_parser)
        assert isinstance(processed_text, BeautifulSoup)
        assert "<br" not in processed_text

    @pytest.mark.parametrize(
        "file_type",
        ["blockquote", "original"],
    )
    def test_get_text_from_bs4_parser(self, file_type):
        email = read_file(file_type)
        email_parser = BeautifulSoup(email, "html.parser")
        email_text = HTMLParser.get_text_from_bs4_parser(email_parser)

        assert isinstance(email_text, str)

    @pytest.mark.parametrize(
        "file_type",
        ["blockquote", "original", "opt_out"],
    )
    def test_get_removed_opt_out_divs(self, file_type):
        email = read_file(file_type)
        email_parser = BeautifulSoup(email, "html.parser")
        cleaned_email = HTMLParser.get_removed_opt_out_divs(email_parser)

        assert "opt-out" not in cleaned_email

    @pytest.mark.parametrize(
        "file_type",
        ["several_divs", "original"],
    )
    def test_get_removed_last_div(self, file_type):
        email = read_file(file_type)
        email_parser = BeautifulSoup(email, "html.parser")
        start_number_of_divs = len(email_parser.find_all("div"))

        cleaned_email = HTMLParser.get_removed_last_div(email_parser)
        final_number_of_divs = len(cleaned_email.find_all("div"))

        assert start_number_of_divs == final_number_of_divs + 1

    @pytest.mark.parametrize(
        "file_type",
        ["blockquote_p"],
    )
    def test_get_removed_last_p_tag(self, file_type):
        email = read_file(file_type)
        email_parser = BeautifulSoup(email, "html.parser")
        start_number_of_p_tags = len(email_parser.find_all("p"))

        cleaned_email = HTMLParser.get_removed_last_p_tag(email_parser)
        final_number_of_p_tags = len(cleaned_email.find_all("p"))

        assert start_number_of_p_tags == final_number_of_p_tags + 1

    @pytest.mark.parametrize(
        "email_first_part, email_second_part",
        [
            ("Hello, nice to meet you", "Best, Jack"),
            ("Hello, how are you? Best, Ann", "--"),
            ("Hi, my personal email is lilly@gmail.com", "-- Warm regards, Lilly"),
            ("Please call me at noon, 9875764357\nMike", ""),
        ],
    )
    def test_get_added_dashed_delimiter(self, email_first_part, email_second_part):
        email_with_dashed_delimiter = HTMLParser.get_added_dashed_delimiter(
            email_first_part, email_second_part
        )

        assert isinstance(email_with_dashed_delimiter, str)

        cleaned_email_second_part = email_second_part.replace("--", "")
        if email_second_part and cleaned_email_second_part:
            assert "--" in email_with_dashed_delimiter
        elif email_second_part:
            assert "--" not in email_with_dashed_delimiter

    def test_get_replaced_new_lines_with_br_tags(self):
        actual_result = HTMLParser.get_replaced_new_lines_with_br_tags("\nText\n\n")
        expected_result = "<br/>Text<br/><br/>"
        assert actual_result == expected_result

        actual_result = HTMLParser.get_replaced_new_lines_with_br_tags("Text")
        expected_result = "Text"
        assert actual_result == expected_result

    def test_get_parser_from_text(self):
        html_text = "<div><p>Some text</p></div>"
        assert isinstance(HTMLParser.get_parser_from_text(html_text), BeautifulSoup)

    def test_calculate_joint_strings_length(self):
        sentences = ["Some.", "Text.", "Some.", "Text."]
        text_length = HTMLParser.calculate_joint_strings_length(sentences)
        assert text_length == len(" ".join(sentences))
