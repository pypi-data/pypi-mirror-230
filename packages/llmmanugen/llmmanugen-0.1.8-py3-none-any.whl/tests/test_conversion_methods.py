import unittest
import json
from llmmanugen import Manuscript, Section


class TestManuscriptConversionMethods(unittest.TestCase):

    def test_from_and_to_dictionary(self):

        manuscript_dict = {
            "title": "My Manuscript",
            "subtitle": "A Subtitle",
            "author": "John Doe",
            "sections": [
                {"title": "Introduction", "content": "Intro content"},
                {"title": "Conclusion", "content": "Conclusion content"}
            ]
        }

        manuscript1 = Manuscript.from_dictionary(manuscript_dict)
        manuscript2 = Manuscript().from_dictionary(manuscript_dict)

        self.assertTrue(manuscript1.to_dictionary() == manuscript2.to_dictionary())
        self.assertTrue(manuscript1.title == "My Manuscript")
        self.assertTrue(manuscript1.title == manuscript2.title)
        self.assertTrue(manuscript1.author == "John Doe")
        self.assertTrue(manuscript1.author == manuscript2.author)

    def test_from_json(self):
        json_str = json.dumps({
            "title": "My Manuscript",
            "subtitle": "A Subtitle",
            "author": "John Doe",
            "sections": [
                {"title": "Introduction", "content": "Intro content"},
                {"title": "Conclusion", "content": "Conclusion content"}
            ]
        })

        manuscript = Manuscript().from_json(json_str)
        self.assertTrue(Manuscript.from_json(json_str).to_dictionary() == manuscript.to_dictionary())
        self.assertEqual(manuscript.title, "My Manuscript")
        self.assertEqual(manuscript.subtitle, "A Subtitle")
        self.assertEqual(manuscript.author, "John Doe")
        self.assertEqual(len(manuscript.subnodes), 2)
        self.assertEqual(len(Manuscript.from_json(json_str).subnodes), 2)

    def test_to_json(self):
        manuscript = Manuscript(title="My Manuscript", subtitle="A Subtitle", author="John Doe")
        section1 = Section("Introduction", content="Intro content")
        section2 = Section("Conclusion", content="Conclusion content")
        manuscript.add_subnode(section1)
        manuscript.add_subnode(section2)

        json_str = manuscript.to_json()

        # Assuming to_json is implemented correctly
        self.assertIsInstance(json_str, str)
        parsed_json = json.loads(json_str)
        self.assertEqual(parsed_json['title'], "My Manuscript")
        self.assertEqual(parsed_json['subtitle'], "A Subtitle")
        self.assertEqual(parsed_json['author'], "John Doe")
        self.assertEqual(len(parsed_json['sections']), 2)

    def test_from_markdown(self):
        markdown_str = "# My Manuscript\n## Introduction\nIntro Content\n## Conclusion\nConclusion Content"
        manuscript = Manuscript().from_markdown(markdown_str)
        manuscript2 = Manuscript.from_markdown(markdown_str)
        self.assertEqual(manuscript.title, "My Manuscript")
        self.assertEqual(len(manuscript.subnodes), 2)
        self.assertEqual(manuscript2.title, "My Manuscript")
        self.assertEqual(len(manuscript2.subnodes), 2)

    def test_to_markdown(self):
        manuscript = Manuscript(title="My Manuscript")
        section1 = Section("Introduction", content="Intro content")
        section2 = Section("Conclusion", content="Conclusion content")
        manuscript.add_subnode(section1)
        manuscript.add_subnode(section2)

        markdown_str = manuscript.to_markdown()

        # Assuming to_markdown is implemented correctly
        self.assertIsInstance(markdown_str, str)
        self.assertTrue("My Manuscript" in markdown_str)
        self.assertTrue("# Introduction" in markdown_str)
        self.assertTrue("# Conclusion" in markdown_str)
