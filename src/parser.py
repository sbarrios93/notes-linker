import re


class MarkdownNote:
    def __init__(self, filename: str, filePath: str):
        self.filename = filename
        self.filePath = filePath
        self.fileText = self._getText()

        # regular expressions
        self.regexHeaderOne = re.compile(
            r"^(#[^#].*)"
        )  # this looks for the H1 headers in the file
        self.regexWikiLink = re.compile(
            r"\[\[(.+)\]\]"
        )  # this will look for all wiki-link-style strings (e.g. [[This is a WikiLink]])
        
        # TODO: make regex for wiki link that includes [[]]
        # functions
        self.fileTitle = self._getTitle()
        self.fileWikiLinks = self._getWikiLinks()

    def _getText(self) -> str:
        with open(self.filePath, "r", encoding="utf-8") as file:
            return file.read()

    def _getTitle(self) -> str:
        firstHeaderOne = self.regexHeaderOne.findall(self.fileText)[0]
        return re.sub(r"^#[ ]*", "", firstHeaderOne)

    def _getWikiLinks(self) -> list:
        return self.regexWikiLink.findall(self.fileText)

    # TODO: add attribute with the relative url link
    # TODO: incorporate with main script