import os
from shutil import copy

from notes_linker.modules.fileImporter import loadFiles
from notes_linker.modules.linkSearch import loopSearchWikiLinks


def addWikiLinks(notesDict: dict, linksMasterDict: dict) -> None:
    for title, note in notesDict.items():
        links = linksMasterDict.get(title, {}) if linksMasterDict.get(title, {}) else None
        if links is not None:
            linksToTitleMap, linksToRelativeLinkMap = dict(), dict()
            for link in links:
                linksToTitleMap[link] = notesDict[link].fileTitle
                linksToRelativeLinkMap[link] = notesDict[link].filenameNormalized
            note.addWikiLinksSection(links, linksToTitleMap, linksToRelativeLinkMap)

def copyImages(obj: object, input: str, output: str) -> None:
    """This will copy all the images related to a MarkdownNote into the output folder (which is an attribute of the MarkdownNote Object)

    Args:
        obj (MarkdownNote): [The note as a MarkdownNote object]
        input (str): [The source of the notes folder where the image folder is contained]
        output (str): [The output folder where the image folder will be copied to]
    """
    # we need to check if the input image folder exists
    # images are in the directory 'obj.fullCurrentImageDir' and need to be moved to 'obj.fullNormalizedImageDir' inside the output folder
    inputImgPath = os.path.join(input, obj.fullCurrentImageDir)
    outputImgPath = os.path.join('.', output, obj.fullNormalizedImageDir)
    if os.path.exists(inputImgPath):
        # check if output directory exists, otherwise create it
        if not os.path.exists(outputImgPath):
            os.makedirs(outputImgPath)
        # get list of images in inputImgPath
        imagesList = [image for image in os.listdir(inputImgPath) if os.path.isfile(os.path.join(inputImgPath, image))]
        # copy to output directory
        for image in imagesList:
            copy(os.path.join(inputImgPath, image), outputImgPath)
        


def run(
    input: str,
    output: str,
    outputNotesSubDir: str,
    currentImageDir: str,
    normalizedImageDir: str,
    linkImageDir: str,
    frontMatterTemplate: dict,
) -> None:
    # load files and manipulate each note as a MarkdownNote object
    f = loadFiles(
        path=input,
        currentImageDir=currentImageDir,
        normalizedImageDir=normalizedImageDir,
        linkImageDir=linkImageDir,
    )
    w = loopSearchWikiLinks(f)
    addWikiLinks(f, w)
    outputNotesPath = os.path.join(output, outputNotesSubDir)
    for note in f.values():
        note.replaceLinks(f)
        note.updateFrontMatter(frontMatterTemplate)
        note.joinText()
        note.outputFile(outputNotesPath)
        copyImages(obj=note, input=input, output=output)

