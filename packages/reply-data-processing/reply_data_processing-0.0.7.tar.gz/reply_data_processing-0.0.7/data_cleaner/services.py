import re
import sys
import json
import string
import numpy as np
import spacy
from spacy.cli import download
from bs4 import BeautifulSoup

from data_cleaner.configs import (
    history_tag_definers,
    history_substring_definers,
    conclusion_phrases,
    unwanted_phrases,
    reply_variables_separators,
    cheker_url_regex,
    spam_words,
)

sys.setrecursionlimit(10000)
download('en_core_web_sm')
NER = spacy.load('en_core_web_sm')


class EmailsProcessor:
    def __init__(self):
        pass

    @classmethod
    def get_preprocessed_input_field_text(cls, text):
        text_parser = HTMLParser.get_parser_from_text(text)
        text_parser_without_brs = HTMLParser.get_removed_br_tags_from_bs4_parser(
            text_parser
        )
        preprocessed_text = HTMLParser.get_text_from_bs4_parser(text_parser_without_brs)
        preprocessed_text = cls.get_reduces_new_lines_to_two(preprocessed_text)
        return cls.get_removed_non_breaking_spaces(preprocessed_text).strip()

    @classmethod
    def get_clean_html_body(cls, body_html) -> str:
        # Removing signature, that was added at backend
        body_html = HTMLParser.get_body_without_history_using_tag_parameter(
            body_html, "div", "class", "signature"
        )

        # checking if html-body contains specific tags that indicate history presence
        positions = cls.get_history_tag_positions(body_html)

        if positions:
            main_history_definer, main_definer_position = list(positions.items())[0]
            final_text = cls.get_email_without_history(
                body_html, main_history_definer, main_definer_position
            )

        else:
            final_text = HTMLParser.get_text_from_bs4_parser(
                HTMLParser.get_parser_from_text(body_html)
            )

        final_text = cls.get_removed_carriage_returns(final_text)
        final_text = cls.get_removed_non_breaking_spaces(final_text)
        final_text = cls.get_removed_extra_whitespaces(final_text)
        final_text = cls.get_removed_whitespaces_at_the_beginning_of_the_line(
            final_text
        )
        final_text = cls.get_reduces_new_lines_to_two(final_text)
        final_text = final_text.strip().strip("-_").strip()

        return final_text

    @staticmethod
    def get_history_tag_positions(body_html):
        positions = {}
        for key, value in history_tag_definers.items():
            positions[key] = HTMLParser.get_tag_position(body_html, *value)

        for key, value in history_substring_definers.items():
            if type(value) == str:
                if value in body_html:
                    positions[key] = HTMLParser.get_position_by_split(body_html, value)
            elif type(value) == list:
                for variation in value:
                    if variation in body_html.lower():
                        positions[key] = HTMLParser.get_position_by_split(
                            body_html.lower(), variation
                        )

        positions = {k: v for k, v in positions.items() if v is not None}
        positions = dict(sorted(positions.items(), key=lambda item: item[1]))

        return positions

    @staticmethod
    def get_email_without_history(
        body_html, main_history_definer, main_definer_position
    ):
        email_without_history = None
        if main_history_definer in history_tag_definers.keys():
            remove_parent = main_history_definer == "div_border"
            remove_siblings = main_history_definer in [
                "hr_line",
                "hr_id",
                "hr_width",
                "div_border",
            ]
            body_html = HTMLParser.get_body_without_history_using_tag_parameter(
                body_html,
                *history_tag_definers[main_history_definer],
                remove_parent=remove_parent,
                remove_siblings=remove_siblings,
            )

            email_without_history = HTMLParser.get_text_from_bs4_parser(
                HTMLParser.get_parser_from_text(body_html)
            )

        elif main_history_definer == "blockquote":
            # <blockquote> tag splits reply and history messages
            email_without_history = (
                HTMLParser.get_body_without_history_using_blockquote_tag(body_html)
            )

        elif main_history_definer == "original":
            body_html = body_html[:main_definer_position]
            email_without_history = HTMLParser.get_text_from_bs4_parser(
                HTMLParser.get_parser_from_text(body_html)
            )

        return email_without_history

    @staticmethod
    def remove_new_line_sign(text):
        return text.replace("\n", "")

    @staticmethod
    def get_removed_extra_whitespaces(text):
        return re.sub(r" +", " ", text)

    @staticmethod
    def get_removed_whitespaces_at_the_beginning_of_the_line(text):
        return re.sub(r"\n +", "\n", text)

    @staticmethod
    def get_removed_non_breaking_spaces(text):
        return text.replace("\xa0", " ")

    @staticmethod
    def get_removed_carriage_returns(text):
        return text.replace("\r", "")

    @staticmethod
    def get_reduces_new_lines_to_two(text):
        return re.sub(r"\n\n+", "\n\n", text)

    @staticmethod
    def get_email_without_conclusion_phrase(email) -> str:
        email = email.replace("\\n", "\n")

        email_lines = email.split("\n")

        new_email = ""
        signature_found = False

        for i, line in enumerate(email_lines):
            for phrase in conclusion_phrases:
                if line.lower().startswith(phrase):
                    new_email = "\n".join(email_lines[:i])
                    signature_found = True
                    break

        if not new_email and not signature_found:
            return email

        return new_email

    @staticmethod
    def remove_unwanted_phrases_from_body(body):
        for phrase in unwanted_phrases:
            body = body.replace(phrase, "")
        return body

    @staticmethod
    def get_processed_json_email_body(json_string):
        json_string = json_string.replace("\\n", "\n")
        json_string = re.sub(r'"\n *"body":', '",\n  "body":', json_string)

        if json_string.count('"') > 8:
            before_body_key, after_body_key = json_string.split('"body":')
            after_body_key = after_body_key.strip()
            body_value, after_body_value = after_body_key.rsplit('"', 1)
            body_value = re.sub('(?<=[\w\s])"', '\\"', body_value[1:])

            json_string = (
                before_body_key + '"body": "' + body_value + '"' + after_body_value
            )

        return json_string

    @classmethod
    def get_processed_generated_email(cls, text):
        begin_index = text.find("{")
        end_index = text.rfind("}")
        json_string = text[begin_index : end_index + 1]
        json_string = cls.get_processed_json_email_body(json_string)

        try:
            json_response = json.loads(json_string, strict=False)
        except ValueError:
            try:
                # removing extra comma after last json field and retrying loading data
                json_string = '"'.join(json_string.rsplit('",', 1))
                json_response = json.loads(json_string)
            except ValueError:
                raise Exception(f"Unable to parse output: {repr(json_string)}")

        json_response["body"] = EmailsProcessor.get_email_without_conclusion_phrase(
            json_response["body"]
        ).strip()
        json_response["body"] = cls.remove_unwanted_phrases_from_body(
            json_response["body"]
        )
        return json_response

    @staticmethod
    def get_end_of_email_with_first_token_by_separator(email):
        separator = "<br/>" if "<br/>" in email else "."
        n_last_tokens = len(email.split(separator)) * 0.3
        n_last_tokens = int(n_last_tokens) if n_last_tokens >= 1 else 1
        end_of_email = [token for token in email.split(separator) if token][-n_last_tokens:]
        first_token_from_end_of_email = end_of_email[0]
        end_of_email = " ".join(end_of_email).replace("\n", "")
        # clean up tokens from special characters
        end_of_email = re.sub("[^A-Za-z0-9,. ]+", " ", end_of_email)
        return end_of_email, first_token_from_end_of_email

    @staticmethod
    def get_email_without_name_signature(email) -> str:
        pattern = "\[.*?\]"
        compiled_pattern = re.compile(pattern)
        if bool(re.search(compiled_pattern, email)):
            email = re.sub(pattern, "", email)
        else:
            end_of_email, first_token_from_end_of_email = \
                EmailsProcessor.get_end_of_email_with_first_token_by_separator(email)

            signature = NER(end_of_email)
            entities_to_remove = " ".join(
                [str(entity) for entity in signature.ents if entity.label_ in ["PERSON", "ORG"]])

            resulting_end_of_email = "".join([
                first_token_from_end_of_email,
                email.split(first_token_from_end_of_email)[1]
            ])
            # removing discovered entities
            if entities_to_remove:
                for entity in entities_to_remove.split(" "):
                    resulting_end_of_email = "".join(resulting_end_of_email.rsplit(entity, 1))
            email = email.split(first_token_from_end_of_email)[0] + resulting_end_of_email

            # cleaning up
        email = EmailsProcessor.clean_email_ending(email)
        email = email.replace("<br/><br/><br/>", "<br/><br/>")
        email = email.replace("  ", " ")
        return email

    @staticmethod
    def clean_email_ending(email):
        if email.endswith("<br/>"):
            return email
        if email.endswith(" "):
            # recursion to avoid several blank spaces
            email = EmailsProcessor.clean_email_ending(email[:-1])
        if email.endswith("\n"):
            email = EmailsProcessor.clean_email_ending(email[:-1])
        for char in reversed(email):
            if bool(re.search("[^A-Za-z0-9,.]", char)):
                email = email[:-1]
            else:
                break
        # to avoid companies endings being skipped in some cases
        companies_endings = ["io", "com", "inc", "Inc", "org"]
        for ending in companies_endings:
            if email.endswith(ending):
                email = email.replace(ending, "")
        return email

    @classmethod
    def get_processed_generated_result(cls, text):
        begin_index = text.find("{")
        end_index = text.rfind("}")
        json_string = text[begin_index : end_index + 1]

        # fixing commas at the end of pairs "key": "value"
        # because models pretty often output invalid json
        json_string = json_string.replace('"\n', '",\n')
        json_string = '"'.join(json_string.rsplit('",', 1))

        try:
            json_response = json.loads(json_string, strict=False)
        except ValueError:
            if not json_string:
                return
            raise Exception(f"Unable to parse output: {json_string}")

        result = cls.get_extracted_email_text(json_response["result"])

        return result

    @staticmethod
    def get_extracted_email_text(result):
        while isinstance(result, dict):
            for key in ["email", "body", "email_body"]:
                if key in result.keys():
                    result = result[key]
                    break

        return result

    @classmethod
    def get_cleaned_html(cls, text):
        pattern = re.compile(r"\n|&nbsp;")
        clean_text = re.sub(pattern, " ", text)
        pattern = re.compile("<.*?>")
        clean_text = re.sub(pattern, " ", clean_text)
        # pattern = re.compile(r'\s+')
        clean_text = cls.get_removed_extra_whitespaces(clean_text)
        return clean_text

    @classmethod
    def get_dropped_reply_variables(cls, body):
        for separator in reply_variables_separators:
            body = cls.get_processed_reply_variables(body, separator)

        return body

    @classmethod
    def get_processed_reply_variables(cls, body, separator):
        variables = re.compile(rf"\{separator[0]}(.*?)\{separator[1]}").findall(body)
        if variables:
            variables = [separator[0] + var + separator[1] for var in variables]
            variables = "|".join(variables)
            body = re.sub(variables, "", body)
            body = cls.get_removed_extra_whitespaces(body)

        return body

    @classmethod
    def get_detected_spam_words(cls, text):
        text = cls.get_dropped_reply_variables(text)
        regex = re.compile("[%s]" % re.escape(string.punctuation))

        text = text.lower()
        text = regex.sub(" PUNCT ", text)
        text = " " + text.strip() + " "

        detected_spam_words = []
        for spam_words_category in spam_words.keys():
            for token in spam_words[spam_words_category]:
                if (" " + token.lower() + " ") in text:
                    detected_spam_words.append(token.lower())

        detected_spam_words = cls.get_filtered_spam_words(text, detected_spam_words)

        return detected_spam_words

    @staticmethod
    def get_filtered_spam_words(text, spam_words_from_text):
        words_to_drop = []
        resulting_list = [word.split() for word in spam_words_from_text]
        one_word_spam_words = [word[0] for word in resulting_list if len(word) == 1]
        phrase_spam_words = [phrase for phrase in resulting_list if len(phrase) > 1]
        for spam_word in one_word_spam_words:
            spam_words_match = np.array(
                [spam_word in phrase for phrase in phrase_spam_words]
            )
            if np.sum(spam_words_match) > 0:
                for i in np.where(spam_words_match)[0]:
                    if spam_word not in text.replace(
                        " ".join(phrase_spam_words[i]), " "
                    ):
                        words_to_drop.append(spam_word)

        if words_to_drop:
            spam_words_from_text = [
                x for x in spam_words_from_text if x not in words_to_drop
            ]

        return spam_words_from_text

    @staticmethod
    def get_extracted_websites(text):
        if not isinstance(text, str):
            return

        websites = re.findall(cheker_url_regex, text)

        websites = list(set(websites))

        if websites:
            websites = [w.rstrip("/") for w in websites]
            websites = [w for w in websites if w]

        return websites


class TextParser:
    # TO-DO: add methods related to parsing text, this class may call HTML Parser methods
    @staticmethod
    def add_empty_lines_in_the_end(text, n_empty_lines):
        return text + "\n" * n_empty_lines

    @staticmethod
    def get_numbers_in_string(text):
        return re.findall(r"\d+", text)

    @staticmethod
    def get_first_occurred_number(text):
        return int(TextParser.get_numbers_in_string(text)[0])

    @staticmethod
    def get_removed_punctuation(text):
        return text.translate(str.maketrans("", "", string.punctuation))

    @staticmethod
    def get_removed_quotes(text):
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return text


class HTMLParser:
    def __init__(self):
        pass

    @classmethod
    def get_tag_position(cls, html_code, tag_name: str, attr, attr_value) -> int:
        soup = cls.get_parser_from_text(html_code)

        for tag in soup.find_all(tag_name):
            try:
                clean_attribute_value = str(tag.get(attr)).replace(" ", "")
                if tag and tag.get(attr) and attr_value in clean_attribute_value:
                    html_lines = html_code.split("\n")
                    return len(
                        html_code.split(
                            html_lines[tag.sourceline - 1][tag.sourcepos :]
                        )[0]
                    )
            except AttributeError:
                pass

    @staticmethod
    def get_position_by_split(html_code, split_string) -> int:
        return len(html_code.split(split_string)[0])

    @classmethod
    def get_body_without_history_using_tag_parameter(
        cls,
        html_code,
        tag_name,
        attr,
        attr_value,
        remove_parent=False,
        remove_siblings=False,
    ) -> str:
        soup = cls.get_parser_from_text(html_code)

        for tag in soup.find_all(tag_name):
            try:
                if (
                    tag
                    and tag.get(attr)
                    and attr_value in str(tag.get(attr)).replace(" ", "")
                ):
                    if remove_siblings:
                        for el in tag.find_next_siblings():
                            el.decompose()
                    if remove_parent:
                        for el in tag.parent.find_next_siblings():
                            el.decompose()
                    tag.decompose()
            except AttributeError:
                pass

        return str(soup)

    @classmethod
    def get_body_without_history_using_blockquote_tag(cls, html_code) -> str:
        first_part, second_part = html_code.split("<blockquote", 1)

        second_part = "<blockquote" + second_part

        f_body = cls.get_parser_from_text(first_part)
        f_body = cls.get_removed_br_tags_from_bs4_parser(f_body)

        s_body = cls.get_parser_from_text(second_part)
        s_body = cls.get_removed_br_tags_from_bs4_parser(s_body)

        # we should remove last div in first part (it has part "On April 14, 2022 4:45 PM …")
        if f_body.find("div"):
            f_body = cls.get_removed_last_div(f_body)
        elif f_body.find("p"):
            f_body = cls.get_removed_last_p_tag(f_body)

        # we also delete the opt-out div tag from reply
        if f_body.find("div"):
            f_body = cls.get_removed_opt_out_divs(f_body)

        # removing the history by removing blockquotes
        f_body = cls.get_removed_blockquote_tags(f_body)
        s_body = cls.get_removed_blockquote_tags(s_body)

        f_part_modified = cls.get_text_from_bs4_parser(f_body)
        s_part_modified = cls.get_text_from_bs4_parser(s_body)

        # composing the result
        # adding -- delimiter to split signature and reply in future easily
        final_text = cls.get_added_dashed_delimiter(f_part_modified, s_part_modified)

        return final_text

    @staticmethod
    def get_parser_from_text(text):
        return BeautifulSoup(text, "html.parser")

    @staticmethod
    def get_removed_last_div(body):
        try:
            body.find_all("div")[-1].decompose()
            return body
        except Exception:
            pass

    @staticmethod
    def get_removed_last_p_tag(body):
        try:
            body.find_all("p")[-1].decompose()
            return body
        except Exception:
            pass

    @staticmethod
    def get_removed_opt_out_divs(body):
        for div in body.select("div.opt-out"):
            div.extract()

        return body

    @staticmethod
    def get_removed_blockquote_tags(body):
        for bq in body.find_all("blockquote"):
            bq.replace_with("\n")

        return body

    @staticmethod
    def get_removed_br_tags(body):
        return re.sub("<br ?/?>", "\n", body)

    @staticmethod
    def get_removed_br_tags_from_bs4_parser(body):
        for br in body.find_all("br"):
            br.replace_with("\n")

        return body

    @staticmethod
    def get_text_from_bs4_parser(bs4_parser) -> str:
        return bs4_parser.get_text().strip()

    @staticmethod
    def get_added_dashed_delimiter(first_part, second_part):
        if "--" in second_part:
            if not second_part.replace("--", ""):
                return first_part

            return first_part + "\n" + second_part

        if not second_part:
            return first_part

        return first_part + "\n--\n" + second_part

    @staticmethod
    def get_replaced_new_lines_with_br_tags(text):
        return text.replace("\n", "<br/>")

    @staticmethod
    def calculate_joint_strings_length(sentences):
        return len(HTMLParser.get_replaced_new_lines_with_br_tags(" ".join(sentences)))
