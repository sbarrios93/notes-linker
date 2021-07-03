
def loopSearchWikiLinks(objects: dict) -> dict:
    # generate a dict with keys of objects dict and empty dict as values
    wikiLinks: dict[str, list] = {key: {} for key in objects.keys()}
    for key in wikiLinks.keys():
        for title, sentence in objects[key].fileWikiLinksSentences.items():
            # following temp list will look for the normalized name of the file for the title we are
            # iterating over
            tempList = [name for name, obj in objects.items() if obj.filename == title]
            if tempList:
                # now, what we are doing here is to create a dictionary where
                # the parent key is the note being referred in
                # the sentence. That parent key will have a dictionary as
                # its value, where the key for that subdictionary is the 
                # note that contains the sentence and the value is the sentence.
                if wikiLinks[tempList[0]].get(key) is not None:
                    wikiLinks[tempList[0]][key].append(sentence)
                else:
                    wikiLinks[tempList[0]][key] = sentence
    return wikiLinks
    