import unittest
from llmmanugen import Manuscript, Section


class TestManuscript(unittest.TestCase):

    def setUp(self):
        self.manuscript = Manuscript(title="My Manuscript", subtitle="An Adventure", author="John Doe")
        self.section1 = Section("Introduction", summary="Intro", content="Welcome", prompt="Read More")
        self.section2 = Section("Body", summary="Main Part", content="Content Here", prompt="Continue")
        self.manuscript.add_sections(self.section1, self.section2)

    def test_init(self):
        self.assertEqual(self.manuscript.title, "My Manuscript")
        self.assertEqual(self.manuscript.subtitle, "An Adventure")
        self.assertEqual(self.manuscript.author, "John Doe")
        self.assertIsInstance(self.manuscript.fields, dict)

    def test_add_section(self):
        new_section = Section("Conclusion", summary="End", content="Goodbye", prompt="The End")
        self.manuscript.add_sections(new_section)
        self.assertIn(new_section, self.manuscript.subnodes)

    def test_move_to_next_section(self):
        next_section = self.manuscript.move_to_next_section()
        self.assertEqual(next_section, self.manuscript)
        next_section = self.manuscript.move_to_next_section()
        self.assertEqual(next_section, self.section1)

    def test_move_to_prev_section(self):
        self.manuscript.next()
        self.manuscript.next()
        prev_section = self.manuscript.move_to_prev_section()
        self.assertEqual(prev_section, self.manuscript)

    def test_get_current_prompt(self):
        self.manuscript.next()
        self.manuscript.next()
        current_prompt = self.manuscript.get_current_prompt()
        self.assertEqual(current_prompt, "Read More")

    def test_get_current_content(self):
        self.manuscript.next()
        self.manuscript.next()
        current_content = self.manuscript.get_current_content()
        self.assertEqual(current_content, "Welcome")

    def test_get_current_summary(self):
        self.manuscript.next()
        self.manuscript.next()
        current_summary = self.manuscript.get_current_summary()
        self.assertEqual(current_summary, "Intro")

    def test_get_current_title(self):
        self.manuscript.next()
        self.manuscript.next()
        current_title = self.manuscript.get_current_title()
        self.assertEqual(current_title, "Introduction")

    def test_str_method(self):
        self.assertEqual(str(self.manuscript), "My Manuscript: An Adventure")
        self.manuscript.subtitle = None
        self.assertEqual(str(self.manuscript), "My Manuscript")

    def test_get_contents(self):
        contents = self.manuscript.get_contents()
        expected_contents = """My Manuscript: An Adventure
by: John Doe

# Introduction

Welcome

# Body

Content Here"""
        self.assertEqual(contents, expected_contents)

    def test_headings(self):
        self.manuscript.add_section(Section("Chapter 1", Section("Chapter 1.1", Section("Chapter 1.1.1"), Section("Chapter 1.1.2"))))
        self.manuscript.add_section(Section("Chapter 2"))
        # Manuscript root -> First section
        self.manuscript.move_to_next_section().move_to_next_section()
        headings = self.manuscript.get_headings()
        self.assertTrue("├── Introduction" in headings)
        self.assertTrue("├── Body" in headings)
        self.assertTrue("└── Chapter 1" in headings)
        self.assertTrue("│   └── Chapter 1.1" in headings)
        self.assertTrue("└── Chapter 2" in headings)
