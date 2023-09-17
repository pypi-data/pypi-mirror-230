import json
import re
from datetime import datetime

def parse_json_to_manuscript(json_str):
    """
    Parses a JSON-formatted string to create a Manuscript object with nested Section objects.

    The function deserializes the JSON string to a Python dictionary and then recursively constructs
    Section objects for each section and its sub-sections. These Section objects are added to a Manuscript object.

    Parameters:
    - json_str (str): The JSON-formatted string representing the manuscript and its sections.

    Returns:
    Manuscript: A Manuscript object initialized with the data from the JSON string.

    Example JSON Input:
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
                ...
            },
            ...
        ]
    }
    """
    from .Manuscript import Manuscript
    from .Section import Section
    
    json_data = json.loads(json_str)

    def parse_node(node_data):
        
        title = node_data.get('title', '')
        summary = node_data.get('summary', '')
        content = node_data.get('content', '')
        prompt = node_data.get('prompt', {})
        completed = node_data.get('completed', False)
        created = node_data.get('created', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        updated = node_data.get('updated', created)
        
        node = Section(title, summary=summary, content=content, prompt=prompt, completed=completed, created=created, updated=updated)

        subnodes_data = node_data.get('sections', [])
        for subnode_data in subnodes_data:
            subnode = parse_node(subnode_data)
            node.add_subnode(subnode)

        return node

    manuscript_data = json_data.get('manuscript', {})
    
    title = json_data.get('title', '')
    subtitle = json_data.get('subtitle', '')
    author = json_data.get('author', '')
    
    created = json_data.get('created', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    additional_arguments = {
        "created": created,
        "updated": json_data.get('updated', created),
        "guidelines": json_data.get('guidelines', {}),
        "constraints": json_data.get('constraints', {})
    }

    manuscript = Manuscript(title=title, subtitle=subtitle, author=author, **additional_arguments)

    sections_data = json_data.get('sections', [])
    for section_data in sections_data:
        section = parse_node(section_data)
        manuscript.add_subnode(section)

    return manuscript

def parse_markdown_to_manuscript(md_text, content_field="content"):
    """
    Parses a Markdown-formatted text to create a Manuscript object with nested Section objects.

    The function reads the Markdown text line by line, identifying section titles based on the number of '#' characters.
    It then recursively constructs Section objects for each section and its sub-sections, adding them to a Manuscript object.

    Parameters:
    - md_text (str): The Markdown-formatted text representing the manuscript and its sections.
    - content_field (str): The field in which to store the content. Default is "content".

    Returns:
    Manuscript: A Manuscript object initialized with the data from the Markdown text.

    Example Markdown Input:
    ```
    # Sample Manuscript
    ## Introduction
    This is the introduction.
    ## Background
    This is the background.
    ```

    Notes:
    - The first line is assumed to be the title of the manuscript.
    - Subsequent lines starting with '#' characters denote section titles.
    - The number of '#' characters indicates the nesting level of the section.
    - Lines not starting with '#' characters are considered content for the most recently defined section.
    """
    from .Manuscript import Manuscript
    from .Section import Section

    lines = md_text.strip().split('\n')
    manuscript_title = lines[0].replace('# ', '')
    manuscript = Manuscript(title=manuscript_title)
    current_section = manuscript
    current_indent = 0
    content_lines = []

    def set_content(section, lines):
        content = '\n'.join(lines).strip()
        if content:
            setattr(section, content_field, content)

    for line in lines[1:]:
        match = re.match(r'^(#+) ', line)
        if match:
            set_content(current_section, content_lines)
            content_lines = []

            indent = len(match.group(1))
            title = line.replace(match.group(0), '')
            section = Section(title)

            if indent > current_indent:
                current_section.add_subnode(section)
                current_section = section
            elif indent == current_indent:
                current_section.parent.add_subnode(section)
                current_section = section
            else:
                while current_indent >= indent:
                    current_section = current_section.parent
                    current_indent -= 1
                current_section.add_subnode(section)
                current_section = section

            current_indent = indent
        else:
            content_lines.append(line)

    set_content(current_section, content_lines)

    return manuscript