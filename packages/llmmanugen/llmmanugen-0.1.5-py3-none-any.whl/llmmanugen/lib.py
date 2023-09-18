import re
from datetime import datetime
from .Section import Section


def parse_markdown_to_manuscript(manuscript_instance, md_text, content_field="content"):

    """
    Parses a Markdown-formatted text to create a Manuscript object with nested Section objects.

    The function reads the Markdown text line by line, identifying section titles based on the number of '#' characters.
    It then recursively constructs Section objects for each section and its sub-sections, adding them to a Manuscript object.

    Parameters:
        - manuscript_instance (Manuscript): The Manuscript instance to populate.
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
    lines = md_text.strip().split('\n')
    manuscript_title = lines[0].replace('# ', '')
    manuscript_instance.title = manuscript_title
    manuscript = manuscript_instance
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

    return manuscript_instance


def parse_dictionary_to_manuscript(manuscript_instance, data):

    """
    Parse a dictionary to populate a Manuscript instance.

    Parameters:
        - manuscript_instance (Manuscript): The Manuscript instance to populate.
        - data (dict): The dictionary containing manuscript data.

    Returns:
        Manuscript: The populated Manuscript instance.
    """
    def dictionary_to_sections(sections):

        """
        Convert a list of dictionaries to a list of Section objects.

        Parameters:
            - sections (list): A list of dictionaries, each representing a section.

        Returns:
            list: A list of Section objects.
        """
        section_objects = []
        for section in sections:

            created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            kwdict = {
                'summary': section.get('summary', ''),
                'content': section.get('content', ''),
                'prompt': section.get('prompt', None),
                'completed': section.get('completed', ''),
                'created': section.get('created', created),
                'updated': section.get('updated', section.get('created', created))
            }

            sub_sections = section.get('sections', [])
            if sub_sections:
                sub_sections = dictionary_to_sections(sub_sections)

            section_objects.append(Section(section.get('title', ''), *sub_sections, **kwdict))

        return section_objects

    manuscript_instance.title = data.get("title", "Untitled")
    manuscript_instance._init(**{k: v for k, v in data.items() if k not in ["title", "sections"]})

    if "sections" in data:
        manuscript_instance.add_sections(*dictionary_to_sections(data["sections"]))

    return manuscript_instance
