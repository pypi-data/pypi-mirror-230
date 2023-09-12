import random
from uuid import uuid4

from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from templates.renderers.md.template_parser import MarkdownTemplateParser


class TestMarkdownTemplateParser:
    def test_simple_text_one_lang(self):
        base_format = """
        some cool test
        """

        parser = MarkdownTemplateParser({"en": base_format})

        res = parser.render("en")

        assert res is not None
        assert res.text is not None
        assert res.text.strip() == base_format.strip()

    def test_simple_text_two_lang(self):
        base_format_en = """
        some cool test
        """
        base_format_ru = """
        сроки жмут слышком
        """

        parser = MarkdownTemplateParser(
            {
                "en": base_format_en,
                "ru": base_format_ru,
            }
        )

        res = parser.render("en")

        assert res is not None
        assert res.text is not None

        assert res.text.strip() == base_format_en.strip()

        res = parser.render("ru")

        assert res is not None
        assert res.text is not None

        assert res.text.strip() == base_format_ru.strip()

    def test_simple_one_reply_keyboard(self):
        key_text = "only one reply key"
        base_format = f"""
        something cool to say1

        | !reply |
        | [{key_text}]() |
        """

        parser = MarkdownTemplateParser({"en": base_format})

        res = parser.render("en")

        assert type(res.keyboard) is ReplyKeyboardBuilder
        keys = list(res.keyboard.buttons)

        assert len(keys) == 1

        assert list(keys)[0].text == key_text

        assert res.keyboard is not None

    def test_row_reply_keyboard(self):
        key_text1 = str(random.randint(1, 9999999))
        key_text2 = str(random.randint(1, 9999999))

        base_format = f"""
        something cool to say1

        | !reply |
        | [{key_text1}]() | [{key_text2}]() |
        """

        parser = MarkdownTemplateParser({"en": base_format})

        res = parser.render("en")

        assert type(res.keyboard) is ReplyKeyboardBuilder
        keys = list(res.keyboard.buttons)

        assert len(keys) == 2

        assert list(keys)[0].text == key_text1
        assert list(keys)[1].text == key_text2

        assert res.keyboard is not None

    def test_mutli_row_column_keyboard(self):
        key_text1 = str(random.randint(1, 9999999))
        key_text2 = str(random.randint(1, 9999999))
        key_text3 = str(random.randint(1, 99999999))
        key_text4 = str(random.randint(1, 99999999))
        key_text5 = str(random.randint(1, 99999999))

        base_format = f"""
        something cool to say1

        | !reply |
        | [{key_text1}]() | [{key_text2}]() |
        | [{key_text3}]() | [{key_text4}]() |
        | [{key_text5}]() |
        """

        parser = MarkdownTemplateParser({"en": base_format})

        res = parser.render("en")

        assert type(res.keyboard) is ReplyKeyboardBuilder
        keys = list(res.keyboard.buttons)

        assert len(keys) == 5

        assert list(keys)[0].text == key_text1
        assert list(keys)[1].text == key_text2
        assert list(keys)[2].text == key_text3
        assert list(keys)[3].text == key_text4
        assert list(keys)[4].text == key_text5

        assert res.keyboard is not None

    def test_meta_type(self):
        base_format = """
        something cool to say1

        !meta:
            type: audio

        """

        parser = MarkdownTemplateParser({"en": base_format})

        res = parser.render("en")

        assert res.type_ == "audio"

    def test_data_content(self):
        file_id = str(uuid4())

        base_format = f"""
        something cool to say1

        !meta:
            data-content:
                file_id: {file_id}

        """

        parser = MarkdownTemplateParser({"en": base_format})

        res = parser.render("en")

        assert res.content_data is not None
        assert res.content_data.get("file_id") == file_id

    def test_full_template(self):
        file_id = str(uuid4())
        buttons_text = ""
        buttons = []

        for _ in range(random.randint(1, 8)):
            button_text_row = ""

            for __ in range(random.randint(1, 5)):
                text = str(uuid4())
                data = f"!{str(uuid4())}"

                buttons.append((text, data))
                button_text_row += f" [{text}]({data}) |"

            buttons_text += f"\n{button_text_row}"

        text = str(random.randint(1, 99999999999999))
        base_format = (
            text
            + "\n"
            + "\n | !inline |"
            + buttons_text
            + "\n"
            + f"""
            !meta:
                type: video
                data-content:
                    file_id: {file_id}

            """
        )

        parser = MarkdownTemplateParser(base_formats={"en": base_format})

        res = parser.render("en")

        assert res is not None

        assert res.text is not None
        assert res.text.strip() == text

        assert res.type_ == "video"

        assert type(res.keyboard) is InlineKeyboardBuilder
        keys = list(res.keyboard.buttons)

        assert len(keys) == len(buttons)

        for button, key in zip(buttons, keys):
            assert key.text == button[0]
            assert key.callback_data == button[1]
