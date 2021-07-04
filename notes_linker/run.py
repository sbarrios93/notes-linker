from notes_linker.modules.fileImporter import loadFiles
from notes_linker.modules.linkSearch import loopSearchWikiLinks


def addWikiLinks(notesDict: dict, linksMasterDict: dict) -> None:
    for title, note in notesDict.items():
        links = linksMasterDict.get(title, {}) if linksMasterDict.get(title, {}) else None
        if links is not None:
            linksToTitleMap, linksToRelativeLinkMap = dict(), dict()
            for link in links:
                linksToTitleMap[link] = notesDict[link].fileTitle
                linksToRelativeLinkMap[link] = notesDict[link].fullOutputLinkPath
            note.addWikiLinksSection(links, linksToTitleMap, linksToRelativeLinkMap)


def run(
    input: str,
    output: str,
    currentImageDir: str,
    normalizedImageDir: str,
    wikiHeadingLevel: int,
    frontMatterTemplate: dict,
) -> None:
    # load files and manipulate each note as a MarkdownNote object
    f = loadFiles(
        path=input,
        currentImageDir=currentImageDir,
        normalizedImageDir=normalizedImageDir,
        wikiHeadingLevel=wikiHeadingLevel,
    )
    w = loopSearchWikiLinks(f)
    addWikiLinks(f, w)
    for note in f.values():
        note.replaceLinks(f)
        note.updateFrontMatter(frontMatterTemplate)
        note.joinText()
        note.outputFile(output)
