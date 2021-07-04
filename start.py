import yaml
from notes_linker.run import run

# TODO: move images to correct directory

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
        currentImageDir=settings["currentImgDir"],
        normalizedImageDir=settings["outputImgDir"],
        wikiHeadingLevel=settings["wikiHeadingLevel"],
        frontMatterTemplate=frontMatterTemplate,
    )

if __name__ == "__main__":
    main()