from notes_linker.modules.traverseFiles import getFilesPaths
from notes_linker.modules.markdownNote import MarkdownNote

def loadFiles(path: str = 'notes', quiet: bool = True):
    # load the name of markdown files and the path to each of them in a dict
    filesDict = getFilesPaths(path)

    # objectsDict will be the dictionary returned from the function, where key = normalized file name and value = MarkdownNote object
    objectsDict = dict()
    
    # loop through each file and make a MarkdownNote object for each file
    # then get the normalized file name from each object and make entry in dictionary
    # where key is object's normalized name and value is the object
    for file, filePath in filesDict.items():
        mdNote = MarkdownNote(file, filePath, quiet = quiet)
        # don't iterate if value of publish of the note is set to False or the note has no content
        if mdNote.publish == True and mdNote.hasContent == True:
            objectsDict[mdNote.filenameNormalized] = mdNote
    return objectsDict


# TODO: loop through objects and append which other files reference said object
def loopSearchBackLinks(objects: dict) -> dict:
    # generate a dict with keys of objects dict and empty lists as values
    backlinks = {key: [] for key in objects.keys()}
    for key, value in backlinks.items():
        