from bs4 import NavigableString


class LinkedText:
    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return f"<LinkedText: {self.text} ({self.link})>"

    @property
    def link(self):
        if isinstance(self.content, NavigableString):
            return None
        return (self.content.a or self.content).get("href")

    @property
    def text(self):
        return self.content.text.strip()
