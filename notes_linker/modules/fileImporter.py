import os
from notes_linker.modules.markdownNote import MarkdownNote
import datetime


def getFilesPaths(
    path_: str,
    ext_: str = ".md",
    excludeFolders: list = None,
    excludeHidden: bool = True,
) -> dict:
    """This will traverse all the files in the directory and its subdirectories
    to find all the markdown files

    Args:
        path_ (str): path to the parent directory to traverse
        ext_ (str): extension type of the files to look for
        excludeFolders (list): list of directories to exclude
        excludeHidden (bool): whether to exclude hidden directories (starting with ".")

    Returns:
        dict : dictionary containing file names without extensions as keys and paths to its file (containing the file name) as values.
    """
    # init dict to be returned by function
    fileDict = dict()

    for root, dirs, files in os.walk(path_):
        # exclude directories in the excludeFolders list
        if excludeFolders:
            dirs[:] = [d for d in dirs if d not in excludeFolders]
        # exclude directories and files starting with '.' if excludeHidden is True
        if excludeHidden:
            dirs[:] = [d for d in dirs if not d[0] == "."]
            files[:] = [f for f in files if not f[0] == "."]
        for file in files:
            if file.endswith(ext_):
                # split the filename on its extension, to get a clean file name
                filenameSplit = file.split(ext_)
                # check if filename can be split by its extension type just once, if not, then this is an invalid name. e.g. "file1.md.md" is not a valid name
                assert len(filenameSplit) == 2, f"Filename: {file} is not a valid name"
                # add filename, path to dictionary
                fileDict[filenameSplit[0]] = os.path.join(root, file)
    return fileDict


def loadFiles(path: str, currentImageDir: str, normalizedImageDir: str,linkImageDir: str, quiet: bool = True):
    # load the name of markdown files and the path to each of them in a dict
    filesDict = getFilesPaths(path)

    # objectsDict will be the dictionary returned from the function, where key = normalized file
    # name and value = MarkdownNote object
    objectsDict = dict()

    # loop through each file and make a MarkdownNote object for each file
    # then get the normalized file name from each object and make entry in dictionary
    # where key is object's normalized name and value is the object
    for file, filePath in filesDict.items():
        mdNote = MarkdownNote(
            file,
            filePath,
            modDate = datetime.datetime.utcfromtimestamp(os.path.getmtime(filePath)).strftime('%Y-%m-%d'),
            currentImageDir=currentImageDir,
            normalizedImageDir=normalizedImageDir,
            linkImageDir=linkImageDir,
            quiet=quiet,
        )
        # don't iterate if value of publish of the note is set to False or the note has no content
        if mdNote.publish and mdNote.hasContent:
            objectsDict[mdNote.filenameNormalized] = mdNote
    return objectsDict
