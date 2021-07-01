import re
import os

class MarkdownNote:
    def __init__(self, filename: str, filePath: str, currentImageDir: str = "images",
                 normalizedImageDir: str = "../img/post/"):
        self.filename = filename
        self.filePath = filePath
        self.currentImageDir = currentImageDir
        self.normalizedImageDir = normalizedImageDir
        self.fileExtension = ".md"
        self.fileText = self._getText()


        # regular expressions
        self.regexHeaderOne = re.compile(
            r"^(#[^#].*)",
            re.MULTILINE
        )  # this looks for the H1 headers in the file
        self.regexWikiLink = re.compile(
            r"(\[\[.+\]\])"
        )  # this will look for all wiki-link-style strings (e.g. [[This is a WikiLink]] -> [[This is a WikiLink]])
        self.regexWikiLinkText = re.compile(
            r"\[\[(.+)\]\]"
        )  # this will look for all wiki-link-style strings (e.g. [[This is a WikiLink]] -> This is a WikiLink)
        self.regexFrontMatter = re.compile(r"^---[\s\S]+?---")

        # functions
        self.fileTitle = self._getTitle()
        self.fileWikiLinks = self._getWikiLinks()
        self.fileWikiLinksText = self._getWikiLinksText()
        self.filenameNormalized = self._normalizeFilename()
        self.fullCurrentImageDir = self._getCurrentImageDir()
        self.fullNormalizedImageDir = self._getNormalizedImageDir()
        self.frontMatterDict = self._passFrontMatter()
        

    def _getText(self) -> str:
        with open(self.filePath, "r", encoding="utf-8") as file:
            return file.read()

    def _getTitle(self) -> str:
        firstHeaderOne = self.regexHeaderOne.findall(self.fileText)[0]
        return re.sub(r"^#[ ]*", "", firstHeaderOne)

    def _getWikiLinks(self) -> list:
        return self.regexWikiLink.findall(self.fileText)
        
    def _getWikiLinksText(self) -> list:
        return self.regexWikiLinkText.findall(self.fileText)

    def _normalizeFilename(self) -> str:
        return self.filename.lower().replace(" ", "-")

    def _getCurrentImageDir(self) -> str:
        return os.path.join(self.currentImageDir, self.filename)

    def _getNormalizedImageDir(self) -> str:
        return os.path.join(self.normalizedImageDir, self.filenameNormalized)

    def _passFrontMatter(self) -> dict:
        frontMatter = self.regexFrontMatter.findall(self.fileText)
        if not frontMatter:
            raise RuntimeError("No frontmatter detected")
        # clean frontmatter, remove '---', remove whitespace and
        # return dictionary with key, value for each attribute in frontmatter
        frontMatter = frontMatter[0].replace('---', '').split('\n')
        frontMatter = [re.sub(r"^\s+|\s+$", "", a) for a in frontMatter if a]
        frontMatterDict = {re.search(r"(^[a-zA-Z0-9]*)[^:]", i).group(0): re.search(r":[ ]*(.*)\s*$", i).group(1) for i in frontMatter}

        assert "publish" in frontMatterDict, "There should be at least a key 'publish' in the front matter"
        # assign keys of dictionary to attributes of the class
        for key in frontMatterDict:
            setattr(self, key, frontMatterDict[key])
        
        return frontMatterDict


