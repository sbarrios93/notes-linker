from notes_linker.modules.traverseFiles import getFilesPaths
from notes_linker.modules.markdownNote import MarkdownNote

# TODO: append loopSearchBackLinks content to each markdown file.
# TODO: rename files
# TODO: change wikilinks to markdown links.
# TODO: move images to correct directory


def loadFiles(path: str = "notes", quiet: bool = True):
    # load the name of markdown files and the path to each of them in a dict
    filesDict = getFilesPaths(path)

    # objectsDict will be the dictionary returned from the function, where key = normalized file
    # name and value = MarkdownNote object
    objectsDict = dict()

    # loop through each file and make a MarkdownNote object for each file
    # then get the normalized file name from each object and make entry in dictionary
    # where key is object's normalized name and value is the object
    for file, filePath in filesDict.items():
        mdNote = MarkdownNote(file, filePath, quiet=quiet)
        # don't iterate if value of publish of the note is set to False or the note has no content
        if mdNote.publish and mdNote.hasContent:
            objectsDict[mdNote.filenameNormalized] = mdNote
    return objectsDict


def loopSearchBackLinks(objects: dict) -> dict:
    # generate a dict with keys of objects dict and empty lists as values
    backlinks: dict[str, list] = {key: [] for key in objects.keys()}
    for key in backlinks.keys():
        for title, sentence in objects[key].fileWikiLinksSentences.items():
            # following temp list will look for the normalized name of the file for the title we are
            # iterating over
            tempList = [name for name, obj in objects.items() if obj.filename == title]
            if tempList:
                backlinks[tempList[0]].append(sentence)
    return backlinks
#
