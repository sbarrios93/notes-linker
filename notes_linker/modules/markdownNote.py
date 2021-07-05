import re
import regex
import os
import warnings


class MarkdownNote:
    def __init__(
        self,
        filename: str,
        filePath: str,
        modDate,
        currentImageDir: str,
        normalizedImageDir: str,
        linkImageDir: str,
        outputLinkPath: str = ".",
        quiet: bool = True,
    ):
        self.filename = filename
        self.filePath = filePath
        self.modDate = modDate
        self.currentImageDir = currentImageDir
        self.normalizedImageDir = normalizedImageDir
        self.outputLinkPath = outputLinkPath
        self.quiet = quiet

        self.fileExtension = ".md"
        self.fileText = self._getText()
        
        # on tests, the linkImageDir parameter, which is the markdownLinkImageDir config setting in config.yaml was appearing as a tuple...a quick fix was to use the 0 index of the tuple in case it was an iterable item instead of a string
        if (not isinstance(linkImageDir, str)) and hasattr(linkImageDir, '__iter__'):
            self.linkImageDir = linkImageDir[0],
        else:
            self.linkImageDir = linkImageDir
        if not isinstance(self.linkImageDir, str):
            raise TypeError(f"There's an issue with the setting markdownLinkImageDir, current type is {type(self.linkImageDir)} -> it should be a string")

        self.fileTitle = None
        self.fileWikiLinks = None
        self.fileWikiLinksText = None
        self.filenameNormalized = None
        self.fullCurrentImageDir = None
        self.fullNormalizedImageDir = None
        self.fullOutputLinkPath = None
        self.outputFrontMatterText = str()

        self.publish = False
        self.WikiLinksSection = None

        # initialize output text == input text for now
        self.fullOutputText = self.fileText

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

        self.regexLatexDisplay = regex.compile(r'(\\\[)([\s]*)([\s\S]*?)([\s]*?)(\\\])')
        self.regexLatexInline = regex.compile(r'(\\\()([\s]*)([\s\S]*?)([\s]*?)(\\\))')

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
            self.fullOutputLinkPath = os.path.join(self.outputLinkPath, self.filenameNormalized + self.fileExtension)
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
        return self.filename.lower().replace(" ", "-").replace(".", "").replace(",", "")

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

    def addWikiLinksSection(self, linksDict, linksToTitleMap, linksToRelativeLinkMap):
        # create wiki links block of text that will be appended at the end of the markdown file
        if linksDict:
            self.WikiLinksSection = "\n\n"  " Backlinks {:.backlinks-header}" +"\n"
            for title, sentence in linksDict.items():
                # titles in linksDict have the form 'this-is-a-title' so we need the proper title
                properTitle = linksToTitleMap[title]
                # we need to get the proper link that will be printed in the md file
                relativeLink = linksToRelativeLinkMap[title]
                # for each note in the backlinks, make a h4 header with a link to that note
                self.WikiLinksSection += "\n" + f" [{properTitle}](/{relativeLink.strip()})\n\n"
                if sentence:
                    # then add each sentence as a bullet point
                    for s in sentence:
                        self.WikiLinksSection += f"- {s.strip()}\n"
                    # after all the sentences for a note have been added, include an extra \n to divide
                    self.WikiLinksSection += "\n"

    def replaceLinks(self, notes: dict) -> str:
        # this function will take the whole text from the markdown
        # and replace all the [[links in this form]] with real markdown links. It will also call the subfunction replaceImageLinks to replace links with links formatted for the website 
        def replaceImageLinks(content) -> str:
            # this function will replace all the image links in markdown for valid links to the website
            regexString = regex.compile(r'!\[([^\]]*)\]\(.*\/(?<filename>.*?)(?=\"|\))(?<optionalpart>\".*\")?\)|!\[([^\]]*)\]\([^\/]*?(?<filename2>.*?)(?=\"|\))(?<optionalpart2>\".*\")?\)')  # find all text in the form ![Title](url "alt")
            # create markdown pointer to image directory
            linkImageDirWithFilename = os.path.join(self.linkImageDir, self.filenameNormalized)
            return regex.sub(regexString, fr'![\1](/{linkImageDirWithFilename}/\2 \3)', content)


        content = self.fileText
        # the dict is in the form
        # {'this-is-a-title': MarkdownNote.Object} so we are going to change the keys to
        # match them with the wikiLinks attribute of the note, which has links in the shape
        # [[This is a title]]
        notes = {f"[[{obj.fileTitle}]]": obj for key, obj in notes.items()}
        # if there's some text in the note styled as a wikilink, but it's not in the map, then delete the [[]]
        for link in self.fileWikiLinks:
            if link not in notes.keys():
                linkCleaned = link.replace("[[", "").replace("]]", "")
                content = content.replace(link, linkCleaned)
            else:
                constructedLink = f"[{(notes[link].fileTitle).strip()}](/{(notes[link].filenameNormalized).strip()})"
                content = content.replace(link, constructedLink)

        content = replaceImageLinks(content=content)    
        self.fullOutputText = content
    
    def updateFrontMatter(self, frontMatterTemplate: dict, outputText: bool = True) -> str:
        templateCopy = frontMatterTemplate.copy()
        templateCopy.update(self.frontMatterDict)
        if templateCopy.get("title", None) is None:
            templateCopy["title"] = self.fileTitle
        if templateCopy.get("date", None) is None and self.modDate:
            templateCopy["date"] = self.modDate
        if templateCopy.get("toc", None) is not None:
            templateCopy["toc"] = str(templateCopy["toc"]).lower()
        
        # there's an issue in the website where if there's a latex delimiter in the first 140 characters, json-ld will throw an error because it uses those characters to read the config. They way to fix this is to add "dump" to a description tag in the frontmatter.
        if regex.search(r'\\\(|\\\[|\$', self.fullOutputText):
            if min(regex.search(r'\\\(|\\\[|\$', self.fullOutputText).span()) <= 220:
                if templateCopy.get("description", None) is not None:
                    templateCopy["description"] += " | dump"
                else:
                    templateCopy["description"] = "dump"
            
        self.outputFrontMatterDict = templateCopy
        if outputText:
            self.outputFrontMatterText += "---\n"
            for key, value in self.outputFrontMatterDict.items():
                if value is not None:
                    self.outputFrontMatterText += f"{key}: {value}\n"
            self.outputFrontMatterText += "---\n\n"


    def transformLatexDelimiters(self, content):
        # \[ x + 2 \] -> $$x+2$$ and \(x + 2\) -> $x+2$
        fixedDisplay = regex.sub(self.regexLatexDisplay, r'$$\3$$', content)
        #now fix inline and return
        return regex.sub(self.regexLatexInline, r'$\3$', fixedDisplay)

        
    def joinText(self):
        # this will join outputFrontMatterText, fileText, WikiLinksSection
        ####
        ### first we need to remove the old frontmatter from fullOutputText
        postFrontMatter = self.regexContentPostFrontMatter.findall(self.fullOutputText)
        if not postFrontMatter:
            raise Exception("No text found after frontmatter while attempting to join output text")
        # strip leading/trailing whitespace
        postFrontMatter = postFrontMatter[0].strip()
        # run removeBreaksDisplayLatex
        postFrontMatter = self.transformLatexDelimiters(postFrontMatter)
        # concatenate sections
        self.fullOutputText = self.outputFrontMatterText + postFrontMatter
        if self.WikiLinksSection is not None:
            self.fullOutputText += self.WikiLinksSection

    def outputFile(self, outputNotesPath) -> None:
        dirOfNote = os.path.join('.', outputNotesPath)
        if not os.path.exists(dirOfNote):
            os.makedirs(dirOfNote)
        pathOfNote = os.path.join(dirOfNote, self.filenameNormalized + self.fileExtension)
        with open(pathOfNote, 'w', encoding='utf-8') as f:
           f.write(self.fullOutputText)

