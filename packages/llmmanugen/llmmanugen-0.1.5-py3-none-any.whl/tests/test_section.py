import unittest
from datetime import datetime
from llmmanugen import Section


class TestSection(unittest.TestCase):

    def setUp(self):
        self.section = Section("Introduction", summary="A brief intro", content="Welcome to the guide.", prompt="Read more", extra_item="foo")

    def test_init(self):
        self.assertEqual(self.section._title, "Introduction")
        self.assertEqual(self.section._summary, "A brief intro")
        self.assertEqual(self.section._content, "Welcome to the guide.")
        self.assertEqual(self.section._prompt, "Read more")

        created_format = datetime.strptime(self.section._created, '%Y-%m-%d %H:%M:%S')
        self.assertIsInstance(created_format, datetime)

        updated_format = datetime.strptime(self.section._updated, '%Y-%m-%d %H:%M:%S')
        self.assertIsInstance(updated_format, datetime)

    def test_extra_item_property(self):
        self.assertEqual(self.section._additional_fields.get("extra_item"), "foo")
        self.assertEqual(self.section["extra_item"], "foo")
        self.section["extra_item"] = "bar"
        self.assertEqual(self.section["extra_item"], "bar")

    def test_title_property(self):
        self.section.title = "New Intro"
        self.assertEqual(self.section.title, "New Intro")
        self.assertEqual(self.section._title, "New Intro")
        updated_format = datetime.strptime(self.section._updated, '%Y-%m-%d %H:%M:%S')
        self.assertIsInstance(updated_format, datetime)

    def test_title_empty_value(self):
        with self.assertRaises(ValueError):
            self.section.title = None

    def test_update_method(self):
        self.section.update(title="Updated Intro", summary="Updated Summary", content="Updated Content", prompt="Updated Prompt")

        self.assertEqual(self.section._title, "Updated Intro")
        self.assertEqual(self.section._summary, "Updated Summary")
        self.assertEqual(self.section._content, "Updated Content")
        self.assertEqual(self.section._prompt, "Updated Prompt")

        updated_format = datetime.strptime(self.section._updated, '%Y-%m-%d %H:%M:%S')
        self.assertIsInstance(updated_format, datetime)

    def test_summary_property(self):
        self.section.summary = "Updated Summary"
        self.assertEqual(self.section._summary, "Updated Summary")
        updated_format = datetime.strptime(self.section._updated, '%Y-%m-%d %H:%M:%S')
        self.assertIsInstance(updated_format, datetime)

    def test_content_property(self):
        self.section.content = "Updated Content"
        self.assertEqual(self.section._content, "Updated Content")
        updated_format = datetime.strptime(self.section._updated, '%Y-%m-%d %H:%M:%S')
        self.assertIsInstance(updated_format, datetime)

    def test_prompt_property(self):
        self.section.prompt = "Updated Prompt"
        self.assertEqual(self.section._prompt, "Updated Prompt")
        updated_format = datetime.strptime(self.section._updated, '%Y-%m-%d %H:%M:%S')
        self.assertIsInstance(updated_format, datetime)

    def test_getitem_method(self):
        self.assertEqual(self.section['title'], "Introduction")
        self.assertEqual(self.section['summary'], "A brief intro")
        self.assertEqual(self.section['nonexistent'], None)

    def test_setitem_method(self):
        self.section['title'] = "Set via item"
        self.assertEqual(self.section._title, "Set via item")
        updated_format = datetime.strptime(self.section._updated, '%Y-%m-%d %H:%M:%S')
        self.assertIsInstance(updated_format, datetime)

    def test_count_content_words_and_letters_method(self):
        section = Section("Introduction", content="Set content to the introduction.")
        section.add_subnode(Section("Background", content="Content for the background."))
        self.assertEqual(section.count_content_words_and_letters(), (5, 32))
        self.assertEqual(section.count_content_words_and_letters(include_all_subsections=True), (9, 59))

    def test_subsection_types(self):
        subsection1 = {"title": "Sub1", "sections": [{"title": "Sub1.1", "sections": []}]}
        subsection2 = Section("Sub2", {"title": "Sub2.1"})
        mainsection = Section("Main", subsection1, subsection2)

        self.assertTrue(all(type(node) is Section for node in mainsection.subnodes))
        self.assertTrue(all(type(node) is Section for node in subsection2.subnodes))
        self.assertTrue(all(type(node) is Section for node in mainsection.subnodes[0].subnodes))
