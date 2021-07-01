from notes_linker import __version__

from notes_linker.modules.markdownNote import MarkdownNote
from notes_linker.modules.traverseFiles import getFilesPaths
from notes_linker.run import loadFiles 

TEST_INPUT = 'Lasso Regression'

def frontMatterExists():
    f = getFilesPaths('notes')
    m = MarkdownNote(TEST_INPUT, f[TEST_INPUT])
    assert m.frontMatterDict['publish'] == 'True'
    return m

def publishAttributeExists():
    m = frontMatterExists()
    assert m.publish == True

def testLoadFiles():
    objects = loadFiles('notes')
    assert objects['lasso-regression'].filenameNormalized == 'lasso-regression'


def test_version():
    assert __version__ == '0.1.0'
