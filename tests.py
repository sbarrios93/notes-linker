from yaml import Mark
from src.markdownNote import MarkdownNote
from src.traverseFiles import getFilesPaths
from run import loadFiles 

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

if __name__ == '__main__':
    frontMatterExists()
    publishAttributeExists()
    testLoadFiles()
    print('All tests passed')
