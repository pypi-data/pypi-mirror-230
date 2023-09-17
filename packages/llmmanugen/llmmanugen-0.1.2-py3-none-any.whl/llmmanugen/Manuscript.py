"""
# Manuscript Class Documentation

## Overview

The `Manuscript` class represents a manuscript composed of multiple sections. It inherits from the `Section` class and provides additional functionalities specific to a manuscript.

## Attributes

- `subtitle` (str): The subtitle of the manuscript.
- `author`: The author of the manuscript.
- `additional_fields` (dict): Additional metadata or information.

## Methods

### `__init__`

Initializes a Manuscript object with a title, optional subtitle, and author.

#### Parameters

- `title` (str): The title of the manuscript.
- `*sections` (Section): Sections to include in the manuscript.
- `subtitle` (str, optional): The subtitle of the manuscript.
- `author` (optional): The author of the manuscript.
- `**kwargs`: Additional fields for extended information.

### `add_section`

Adds one Section object to the manuscript.

#### Parameters

- `section` (Section): Section object to add to the manuscript.

### `add_sections`

Adds one or more Section objects to the manuscript.

#### Parameters

- `*sections` (Section): Section object(s) to add to the manuscript.

### `get_current_section`

Returns the current section in the manuscript.

#### Returns

- `Section`: The current section object.

### `move_to_next_section_and_get_prompts`

Moves to the next section in the manuscript and returns relevant prompts and instructions.

#### Parameters

- `general_instructions` (bool): Whether to include general instructions in the result. Default is True.

#### Returns

- `dict`: A dictionary containing the current title, current prompt, next section details, and optionally general instructions.

### `move_to_next_section`

Moves to the next section in the manuscript and returns it.

#### Returns

- `Section`: The next section object.

### `move_to_prev_section`

Moves to the previous section in the manuscript and returns it.

#### Returns

- `Section`: The previous section object.

### `get_current_prompt`

Returns the prompt of the current section in the manuscript.

#### Returns

- `str`: The prompt of the current section.

### `get_current_content`

Returns the content of the current section in the manuscript.

#### Returns

- `str`: The content of the current section.

### `get_current_summary`

Returns the summary of the current section in the manuscript.

#### Returns

- `str`: The summary of the current section.

### `get_current_title`

Returns the title of the current section in the manuscript.

#### Returns

- `str`: The title of the current section.

### `get_current_completed`

Returns the completion status of the current section in the manuscript.

#### Returns

- `bool`: The completion status of the current section.

### `set_current_content`

Sets the content of the current section.

#### Parameters

- `content` (str): The new content to set for the current section.

### `set_current_title`

Sets the title of the current section.

#### Parameters

- `title` (str): The new title to set for the current section.

### `set_current_completed`

Sets the completion status of the current section.

#### Parameters

- `completed` (bool): The new completion status to set for the current section. Default is True.

### `set_current_prompt`

Sets the prompt of the current section.

#### Parameters

- `prompt` (str): The new prompt to set for the current section.

### `set_current_summary`

Sets the summary of the current section.

#### Parameters

- `summary` (str): The new summary to set for the current section.

### `__str__`

Returns a string representation of the Manuscript object, consisting of the title and optionally the subtitle.

#### Returns

- `str`: A string in the format "Title: Subtitle" if a subtitle exists, otherwise just "Title".

### `get_contents`

Generates and returns a comprehensive table of contents for the manuscript.

#### Returns

- `str`: A Markdown-formatted string representing the table of contents, including titles, subtitles, authors, and content.

### `__getattr__`

Custom attribute getter that first tries to get the attribute using the superclass's method. If not found, it looks in the `additional_fields` dictionary.

#### Parameters

- `name` (str): The name of the attribute to get.

#### Returns

- The value of the attribute, or None if the attribute is not found.

### `from_json`

Initializes a Manuscript object from a JSON-formatted string.

#### Parameters

- `json_str` (str): The JSON-formatted string representing the manuscript.

#### Returns

- A Manuscript object initialized with the data from the JSON string.

### `from_markdown`

Initializes a Manuscript object from a Markdown-formatted string.

#### Parameters

- `markdown_str` (str): The Markdown-formatted string representing the manuscript.
- `content_field` (str): The field in which to store the content. Default is "content".

#### Returns

- A Manuscript object initialized with the data from the Markdown string.

### `to_markdown`

Converts the Manuscript object to a Markdown-formatted string.

#### Parameters

- `content_field` (str): The field from which to retrieve the content. Default is "content".

#### Returns

- A Markdown-formatted string representing the Manuscript object.

### `to_json`

Converts the Manuscript object and its nested sections to a JSON-formatted string.

#### Returns

- `str`: A JSON-formatted string representing the Manuscript object and its nested sections.

## Usage Example

```python
# Create individual sections for the manuscript
intro = Section("Introduction", content="This is the introduction.")
body = Section("Body", content="This is the main content.")
conclusion = Section("Conclusion", content="This is the conclusion.")

# Create a manuscript with sections
manuscript = Manuscript(title="My Manuscript", subtitle="A Subtitle", author="John Doe", *(intro, body, conclusion))

# Add a new section to the manuscript
new_section = Section("New Section", content="This is a new section.")
manuscript.add_section(new_section)

# Navigate through sections
current_section = manuscript.get_current_section()
print(f"Current section: {current_section.title}")

# Move to the next section
next_section = manuscript.move_to_next_section()
print(f"Next section: {next_section.title}")

# Get content of the current section
print(f"Current content: {manuscript.get_current_content()}")

# Output the manuscript's title and subtitle
print(str(manuscript))

# Generate and print the full contents of the manuscript
print(manuscript.get_contents())

## Additional Usage Examples

### Setting Content and Title for Current Section

```python
# Set the content for the current section
manuscript.set_current_content("This is the updated content for the current section.")

# Set the title for the current section
manuscript.set_current_title("Updated Title for Current Section")

# Verify the changes
print(f"Updated content: {manuscript.get_current_content()}")
print(f"Updated title: {manuscript.get_current_title()}")
```

### Moving to Previous Section and Checking Completion Status

```python
# Move to the previous section
prev_section = manuscript.move_to_prev_section()
print(f"Previous section: {prev_section.title}")

# Check if the current section is completed
is_completed = manuscript.get_current_completed()
print(f"Is current section completed? {is_completed}")
```

### Setting and Getting Prompts

```python
# Set a prompt for the current section
manuscript.set_current_prompt("This is your new prompt for the current section.")

# Get the current prompt
current_prompt = manuscript.get_current_prompt()
print(f"Current prompt: {current_prompt}")
```

### Exporting Manuscript to JSON and Markdown

```python
# Export the manuscript to a JSON-formatted string
json_output = manuscript.to_json()
print(f"JSON Output: {json_output}")

# Export the manuscript to a Markdown-formatted string
markdown_output = manuscript.to_markdown()
print(f"Markdown Output: {markdown_output}")
```

### Importing Manuscript from JSON and Markdown

```python
# Initialize a Manuscript object from a JSON-formatted string
new_manuscript_from_json = Manuscript().from_json(json_output)

# Initialize a Manuscript object from a Markdown-formatted string
new_manuscript_from_md = Manuscript().from_markdown(markdown_output)
```

These examples demonstrate the various functionalities provided by the `Manuscript` class for creating, navigating, and manipulating manuscripts.
"""

import json
from datetime import datetime
from .Section import Section
from .lib import parse_markdown_to_manuscript, parse_dictionary_to_manuscript


class Manuscript(Section):
    """
    Represents a manuscript composed of multiple sections. Inherits from the Section class.

    Attributes:
        subtitle (str): The subtitle of the manuscript.
        author: The author of the manuscript.
        additional_fields (dict): Additional metadata or information.

    Usage:
        # Create individual sections for the manuscript
        intro = Section("Introduction", content="This is the introduction.")
        body = Section("Body", content="This is the main content.")
        conclusion = Section("Conclusion", content="This is the conclusion.")

        # Create a manuscript with sections
        manuscript = Manuscript(title="My Manuscript", subtitle="A Subtitle", author="John Doe", *(intro, body, conclusion))

        # Add a new section to the manuscript
        new_section = Section("New Section", content="This is a new section.")
        manuscript.add_section(new_section)

        # Navigate through sections
        current_section = manuscript.get_current_section()
        print(f"Current section: {current_section.title}")

        # Move to the next section
        next_section = manuscript.move_to_next_section()
        print(f"Next section: {next_section.title}")

        # Get content of the current section
        print(f"Current content: {manuscript.get_current_content()}")

        # Output the manuscript's title and subtitle
        print(str(manuscript))

        # Generate and print the full contents of the manuscript
        print(manuscript.get_contents())
    """
    def __init__(self, *sections, **kwargs):
        """
        Initialize a Manuscript instance with optional sections and additional keyword arguments.

        Parameters:
            - *sections: Zero or more section objects to initialize the Manuscript with.
            - **kwargs: Additional keyword arguments to set as attributes. 'title' can be set here.
                title (str): The title of the manuscript.
                subtitle (str, optional): The subtitle of the manuscript.
                author (optional): The author of the manuscript.

        Returns:
            None: This method initializes the instance and does not return a value.
        """
        super().__init__(kwargs.get("title", "Untitled"), *sections)
        self._init(**kwargs)

    def _init(self, **kwargs):
        """
        Initialize additional fields for the Manuscript instance.

        Parameters:
            - **kwargs: Additional keyword arguments to set as attributes.

        Returns:
            None: This method initializes additional fields and does not return a value.
        """
        self.additional_fields = kwargs

    def add_section(self, section=None, **kwargs):
        """Adds one Section/dictionary object to the manuscript.

        Note: dictionary object is transformed to Section type.

        Parameters:
            section (Section|dict): Section/dictionary object to add to the manuscript.
        """
        if kwargs and not section:
            section = Section(**kwargs)
        if isinstance(section, Section):
            self.add_subnode(section)
        else:
            raise TypeError("Section must be type of Section")

    def add_sections(self, *sections):
        """Adds one or more Section/dictionary objects to the manuscript.

        Note: Dictionaries are transformed to Section type.

        Parameters:
            *sections (Section|dict): Section/dictionary object(s) to add to the manuscript.
        """
        self.add_subnodes(*(section if isinstance(section, Section) else Section(**section) for section in sections))

    def get_current_section(self):
        """Returns the current section in the manuscript.

        Returns:
            Section: The current section object.
        """
        return self.current_node

    def update_current_section(self, **kwargs):
        """
        Update the attributes of the current section with the given keyword arguments.

        Parameters:
            - **kwargs: Keyword arguments representing the attributes to update and their new values.

        Returns:
            None: This method updates the current section in place and does not return a value.
        """
        self.get_current_section().update(**kwargs)

    def move_to_next_section_and_get_prompts(self, general_instructions=True):
        """
        Moves to the next section in the manuscript and returns relevant prompts and instructions.

        Parameters:
        - general_instructions (bool): Whether to include general instructions in the result. Default is True.

        Returns:
        dict: A dictionary containing the following keys:
            - 'current': A dictionary containing the title and prompt of the current section.
            - 'next': A dictionary containing the title and prompt of the next section, or None if there is no next section.
            - 'general_instructions': (Optional) A dictionary containing general guidelines and constraints, included if general_instructions is True.

        Example:
        {
            'current': {
                'title': 'Introduction',
                'prompt': 'Write an introduction here.'
            },
            'next': {
                'title': 'Background',
                'prompt': 'Provide some background.'
            },
            'general_instructions': {
                'guidelines': 'Keep it concise.',
                'constraints': 'Max 300 words'
            }
        }
        """
        self.move_to_next_section()
        result = {
            'current': {
                "title": self.get_current_title(),
                'prompt': self.get_current_prompt()
            },
            'next': (lambda x: {"title": x.title, "prompt": x.prompt} if x else None)(self.peak_next())
        }
        if general_instructions:
            result["general_instructions"] = {
                "guidelines": self.guidelines,
                "constraints": self.constraints
            }
        return result

    def set_and_get_current_section_by_index(self, index):
        """
        Set the current section based on the given index and return it.

        Parameters:
            - index (int): The index of the section to set as the current section.

        Returns:
            object: The section object that has been set as the current section.
        """
        return self.set_current_node_by_index(index)

    def move_to_next_section(self):
        """Moves to the next section in the manuscript and returns it.

        Returns:
            Section: The next section object.
        """
        return self.next()

    def move_to_prev_section(self):
        """Moves to the previous section in the manuscript and returns it.

        Returns:
            Section: The previous section object.
        """
        return self.prev()

    def get_current_prompt(self):
        """Returns the prompt of the current section in the manuscript.

        Returns:
            str: The prompt of the current section.
        """
        return self.get_current_section().prompt

    def get_current_content(self):
        """Returns the content of the current section in the manuscript.

        Returns:
            str: The content of the current section.
        """
        return self.get_current_section().content

    def get_current_summary(self):
        """Returns the summary of the current section in the manuscript.

        Returns:
            str: The summary of the current section.
        """
        return self.get_current_section().summary

    def get_current_title(self):
        """Returns the title of the current section in the manuscript.

        Returns:
            str: The title of the current section.
        """
        return self.get_current_section().title

    def get_current_completed(self):
        """Returns the title of the current section in the manuscript.

        Returns:
            str: The title of the current section.
        """
        return self.get_current_section().completed

    def set_current_content(self, content):
        """
        Sets the content of the current section.

        Parameters:
        - content (str): The new content to set for the current section.
        """
        self.get_current_section().content = content

    def set_current_title(self, title):
        """
        Sets the title of the current section.

        Parameters:
        - title (str): The new title to set for the current section.
        """
        self.get_current_section().title = title

    def set_current_completed(self, completed=True):
        """
        Sets the completion status of the current section.

        Parameters:
        - completed (bool): The new completion status to set for the current section. Default is True.
        """
        self.get_current_section().completed = completed

    def set_current_prompt(self, prompt):
        """
        Sets the prompt of the current section.

        Parameters:
        - prompt (str): The new prompt to set for the current section.
        """
        self.get_current_section().prompt = prompt

    def set_current_summary(self, summary):
        """
        Sets the summary of the current section.

        Parameters:
        - summary (str): The new summary to set for the current section.
        """
        self.get_current_section().summary = summary

    def get_headings(self, tree_structure=True):
        """
        Generates a string representation of the manuscript's table of contents, including section and subsection titles.

        Parameters:
            tree_structure (bool): Whether to display the table of contents as a tree structure. Default is True.

        Returns:
            str: A string representing the table of contents. Each line corresponds to a section or subsection title.
                The titles are indented to indicate their level in the manuscript. The current section is marked with an asterisk (*).

        Example:
            My Manuscript
            ├── Introduction*
            ├── Chapter 1
            │   ├── Section 1.1
            │   └── Section 1.2
            └── Conclusion
        """
        toc = [self.title]
        current_section = self.get_current_section()
        current_title = current_section.title if current_section else "Untitled"
        current_section = self.get_current_section()

        def _(sections, level, prefix=''):
            for i, section in enumerate(sections):
                is_last = i == len(sections) - 1
                spacer, new_prefix = '', ''
                if tree_structure:
                    new_prefix, spacer = ('└── ', '    ') if is_last else ('├── ', '│   ')
                else:
                    prefix = '  ' * level
                toc.append(f"{prefix}{new_prefix}{section.title}{'*' if section.title == current_title else ''}")
                if section.has_subnodes():
                    _(section.subnodes, level + 1, prefix + spacer)
        _(self.subnodes, 1, '' if tree_structure else '  ')
        return '\n'.join(toc)

    def __str__(self):
        """Returns a string representation of the Manuscript object, consisting of the title and optionally the subtitle.

        This method overrides the built-in __str__ method to provide a custom string representation of the Manuscript object.
        If a subtitle is present, it will be included in the format "Title: Subtitle". Otherwise, only the title will be returned.

        Returns:
            str: A string in the format "Title: Subtitle" if a subtitle exists, otherwise just "Title".
        """
        return f'{self.title}: {self.subtitle}' if self.subtitle else self.title

    def get_contents(self, content_field="content"):
        """Generates and returns a comprehensive table of contents for the manuscript.

        This method performs a depth-first traversal of the manuscript and its sections, generating a Markdown-formatted string
        that includes the titles, subtitles, authors, and content of all nested sections. The table of contents is indented
        according to the depth of the section within the manuscript structure.

        Returns:
            str: A Markdown-formatted string representing the table of contents, including titles, subtitles, authors, and content.

        Example:
            # My Manuscript: Sub title
            by: John Doe

            ## Introduction
            This is the introduction content.

            ## Chapter 1: The Beginning
            ### Section 1.1: The Very Start
            This is the content for Section 1.1.

            ### Section 1.2: Another Start
            This is the content for Section 1.2.

            ## Chapter 2: The Middle
            This is the content for Chapter 2.

            ### Section 2.1: The Real Middle
            This is the content for Section 2.1.

            ## Conclusion
            This is the conclusion content.
        """
        contents = []

        def traverse(node, indent=0):
            if indent:
                contents.append("")
            title = (node.title+": "+node.subtitle) if hasattr(node, 'subtitle') and node.subtitle else node.title
            contents.append(f'{"#"*indent}{" " if indent else ""}{title}')
            if hasattr(node, 'author') and node.author:
                contents.append("by: %s" % str(node.author))
            content = getattr(node, content_field) if hasattr(node, content_field) else ""
            if content:
                contents.append("")
                contents.append(content)
            for subnode in node.subnodes:
                traverse(subnode, indent+1)
        traverse(self)
        return '\n'.join(contents)

    def __getattr__(self, name):
        """
        Custom attribute getter that first tries to get the attribute using the superclass's method.
        If not found, it looks in the additional_fields dictionary.

        Parameters:
            - name (str): The name of the attribute to get.

        Returns:
            The value of the attribute, or None if the attribute is not found.
        """
        try:
            return super().__getattr__(name)
        except AttributeError:
            return self.additional_fields.get(name, None)

    @classmethod
    def from_dictionary(cls, data_dict):
        """
        Convert a dictionary to a Manuscript object.

        Parameters:
            - cls (type): The class on which this method is called. Automatically passed by Python.
            - data_dict (dict): Dictionary containing manuscript data.

        Returns:
            - Manuscript: Manuscript object initialized with the data from the dictionary.
        """
        return parse_dictionary_to_manuscript(cls() if cls == Manuscript else cls, data_dict)

    @classmethod
    def from_json(cls, json_str):
        """
        Initializes a Manuscript object from a JSON-formatted string.

        Parameters:
            - cls (type): The class on which this method is called. Automatically passed by Python.
            - json_str (str): The JSON-formatted string representing the manuscript.

        Returns:
            A Manuscript object initialized with the data from the JSON string.
        """
        return parse_dictionary_to_manuscript(cls() if cls == Manuscript else cls, json.loads(json_str))

    @classmethod
    def from_markdown(cls, markdown_str, content_field="content"):
        """
        Initializes a Manuscript object from a Markdown-formatted string.

        Parameters:
            - cls (type): The class on which this method is called. Automatically passed by Python.
            - markdown_str (str): The Markdown-formatted string representing the manuscript.
            - content_field (str): The field in which to store the content. Default is "content".

        Returns:
            A Manuscript object initialized with the data from the Markdown string.
        """
        return parse_markdown_to_manuscript(cls() if cls == Manuscript else cls, markdown_str, content_field)

    def to_markdown(self, content_field="content"):
        """
        Converts the Manuscript object to a Markdown-formatted string.

        Parameters:
            - content_field (str): The field from which to retrieve the content. Default is "content".

        Returns:
            A Markdown-formatted string representing the Manuscript object.
        """
        return self.get_contents(content_field)

    def to_json(self):
        """
        Converts the Manuscript object and its nested sections to a JSON-formatted string.

        Returns:
            str: A JSON-formatted string representing the Manuscript object and its nested sections.
        """
        return json.dumps(self.to_dictionary(), indent=4)

    def to_dictionary(self):
        """
        Converts the Manuscript object and its nested sections to a dictionary.

        The method traverses the tree-like structure of the Manuscript object, converting each node and its subnodes to dictionaries.

        Returns:
            dict: The Manuscript object and its nested sections as a single dictionary.

        Example Output:
        {
            "title": "Sample Manuscript",
            "subtitle": "An example",
            "author": "John Doe",
            "created": "2023-09-16 12:34:56",
            "updated": "2023-09-16 12:34:56",
            "guidelines": {},
            "constraints": {},
            "sections": [
                {
                    "title": "Introduction",
                    "summary": "Summary of the introduction",
                    "content": "This is the introduction.",
                    "prompt": {},
                    ...
                },
                ...
            ]
        }
        """
        def traverse(node):
            created = node.created if node.created else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated = node.updated if node.updated else created
            node_dict = {
                'title': node.title,
                'summary': node.summary,
                'content': node.content,
                'prompt': node.prompt,
                'completed': node.completed,
                'created': created,
                'updated': updated,
                'sections': [traverse(subnode) for subnode in node.subnodes]
            }
            return node_dict
        created = self.created or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {
            'title': self.title,
            'subtitle': self.subtitle,
            'author': self.author,
            'created': created,
            'updated': self.updated or created,
            'guidelines': self.guidelines or {},
            'constraints': self.constraints or {},
            'sections': [traverse(section) for section in self.subnodes]
        }
