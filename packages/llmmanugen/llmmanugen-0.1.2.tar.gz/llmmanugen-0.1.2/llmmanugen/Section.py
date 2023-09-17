from datetime import datetime
from .Node import Node


class Section(Node):
    """
    Represents a section in a manuscript or document hierarchy.

    Attributes:
        title (str): The title of the section.
        summary (str, optional): A brief summary of the section.
        content (str, optional): The main content of the section.
        prompt (str, optional): A prompt related to the section.
        _created (str): The timestamp when the section was created.
        _updated (str): The timestamp when the section was last updated.

    Methods:
        update(title=None, summary=None, content=None, prompt=None):
            Update the section's attributes and refresh the timestamp.
        _update_timestamp():
            Update the timestamp to the current time.

    Properties:
        title: Gets or sets the title of the section.
        summary: Gets or sets the summary of the section.
        content: Gets or sets the content of the section.
        prompt: Gets or sets the prompt of the section.

    Subscriptable:
        __getitem__(key): Retrieve an attribute value using a key.
        __setitem__(key, value): Set an attribute value using a key.
    """
    def __init__(self, title, *nodes, summary=None, content=None, prompt=None, completed=None, created=None, updated=None, **kwargs):
        """
        Initializes a new Section instance with a title and optional summary, content, and prompt, completed, created, and updated.

        Parameters:
            title (str): The title of the section.
            *nodes (Node): Variable-length list of child nodes to be attached to this section.
            summary (str, optional): A brief summary of the section.
            content (str, optional): The main content of the section.
            prompt (str, optional): A prompt related to the section.
            completed (bool, optional): A completed related to the section.
            created (str, optional): A created related to the section.
            updated (str, optional): A updated related to the section.
        """
        # Make sure that all subnodes are type of Section
        def traverse(node):
            if not isinstance(node, Section):
                node = Section(**node)
            if node.has_subnodes():
                for subnode in node.subnodes:
                    traverse(subnode)
            return node
        super().__init__(title, *(traverse(node) for node in nodes))
        self._summary = summary if summary else ""
        self._content = content if content else ""
        self._prompt = prompt
        self._completed = True if completed else False
        self._created = created if created else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._updated = updated if updated else self._created
        # Note: Not used for any particular case so far.
        self._additional_fields = kwargs

    def update(self, title=None, summary=None, content=None, prompt=None, completed=False):
        """
        Updates the properties of the Section instance with new values.

        Parameters:
            title (str, optional): New title for the section.
            summary (str, optional): New summary for the section.
            content (str, optional): New content for the section.
            prompt (str, optional): New prompt for the section.
            completed (bool, optional): New completed for the section.

        Note:
            This method will also update the timestamp of the last modification.
        """
        if title:
            self._title = title
        if summary:
            self._summary = summary
        if content:
            self._content = content
        if prompt:
            self._prompt = prompt
        if completed:
            self._completed = completed
        self._update_timestamp()

    @property
    def title(self):
        """
        str: Gets or sets the title of the Section. Raises a ValueError if an attempt is made to set it to an empty value.
        """
        return self._title

    @title.setter
    def title(self, value):
        """
        Sets the title of the Section and updates the timestamp.
        """
        if not value:
            raise ValueError('Title cannot be empty')
        self._title = value
        self._update_timestamp()

    def _update_timestamp(self):
        """
        Updates the timestamp of the last modification to the current time.
        """
        self._updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @property
    def summary(self):
        """
        str: Gets or sets the summary of the Section. Also updates the timestamp when set.
        """
        return self._summary

    @summary.setter
    def summary(self, value):
        """
        Sets the summary of the Section and updates the timestamp.
        """
        self._summary = value
        self._update_timestamp()

    @property
    def content(self):
        """
        str: Gets or sets the content of the Section. Also updates the timestamp when set.
        """
        return self._content

    @content.setter
    def content(self, value):
        """
        Sets the content of the Section and updates the timestamp.
        """
        self._content = value
        self._update_timestamp()

    @property
    def prompt(self):
        """
        str: Gets or sets the prompt of the Section. Also updates the timestamp when set.
        """
        return self._prompt

    @prompt.setter
    def prompt(self, value):
        """
        Sets the prompt of the Section and updates the timestamp.
        """
        self._prompt = value
        self._update_timestamp()

    @property
    def completed(self):
        """
        str: Gets or sets the completed state of the Section. Also updates the timestamp when set.
        """
        return self._completed

    @completed.setter
    def completed(self, value):
        """
        Sets the completed state of the Section and updates the timestamp.
        """
        self._completed = value
        self._update_timestamp()

    @property
    def created(self):
        """
        str: Gets or sets the created data of the Section. Also updates the timestamp when set.
        """
        return self._created

    @property
    def updated(self):
        """
        str: Gets or sets the updated data of the Section. Also updates the timestamp when set.
        """
        return self._updated

    def are_childs_complete(self):
        """
        Checks if all child nodes and their subnodes are marked as completed.

        Returns:
            bool: True if all child nodes and their subnodes are completed, False otherwise.
        """

        for node in self.subnodes:
            if not node.completed or (node.subnodes and not node.are_childs_complete()):
                return False
        return True

    def count_content_words_and_letters(self, include_all_subsections=False):
        """
        Counts the total number of words and letters in the content of the current node and optionally its subnodes.

        Parameters:
            - include_all_subsections (bool): Whether to include the word and letter counts of all subnodes. Default is False.

        Returns:
            tuple: A tuple containing the total word count and total letter count.
        """
        words_count, letters_count = len(self.content.split()), len(self.content)
        if include_all_subsections and self.has_subnodes():
            for node in self.subnodes:
                word_count, letter_count = node.count_content_words_and_letters(node.has_subnodes())
                words_count += word_count
                letters_count += letter_count
        return words_count, letters_count

    def __getitem__(self, key):
        """
        Retrieves an attribute by key name. Returns None if the attribute does not exist.

        Parameters:
            key (str): The name of the attribute to retrieve.

        Returns:
            The value of the attribute if it exists, None otherwise.
        """
        return getattr(self, key, self._additional_fields.get(key, None))

    def __setitem__(self, key, value):
        """
        Sets an attribute by key name and updates the timestamp if the attribute exists.

        Parameters:
            key (str): The name of the attribute to set.
            value: The value to set the attribute to.
        """
        if hasattr(self, key):
            setattr(self, key, value)
            self._update_timestamp()
        elif key in self._additional_fields:
            self._additional_fields[key] = value
            self._update_timestamp()
