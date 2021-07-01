from yaml import Mark
from src.markdownNote import MarkdownNote
from src.traverseFiles import getFilesPaths

TEST_INPUT = 'Lasso Regression'

def frontMatterExists():
    f = getFilesPaths('notes')
    m = MarkdownNote(TEST_INPUT, f[TEST_INPUT])
    assert m.frontMatterDict['publish'] == 'True'
    return m

def publishAttributeExists():
    m = frontMatterExists()
    assert m.publish == "True"


if __name__ == '__main__':
    frontMatterExists()
    publishAttributeExists()
    print('All tests passed')
