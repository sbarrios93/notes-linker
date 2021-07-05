import yaml
from notes_linker.run import run

# TODO: remove re module, use only regex module

def parseConfig():
    with open("config.yaml", "r") as ymlfile:
        config = yaml.load(ymlfile)
    settings = config["settings"]
    frontMatterTemplate = config["frontMatterTemplate"]

    return settings, frontMatterTemplate


def main():
    settings, frontMatterTemplate = parseConfig()
    run(
        input=settings["inputDir"],
        output=settings["outputDir"],
        outputNotesSubDir=settings["outputNotesSubDir"],
        currentImageDir=settings["currentImgDir"],
        normalizedImageDir=settings["outputImgDir"],
        linkImageDir=settings["markdownLinkImageDir"],
        frontMatterTemplate=frontMatterTemplate,
    )

if __name__ == "__main__":
    main()