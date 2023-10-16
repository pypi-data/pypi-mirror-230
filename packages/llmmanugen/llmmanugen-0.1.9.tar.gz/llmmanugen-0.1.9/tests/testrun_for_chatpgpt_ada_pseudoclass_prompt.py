# Manuscript Class Extended Features
# September 12, 2023
# https://chat.openai.com/share/821f229c-26b4-44c8-9b29-8f932a807404

# Importing required libraries
import json
import os
import re
from datetime import datetime


class Manuscript:

    def __init__(self, data, title_field="title", children_field="sections"):
        self.title_field = title_field
        self.children_field = children_field
        self.data = data
        if self.children_field not in self.data:
            self.data[self.children_field] = []
        self.validate_schema(self.data)
        self.reset_current_section_path()

    def validate_schema(self, schema):
        def _vs(s):
            if not isinstance(s, dict):
                return False
            if self.title_field not in s or not s[self.title_field]:
                return False
            if self.children_field in s:
                if not isinstance(s[self.children_field], list):
                    return False
                for child in s[self.children_field]:
                    if not _vs(child):
                        return False
            return True

        if not _vs(schema):
            raise ValueError("Invalid schema.")
        return True

    def reset_current_section_path(self, path_indices=None):
        self.current_path = path_indices or [0]

    def get_section(self, path_indices):
        section = self.data[self.children_field]
        for index in path_indices:
            try:
                if self.children_field in section:
                    section = section[self.children_field]
                section = section[index]
            except (IndexError, KeyError):
                return None
        return section

    def get_current_section(self):
        return self.get_section(self.current_path)

    def get_current_and_next_sections(self, without_children=True):
        cur_section = self.get_current_section()
        temp_path = self.current_path.copy()
        next_section = None
        if self.move_to_next_section() == "continue":
            next_section = self.get_current_section()
        self.current_path = temp_path
        if without_children:
            if cur_section and self.children_field in cur_section:
                cur_section = {k: v for k, v in cur_section.items() if k != self.children_field}
            if next_section and self.children_field in next_section:
                next_section = {k: v for k, v in next_section.items() if k != self.children_field}
        return cur_section, next_section

    def move_to_next_section(self):
        section = self.data[self.children_field]
        path = self.current_path.copy()
        for index in path[:-1]:
            section = section[index][self.children_field]
        if self.children_field in section[path[-1]] and section[path[-1]][self.children_field]:
            self.current_path.append(0)
            return "continue"
        if len(section) > path[-1] + 1:
            self.current_path[-1] += 1
            return "continue"
        else:
            while len(self.current_path) > 1:
                self.current_path.pop()
                sections = self.data[self.children_field]
                for index in self.current_path[:-1]:
                    sections = sections[index][self.children_field]
                if len(sections) > self.current_path[-1] + 1:
                    self.current_path[-1] += 1
                    return "continue"
            else:
                return "end"
        return "continue"

    def add_current_content(self, content):
        cur_section = self.get_current_section()
        if cur_section:
            for k, v in content.items():
                if k != self.children_field:
                    cur_section[k] = v

    @staticmethod
    def from_json(file_path):
        with open(file_path, 'r') as f:
            return Manuscript(json.load(f))

    def to_json(self, directory=None):
        self.validate_schema(self.data)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        filename = self.get_safe_filename('.json')
        filepath = os.path.join(directory, filename) if directory else filename
        with open(filepath, 'w') as f:
            json.dump(self.data, f)
        return filename, json.dumps(self.data)

    def get_safe_filename(self, extension):
        title = self.data.get(self.title_field, "Untitled") + "_" + datetime.now().strftime("%Y%m%d%H%M%S")
        safe_title = ''.join(e for e in title if e.isalnum() or e == ' ').replace(' ', '_')
        return safe_title + extension

    def get_table_of_contents(self, tree_structure=True):
        toc = []
        cur_section = self.get_current_section()
        cur_title = cur_section[self.title_field] if cur_section else None

        def _toc(sections, level, prefix=''):
            for i, section in enumerate(sections):
                is_last = i == len(sections) - 1
                if tree_structure:
                    new_prefix = "└── " if is_last else "├── "
                    spacer = "    " if is_last else "│   "
                else:
                    new_prefix = ""
                    spacer = "  " * (level - 1)
                mark = "*" if section[self.title_field] == cur_title else ""
                toc.append(f"{prefix}{new_prefix}{section[self.title_field]} {mark}")
                if self.children_field in section:
                    _toc(section[self.children_field], level + 1, prefix + spacer)

        _toc(self.data[self.children_field], level=1)
        return '\n'.join(toc)


# Extending the Manuscript class with markdown exporter and search utilities
class Manuscript(Manuscript):

    def to_md(self, content_field=None, directory=None):

        md = []

        def _md(subsection, level):
            for section in subsection:
                md.append("#" * level + " " + section[self.title_field])
                if content_field:
                    content = section.get(content_field, f"Section content not present for the field: {content_field}")
                    md.append(f"\n{content}\n")
                if self.children_field in section:
                    _md(section[self.children_field], level + 1)

        _md(self.data[self.children_field], level=1)
        markdown_string = '\n'.join(md)
        filename = self.get_safe_filename('.md')
        filepath = os.path.join(directory, filename) if directory else filename
        with open(filepath, 'w') as f:
            f.write(markdown_string)
        return filename, markdown_string

    def search(self, query, field=None, path=None):

        search_field = field or self.title_field
        results = []

        def _search(sections, new_path=[]):
            for i, section in enumerate(sections):
                local_path = new_path + [i]
                match_condition = (
                    search_field in section and
                    ((isinstance(query, str) and query.lower() in section[search_field].lower()) or
                     (isinstance(query, re.Pattern) and query.search(section[search_field])))
                )
                if match_condition and (path is None or path == local_path[:len(path)]):
                    results.append({self.children_field: section, 'path': local_path})
                if self.children_field in section:
                    _search(section[self.children_field], local_path)

        _search(self.data[self.children_field])
        return results

    def find_path_indices(self, field_values):

        def _find(subsections, remaining_fields, new_path=[]):

            for i, section in enumerate(subsections):
                if section[self.title_field] == remaining_fields[0]:
                    local_path = new_path + [i]
                    if len(remaining_fields) == 1:
                        return local_path
                    if self.children_field in section:
                        return _find(section[self.children_field], remaining_fields[1:], local_path)

        return _find(self.data[self.children_field], field_values)


# Testing the Manuscript class and its methods
test_data = {
    "title": "Test Manuscript",
    "sections": [
        {"title": "Introduction"},
        {"title": "Chapter 1", "sections": [
            {"title": "Section 1.1"},
            {"title": "Section 1.2"},
        ]},
        {"title": "Chapter 2", "sections": [
            {"title": "Section 2.1"},
            {"title": "Section 2.2"},
        ]},
        {"title": "Conclusion"}
    ]
}

# Initialize Manuscript class
m = Manuscript(test_data)

# Test: validate_schema
assert m.validate_schema(test_data) is True

# Test: reset_current_section_path and get_current_section
m.reset_current_section_path([1, 0])
assert m.get_current_section()['title'] == "Section 1.1"

# Test: move_to_next_section
assert m.move_to_next_section() == "continue"
assert m.get_current_section()['title'] == "Section 1.2"
assert m.move_to_next_section() == "continue"
assert m.get_current_section()['title'] == "Chapter 2"

# Test: get_current_and_next_sections
m.reset_current_section_path([0])
current, next_section = m.get_current_and_next_sections()
assert current['title'] == "Introduction"
assert next_section['title'] == "Chapter 1"

# Test: add_current_content
m.add_current_content({"summary": "This is the introduction"})
assert m.get_current_section()['summary'] == "This is the introduction"

# Test: to_json
filename, json_str = m.to_json()
assert filename.endswith('.json')
assert '"summary": "This is the introduction"' in json_str

# Test: get_table_of_contents
toc = m.get_table_of_contents()
assert "Introduction *" in toc
assert "Chapter 1" in toc

# Test: to_md (Markdown export)
filename, md_str = m.to_md(content_field="summary")
assert filename.endswith('.md')
assert "# Introduction" in md_str
assert "This is the introduction" in md_str

# Test: search
search_results = m.search("Chapter")
assert len(search_results) == 2
assert search_results[0][m.children_field]['title'] == "Chapter 1"

# Test: find_path_indices
path_indices = m.find_path_indices(["Chapter 2", "Section 2.1"])
assert path_indices == [2, 0]

print("Tests passed.")
