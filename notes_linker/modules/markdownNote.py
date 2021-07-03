import re
import regex
import os
import warnings


class MarkdownNote:
    def __init__(
        self,
        filename: str,
        filePath: str,
        currentImageDir: str = "images",
        normalizedImageDir: str = "../img/post/",
        quiet: bool = True,
    ):
        self.filename = filename
        self.filePath = filePath
        self.currentImageDir = currentImageDir
        self.normalizedImageDir = normalizedImageDir
        self.quiet = quiet
        self.fileExtension = ".md"
        self.fileText = self._getText()

        self.fileTitle = None
        self.fileWikiLinks = None
        self.fileWikiLinksText = None
        self.filenameNormalized = None
        self.fullCurrentImageDir = None
        self.fullNormalizedImageDir = None

        self.publish = False
        self.WikiLinksSection = None

        # regular expressions
        self.regexHeaderOne = regex.compile(r"^(#[^#].*)", re.MULTILINE)  # this looks for the H1 headers in the file

        self.regexWikiLink = regex.compile(
            r"(\[\[.+?\]\])"
        )  # this will look for all wiki-link-style strings (e.g. [[This is a WikiLink]] -> [[This is a WikiLink]])

        self.regexWikiLinkText = regex.compile(
            r"\[\[(.+?)\]\]"
        )  # this will look for all wiki-link-style strings (e.g. [[This is a WikiLink]] -> This is a WikiLink)

        self.regexWikiLinkSentences = lambda _wikiLink: regex.compile(
            fr"[^.?!\n]*(?<=[.?\s!\n])\[\[{_wikiLink}\]\].*?(?=[\s.?!\n])[^.?!\n]*[.?!\n]"
        )  # this lambda function lets you input a wikilink (without the brackets and get all the surrounding text (the sentence where that wikilink exists.))

        self.regexFrontMatter = regex.compile(r"^---[\s\S]+?---")  # find the frontmatter element

        self.regexContentPostFrontMatter = regex.compile(
            r"^---[\s\S]+?---\K[\s\S]*\S[\s\S]*", flags=regex.DOTALL
        )  # find everything that there is after a front matter.

        self.regexContentNoFrontMatter = regex.compile(
            r"[\s\S]*\S[\s\S]*", flags=regex.DOTALL
        )  # find everything that there is when there's no front matter

        # get structure of note
        self.frontMatterDict = self._passFrontMatter()
        self.hasContent = self._checkHasContent()

        # before running the below functions we need to check if the file has any content
        # (besides the frontmatter)
        # functions
        if self.hasContent:
            self.fileTitle = self._getTitle()
            self.fileWikiLinks = self._getWikiLinks()
            self.fileWikiLinksText = self._getWikiLinksText()
            self.fileWikiLinksSentences = self._getWikiLinksSentences()
            self.filenameNormalized = self._normalizeFilename()
            self.fullCurrentImageDir = self._getCurrentImageDir()
            self.fullNormalizedImageDir = self._getNormalizedImageDir()
        else:
            # if quiet is set to true, show warning when file has no content besides frontmatter
            if not self.quiet:
                warnings.warn(f"File {filename} ({filePath}) has no content.")

        # modify type of value in self.publish
        if not isinstance(self.publish, bool):
            if (self.publish == "True") or (self.publish == "true"):
                self.publish = True
            else:
                self.publish = False

    def _getText(self) -> str:
        with open(self.filePath, "r", encoding="utf-8") as file:
            return file.read()

    def _getTitle(self) -> str:
        firstHeaderOne = self.regexHeaderOne.findall(self.fileText)
        return re.sub(r"^#[ ]*", "", firstHeaderOne[0]) if firstHeaderOne else self.filename

    def _getWikiLinks(self) -> list:
        # ...[[This is a WikiLink]]... -> [[This is a WikiLink]]
        return list(set(self.regexWikiLink.findall(self.fileText)))

    def _getWikiLinksText(self) -> list:
        # [[This is a WikiLink]] -> This is a WikiLink
        return list(set(self.regexWikiLinkText.findall(self.fileText)))

    def _getWikiLinksSentences(self) -> dict:
        sentencesDict = dict()
        for link in self.fileWikiLinksText:
            regex_ = self.regexWikiLinkSentences(link)
            sentencesDict[link] = regex_.findall(self.fileText)
        return sentencesDict

    def _normalizeFilename(self) -> str:
        # This is a Title -> this-is-a-title
        return self.filename.lower().replace(" ", "-")

    def _getCurrentImageDir(self) -> str:
        return os.path.join(self.currentImageDir, self.filename)

    def _getNormalizedImageDir(self) -> str:
        return os.path.join(self.normalizedImageDir, self.filenameNormalized)

    def _passFrontMatter(self) -> dict:
        # init frontMatterDict (this is the returned dict of this function)
        frontMatterDict = dict()
        frontMatter = self.regexFrontMatter.findall(self.fileText)

        # set an attribute if frontmatter exists in the file or not
        # if it doesn't exists, set a single value in returned dictionary
        # where publish is false.
        if not frontMatter:
            self.frontMatterExists = False
            # the value publish in the markdown is True or False with type string, so we use the same type to pass the value in the dictionary
            frontMatterDict = {"publish": "False"}
            if not self.quiet:
                warnings.warn(
                    f"Front matter NOT DETECTED in file {self.filename} ({self.filePath}), the 'publish' value will be set to 'False'"
                )
        else:
            self.frontMatterExists = True
            # clean frontmatter, remove '---', remove whitespace and
            # return dictionary with key, value for each attribute in frontmatter
            frontMatter = frontMatter[0].replace("---", "").split("\n")
            frontMatter = [re.sub(r"^\s+|\s+$", "", a) for a in frontMatter if a]
            frontMatterDict = {
                re.search(r"(^[a-zA-Z0-9]*)[^:]", i).group(0): re.search(r":[ ]*(.*)\s*$", i).group(1)
                for i in frontMatter
            }

            # if "publish" not a key in the dictionary (wasn't in the frontmatter), set it by default to false, print warning.
            if "publish" not in frontMatterDict and not self.quiet:
                warnings.warn(
                    f"Front matter in file {self.filename} ({self.filePath})detected but didn't have key 'publish', so it has been set as 'False' by default"
                )
                # the value publish in the markdown is True or False with type string, so we use the same type to pass the value in the dictionary
                frontMatterDict["publish"] = "False"
            # assign keys of dictionary to attributes of the class
        for key in frontMatterDict:
            setattr(self, key, frontMatterDict[key])

        return frontMatterDict

    def _checkHasContent(self) -> bool:
        if self.frontMatterExists:
            return True if self.regexContentPostFrontMatter.findall(self.fileText) else False
        else:
            return True if self.regexContentNoFrontMatter.findall(self.fileText) else False

    # def addWikiLinksSection(self, )
