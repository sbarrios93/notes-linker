from notes_linker import __version__

from notes_linker.modules.markdownNote import MarkdownNote
from notes_linker.modules.fileImporter import getFilesPaths, loadFiles
from notes_linker.modules.linkSearch import loopSearchWikiLinks
import pytest

TEST_INPUT = "Lasso Regression"


def testFrontMatterExists():
    f = getFilesPaths("notes")
    m = MarkdownNote(TEST_INPUT, f[TEST_INPUT])
    assert m.frontMatterDict["publish"] == "True"
    return m


def testPublishAttributeExists():
    m = testFrontMatterExists()
    assert m.publish is True


def testLoadFiles():
    objects = loadFiles("notes")
    assert objects["lasso-regression"].filenameNormalized == "lasso-regression"


def testCheckWikiLinksStructure():
    objects = loadFiles("notes")
    wikiLinks = loopSearchWikiLinks(objects)
    assert wikiLinks is not None


def test_version():
    assert __version__ == "0.1.0"
