from notes_linker import __version__

from notes_linker.modules.markdownNote import MarkdownNote
from notes_linker.modules.traverseFiles import getFilesPaths
from notes_linker.run import loadFiles
import pytest

TEST_INPUT = "Lasso Regression"


def frontMatterExists():
    print('1')
    f = getFilesPaths("notes")
    m = MarkdownNote(TEST_INPUT, f[TEST_INPUT])
    assert m.frontMatterDict["publish"] == "True"
    return m


def publishAttributeExists():
    print('2')
    m = frontMatterExists()
    assert m.publish == True


def testLoadFiles():
    print('3')
    objects = loadFiles("notes")
    assert objects["lasso-regression"].filenameNormalized == "lasso-regression"


def test_version():
    print('4')
    assert __version__ == "0.1.0"
