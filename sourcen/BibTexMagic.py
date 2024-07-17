import torch
import pandas as pd
torch.cuda.is_available()
from transformers import pipeline
import re
import string
import spacy
import requests

def create_bibtex_loop(multi_refstrings):
    # Schleife für mehrfaches Aufrufen des Parsers
    split_refstrings = multi_refstrings.split('\r\n')
    split_refstrings = list(filter(None, split_refstrings))

    multi_outstring = ""

    for element in split_refstrings:
        multi_outstring = multi_outstring + create_bibtex(element) + "\n\n"

    return multi_outstring

def custom_strip(text, replaceCharacter=[]):
    allowed_chars = string.punctuation + string.whitespace + "“" + "”"
    for character in replaceCharacter:
        allowed_chars = allowed_chars.replace(character, '')
    return text.strip(allowed_chars)


def getIndexOfSubstring(text, regEx=[], reverse=False):
    # if reverse = False then it finds the first occurance of a given regEx.
    # if reverse = True, then it finds the last occurance of a given regEx.
    # beceause the occurance with the max length is taken, it always chooses the regex that covers the most letters
    length = 0
    matches = []
    substring = ""
    # print(f'regEx: {regEx}')
    # print(f'text: {text}')
    for regExElement in regEx:
        matches = list(re.finditer(regExElement, text))
        # print(f'matches: {matches}')
        if matches:
            if reverse:
                match = matches[-1]
            else:
                match = matches[0]
            buffer = match.end() - match.start()
            if buffer > length:
                length = buffer
                startIndex = match.start()
                endIndex = match.end()
                substring = text[match.start():match.end()]
    if substring != "":
        return startIndex, endIndex, substring
    return -1, -1, substring


def is_SurenameFirst(names):
    splitedNames = names.split(" ")
    # print(f'is_SurenameFirst: {splitedNames}')
    # regex wie w+ erkennt bspw. KEIN è
    if splitedNames[0].endswith("."):
        return True
    splitedNames = names.split(",")
    if all(" " in item.strip() for item in splitedNames):
        return True
    return False


def is_NameShortened(df_PER):
    for index in df_PER.index.values.tolist():
        if "." == text[df_PER["end"].iloc[index]] and len(
                text[df_PER["start"].iloc[index]:df_PER["end"].iloc[index] + 1]) == 2:
            return True
    return False


def isSpeceficPunctuation(text, replaceCharacter=[]):
    allowed_chars = string.punctuation + string.whitespace
    for character in replaceCharacter:
        allowed_chars = allowed_chars.replace(character, '')
    return all(char in allowed_chars for char in text)


def is_Editor(editorRegEx, textBetweenNames, startIndexTextBetweenNames, markerBehind=True):
    startSubstring, endSubstring, substring = getIndexOfSubstring(textBetweenNames, [editorRegEx])
    if startIndexTextBetweenNames > -1 and markerBehind:
        if isSpeceficPunctuation(textBetweenNames[startIndexTextBetweenNames:startSubstring], ["&"]):
            return True, startSubstring + startIndexTextBetweenNames, endSubstring + startIndexTextBetweenNames
    elif startIndexTextBetweenNames > -1:
        if isSpeceficPunctuation(textBetweenNames[endSubstring:startIndexTextBetweenNames], ["&"]):
            return True, startSubstring + startIndexTextBetweenNames, endSubstring + startIndexTextBetweenNames
    return False, -1, -1


def processNames(authors):
    finalAuthors = ""
    search_terms = [" and ", ", and ", " & ", ", & "]
    surenameFirst = is_SurenameFirst(authors.strip())
    authors = custom_strip(authors)
    # print(f"processNames: {authors}")
    if surenameFirst:
        startIndex, endIndex, andInAuthors = getIndexOfSubstring(authors, search_terms)
        # print("Fall surenameFirst".format(authors))
        # hier völlig egal, ob er einzelne Initialen in ein eigenes Word gesteckt hat, obwohl es noch Nachnamen gib
        if startIndex >= 0:
            authors = authors.replace(andInAuthors, " and ")
            # print(f'authors: {authors}')
            finalAuthors = authors.replace(", ", " and ")
        else:
            finalAuthors = authors
    elif "., " in authors:
        # print("Fall ., {0}".format(authors))
        search_terms = ["., and ", "., & ", ". and ", ". & "]
        andInAuthors = getIndexOfSubstring(authors, search_terms)[2]
        authors = authors.replace("., ", "#., ")
        if andInAuthors != "":
            authors = authors.replace(andInAuthors, "#., ")
        authors = authors.split("., ")
        authors = [name.replace("#", ".") for name in authors]
        authors = [name.replace("..", ".") for name in authors]
        for author in authors[:-1]:
            buffer = author.split(", ")
            finalAuthors = finalAuthors + buffer[1] + " " + buffer[0] + " and "
        buffer = authors[-1].split(", ")
        finalAuthors = finalAuthors + buffer[1] + " " + buffer[0]
    elif ", " in authors:
        # print("Fall , {0}".format(authors))
        search_terms = [", and ", ", & ", " and ", " & "]
        andInAuthors = getIndexOfSubstring(authors, search_terms)[2]
        if andInAuthors != "":
            authors = authors.replace(andInAuthors, ", ")
        authors = authors.split(", ")
        for i in range(0, len(authors) - 3, 2):
            finalAuthors = finalAuthors + authors[i + 1] + " " + authors[i] + " and "
        finalAuthors = finalAuthors + authors[len(authors) - 1] + " " + authors[len(authors) - 2]
    return custom_strip(finalAuthors)


def getAuthors(text):
    search_terms = [" and ", ", and ", " & ", ", & ", "., & ", "., and ", ". and ", ". & "]

    onlyPunctuation = False
    onlyAnd = False
    authorsDetected = False
    setChainStart = True
    startIndexAuthors = -1
    endIndexAuthors = -1
    chainStartIndex = -1
    changedText = ""

    df_PER = getPersonTags(text)
    index_df_PER_List = df_PER.index.values.tolist()

    if not df_PER.empty and df_PER["start"].iloc[0] == 0:
        for index in index_df_PER_List:
            # beachte: Hiermit lese ich immer schon vor!
            if index < len(index_df_PER_List) - 1:
                textBetweenNames = text[df_PER["end"].iloc[index]:df_PER["start"].iloc[index + 1]]
            else:
                textBetweenNames = text[df_PER["end"].iloc[index]:]
            onlyPunctuation = isSpeceficPunctuation(textBetweenNames, ["&"])
            firstStartIndex, firstEndIndex, andTyp = getIndexOfSubstring(textBetweenNames, search_terms)
            onlyAnd = textBetweenNames == andTyp
            if setChainStart:
                chainStartIndex = df_PER["start"].iloc[index]
                setChainStart = False
            if not onlyPunctuation and not onlyAnd:
                setChainStart = True
                startIndexAuthors = chainStartIndex
                endIndexAuthors = df_PER["end"].iloc[index]
                break
        if startIndexAuthors > -1:
            changedText, author = replaceSubstring(startIndexAuthors, endIndexAuthors, text, ".")
            author = processNames(author)
            return changedText, author
    return text, ""


def getEditors(text):
    search_terms = [" and ", ", and ", " & ", ", & ", "., & ", "., and ", ". and ", ". & "]
    editorRegEx = "\s*(\()?(Eds\.|Eds|Ed|ed|Ed\.|ed\.|eds\.|editor|editors)(\))?\s*"
    onlyPunctuation = False
    onlyAnd = False
    setChainStart = True
    isEditor = False
    startIndexEditors = -1
    endIndexEditors = -1
    chainStartIndex = -1
    startIndexEditorMarker = -1
    endIndexEditorMarker = -1

    df_PER = getPersonTags(text)
    index_df_PER_List = df_PER.index.values.tolist()
    if not df_PER.empty:
        for index in index_df_PER_List:
            if index < len(index_df_PER_List) - 1:
                textBetweenNames = text[df_PER["end"].iloc[index]:df_PER["start"].iloc[index + 1]]
            else:
                textBetweenNames = text[df_PER["end"].iloc[index]:]
            onlyPunctuation = isSpeceficPunctuation(textBetweenNames, ["&"])
            firstStartIndex, firstEndIndex, andTyp = getIndexOfSubstring(textBetweenNames, search_terms)
            onlyAnd = textBetweenNames == andTyp
            # if true, that a new chain of Authors begins. An Author Chain is for example "Name1, Name2 and Name3"
            if setChainStart:
                chainStartIndex = df_PER["start"].iloc[index]
                setChainStart = False
            # If the following if-STatement is true, than the chain has reached an end
            if not onlyPunctuation and not onlyAnd:
                setChainStart = True
                # editors can be the first Part of an literature reference
                textFromStartUntilFirstName = text[0:df_PER["start"].iloc[0]]
                isEditor, startIndexEditorMarker, endIndexEditorMarker = is_Editor(editorRegEx,
                                                                                   textFromStartUntilFirstName, 0,
                                                                                   False)
                # print(f' getEditors, startIndexEditorMarker : {startIndexEditorMarker}')
                if startIndexEditorMarker == -1:
                    isEditor, startIndexEditorMarker, endIndexEditorMarker = is_Editor(editorRegEx, textBetweenNames,
                                                                                       df_PER["end"].iloc[index])
                    # print(f' getEditors, startIndexEditorMarker : {startIndexEditorMarker}')
                if isEditor:
                    startIndexEditors = chainStartIndex
                    endIndexEditors = df_PER["end"].iloc[index]
                    break
    # print(f'getAuthorsAndEditors: return: {[startIndexAuthors,endIndexAuthors],[startIndexEditors, endIndexEditors]}')
    if startIndexEditors > -1:
        changedText, editor = replaceSubstring(startIndexEditors, endIndexEditors, text, ".")
        editor = processNames(editor)
        if startIndexEditorMarker > -1:
            if startIndexEditorMarker > startIndexEditors:
                startIndexEditorMarker = startIndexEditorMarker - (len(text) - len(changedText))
                endIndexEditorMarker = endIndexEditorMarker - (len(text) - len(changedText))
            changedText, buffer = replaceSubstring(startIndexEditorMarker, endIndexEditorMarker, changedText, ".")
        startIndexIn = 0
        if startIndexEditorMarker < startIndexEditors:
            startIndexEditors = startIndexEditors - (endIndexEditorMarker - startIndexEditorMarker)
            endIndexEditors = endIndexEditors - (endIndexEditorMarker - startIndexEditorMarker)
        for i in range(startIndexEditors - 1, -1, -1):
            if isSpeceficPunctuation(changedText[i], [":", " "]):
                startIndexIn = i + 1
                break
        # print(f' getEditors, startIndexIn : {startIndexIn}')
        # print(f' getEditors, startIndexEditors : {startIndexEditors}')
        changedText, replacedEditorMarker = replaceSubstring(startIndexIn, startIndexEditors, changedText, ".")
        return changedText, editor
    return text, ""


def getPublisher(text, doi):
    publisher = ""
    if doi != "":
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            publisher = data['message'].get('publisher', 'Publisher not found')
    if publisher != "":
        startIndex, endIndex, publisher = getIndexOfSubstring(text, [publisher], True)
        # double check
        if endIndex < len(text) - 1:
            if isSpeceficPunctuation(text[startIndex - 2]) and isSpeceficPunctuation(text[endIndex + 1]):
                changedText, publisher = replaceSubstring(startIndex, endIndex, text, "")
                return changedText, custom_strip(publisher)
        else:
            if isSpeceficPunctuation(text[startIndex - 2]):
                changedText, publisher = replaceSubstring(startIndex, endIndex, text, "")
                return changedText, publisher
        changedText, publisher = replaceSubstring(startIndex, endIndex, text, "")
        if publisher != "":
            return changedText, custom_strip(publisher)
    df_ORG = getORGTag(text, 0.8)
    if not df_ORG.empty:
        startIndex = df_ORG["start"].iloc[0]
        endIndex = df_ORG["end"].iloc[0]
        publisher = text[startIndex:endIndex]
        # If the range determined by the tagger corresponds to a string
        # that is only delimited by punctuation before and after, then it is most likely a publisher.
        # startIndex - 2 because of a space inbetween
        if endIndex < len(text) - 1:
            if isSpeceficPunctuation(text[startIndex - 2]) and isSpeceficPunctuation(text[endIndex + 1]):
                changedText, publisher = replaceSubstring(startIndex, endIndex, text, "")
                return changedText, custom_strip(publisher)
        else:
            if isSpeceficPunctuation(text[startIndex - 2]):
                changedText, publisher = replaceSubstring(startIndex, endIndex, text, "")
                return changedText, custom_strip(publisher)
    return text, ""


def replaceSubstring(startIndex, endIndex, text, substituteString, ignorePunctuation=["&", "(", ")"]):
    # The regex also checks for punctuation so that it is particularly precise.
    # The cut text however should in normale mode be without the front delimiter of the bibTex fields in the bibiography,
    # so that future regex are not affected. But the last delimiter belongs to the cut word so this should be removed
    if endIndex > 0:
        startIndexReplace = 0
        endIndexReplace = 0
        if startIndex > 0:
            for i in range(startIndex, -1, -1):
                if isSpeceficPunctuation(text[i], ignorePunctuation):
                    startIndexReplace = i + 1
                    break
        else:
            startIndexReplace = 0
            # print(f' replaceSubstring, startIndexReplace={{{startIndexReplace}}}')
        if endIndex < len(text):
            for i in range(endIndex - 1, len(text), 1):
                if isSpeceficPunctuation(text[i], ignorePunctuation):
                    endIndexReplace = i + 1
                    break
                elif i == len(text) - 1:
                    endIndexReplace = len(text)
        else:
            endIndexReplace = len(text)
        # print(f' replaceSubstring, endIndexReplace={{{endIndexReplace}}}')
        if endIndexReplace > 0:
            changedText = text[0:startIndexReplace] + substituteString + text[endIndexReplace:len(text)]
            return changedText, text[startIndexReplace:endIndexReplace]
    return text, ""


def getAddress(text):
    df_LOC = getLOCTag(text)
    # print(f' df_LOC, df_LOC={{{df_LOC}}}')
    addressFound = False
    index_df_Loc_List = df_LOC.index.values.tolist()
    textBetweenAddress = ""
    setChainStart = True
    startIndex = 0
    endIndex = 0
    if not df_LOC.empty:
        for index in reversed(index_df_Loc_List):
            if index < len(index_df_Loc_List) and index > 0:
                textBetweenAddress = text[df_LOC["end"].iloc[index - 1]:df_LOC["start"].iloc[index]]
            else:
                textBetweenAddress = text[:df_LOC["start"].iloc[index]]
            onlyPunctuation = isSpeceficPunctuation(textBetweenAddress, [])
            # wenn true, dann beginnt eine neue Autorenkette
            if setChainStart:
                chainEnIndex = df_LOC["end"].iloc[index]
                # Solange das auf False, sollen der Substring erweitert werden, also start bleibt konstant
                setChainStart = False
            # Dann ist die Addressenkette zu Ende
            if not onlyPunctuation:
                startIndex = df_LOC["start"].iloc[index]
                endIndex = chainEnIndex
                break
        address = text[startIndex:endIndex]
        # If the chained range determined by the tagger corresponds to a string
        # that is only delimited by punctuation before and after, then it is most likely a publisher.
        # startIndex - 2 because of a space inbetween
        # print(f' getAddress, text={{{text}}}')
        if startIndex > 2 and endIndex < len(text) - 1:
            if isSpeceficPunctuation(text[startIndex - 2]) and isSpeceficPunctuation(text[endIndex + 1]):
                addressFound = True
        else:
            if isSpeceficPunctuation(text[startIndex - 2]):
                addressFound = True
        if addressFound:
            changedText, address = replaceSubstring(startIndex, endIndex, text, "")
            return changedText, custom_strip(address)
    return text, ""


def getDate(text):
    monthYearRegex = "(January|Jan\.?|February|Feb\.?|March|Mar\.?|April|Apr\.?" \
                     "|May|May\.?|June|Jun\.?|July|Jul\.?|August|Aug\.?|September|Sep\.?|Sept\.?|October|" \
                     "Oct\.?|November|Nov\.?|December|Dec\.?)\s\d{4}"
    changedText, monthYear = getSubstringByRegEx(text, [monthYearRegex])
    # print(f' getDate, text={{{text}}}')
    if monthYear == "":
        yearRegEx1 = "(\.|,)? \(\d{4}\)(\.|,|:)"
        yearRegEx2 = "(\.|,) \d{4}(\.|,|;)"
        changedText, year = getSubstringByRegEx(text, [yearRegEx1, yearRegEx2])
        # print(f' getDate, changedText={{{changedText}}}')
        return changedText, "", f'{year}'
    monthYear = monthYear.split(' ')
    return changedText, f'{monthYear[0]}', f'{monthYear[1]}'


def getTitel(text):
    # print(f' getTitel 1, text={{{text}}}')
    ignoreCharacters = ["?", "!", "(", ")", "“", "”", "\""]
    text = custom_strip(text, ignoreCharacters)
    ignoreCharacters = ["?", ":", "-", "(", ")", "“", "”", "\""]
    limit = len(text) - 1
    i = 0
    maxIndex = 0
    # remove pairs of punctuation marks
    while i < limit:
        if (i + 2 < limit) and not (text[i] == "," and text[i + 1] == " " and not isSpeceficPunctuation(text[i + 2])):
            if isSpeceficPunctuation(text[i], ignoreCharacters) and isSpeceficPunctuation(text[i + 1],
                                                                                          ignoreCharacters):
                text = text[:i] + "." + text[i + 2:]
                i = i - 1
                limit = limit - 1
        i = i + 1

    # print(f' getTitel 2, text={{{text}}}')
    ignoreCharacters = ["?", "!", "(", ")"]
    if text[0] == "“":
        text = text.rsplit('”', 1)
        return custom_strip(text[0], ignoreCharacters), custom_strip(text[1], ignoreCharacters), ""
    elif text[0] == "\"":
        text = text.rsplit("\"", 1)
        return custom_strip(text[0], ignoreCharacters), custom_strip(text[1], ignoreCharacters), ""
    elif text.count(".") == 1:
        # print(f' getTitel 3, text={{{text}}}')
        text = text.split(".")
        return custom_strip(text[0]), custom_strip(text[1]), ""
    elif text.count(".") == 2:
        text = text.split(".")
        return custom_strip(text[0]), custom_strip(text[1]), custom_strip(text[2])
    else:
        for index, element in enumerate(text):
            if isSpeceficPunctuation(element, [".", ",", " ", "(", ")", ":"]):
                if maxIndex < index:
                    maxIndex = index
        if maxIndex > 0:
            text = text.split(text[maxIndex])
            return custom_strip(text[0]), custom_strip(text[1]), ""
    if maxIndex == 0 and text.count(",") == 1:
        # print(f' getTitel 4, text={{{text}}}')
        text = text.split(",")
        return custom_strip(text[0]), custom_strip(text[1]), ""
    elif maxIndex == 0 and text.count(",") > 1:
        text = text.rsplit(',', 1)
        return custom_strip(text[0]), custom_strip(text[1]), ""
    return custom_strip(text), "", ""


def getPersonTags(text):
    ner_tagger = pipeline("ner", aggregation_strategy="simple")
    outputs = ner_tagger(text)
    df_outputs = pd.DataFrame(outputs)
    if not df_outputs.empty:
        return df_outputs[df_outputs["entity_group"] == "PER"].reset_index(drop=True)
    return pd.DataFrame()


def getORGTag(text, score):
    ner_tagger = pipeline("ner", aggregation_strategy="simple")
    outputs = ner_tagger(text)
    df_outputs = pd.DataFrame(outputs)
    if not df_outputs.empty:
        return df_outputs[(df_outputs["entity_group"] == "ORG") & (df_outputs["score"] >= score)].reset_index(
            drop=True).tail(1)
    return pd.DataFrame()


def getLOCTag(text):
    ner_tagger = pipeline("ner", aggregation_strategy="simple")
    outputs = ner_tagger(text)
    df_outputs = pd.DataFrame(outputs)
    if not df_outputs.empty:
        return df_outputs[(df_outputs["entity_group"] == "LOC")].reset_index(drop=True)
    return pd.DataFrame()


def getDoi(text):
    doiUrlRegEx1 = "https:\/\/doi\.org(\/[^\s]*)?$"
    doiUrlRegEx2 = "(DOI|doi):\s?(https:\/\/doi\.org)?([^\s]*)+$"
    text, doi = getSubstringByRegEx(text, [doiUrlRegEx1, doiUrlRegEx2])
    httpsDomainRegEx1 = "https:\/\/doi\.org\/"
    httpsDomainRegEx2 = "(DOI|doi):\s?(https:\/\/doi\.org\/)?"
    doi, httpsDomain = getSubstringByRegEx(doi, [httpsDomainRegEx1, httpsDomainRegEx2])
    return text, custom_strip(doi)


def getKey(author, year):
    lastNameFirstAuthor = author.split(" and ")[0].strip().split(" ")[-1]
    return f'{lastNameFirstAuthor}_{year}'


def getSubstringByRegEx(text, regex=[]):
    startIndex, endIndex, substring = getIndexOfSubstring(text, regex, True)
    # print(f' getSubstringByRegEx, startIndex={{{startIndex}}}')
    # print(f' getSubstringByRegEx, startIndex={{{endIndex}}}')
    # print(f' getSubstringByRegEx, text={{{substring}}}')
    changedText, substring = replaceSubstring(startIndex, endIndex, text, "")
    # print(f' getSubstringByRegEx, changedText={{{changedText}}}')
    return changedText, custom_strip(substring)


def getVolumeNumber(text):
    volumeAndNumberRegex = "(\d+\(\d+\)|\d+\.\d+)"
    startIndex, endIndex, substring = getIndexOfSubstring(text, [volumeAndNumberRegex], True)
    if startIndex > -1:
        changedText, volumeNumber = replaceSubstring(startIndex, endIndex, text, "")
        startIndex, endIndex, volume = getIndexOfSubstring(volumeNumber, ["\d+"])
        startIndex, endIndex, number = getIndexOfSubstring(volumeNumber, ["\d+"], True)
        return changedText, volume, number
    else:
        volumeRegEx = "(V|v)ol\. \d+"
        volumeRegEx2 = ", \d+,"
        volumeRegEx3 = ",? \d+(:|\.)"
        number1RegEx = "no\. \d+"
        number2RegEx = "Issue \d+"
        number3RegEx = ", \d+,"
        number4RegEx = "\.\d+"
        startIndex, endIndex, volume = getIndexOfSubstring(text, [volumeRegEx, volumeRegEx2, volumeRegEx3], True)
        changedText, substring = replaceSubstring(startIndex, endIndex, text, "")
        # print(f' getVolumeNumber, changedText={{{changedText}}}')
        startIndex, endIndex, number = getIndexOfSubstring(changedText,
                                                           [number1RegEx, number2RegEx, number3RegEx, number4RegEx],
                                                           True)
        changedText, substring = replaceSubstring(startIndex, endIndex, changedText, "")
        if volume != "":
            volume = re.search(r'\d+', volume).group(0)
        if number != "":
            number = re.search(r'\d+', number).group(0)
        return changedText, volume, number


# search_terms = [", et al.", " et al."]
# firstStartIndex, firstEndIndex, etAl = find_First_Term(text, search_terms)
# if firstStartIndex > -1:
# text = replaceSubstring(firstStartIndex, firstEndIndex, text, ", ")

def create_bibtex(text):
    address = ""
    author = ""
    booktitle = ""
    chapter = ""
    doi = ""
    edition = ""
    editor = ""
    howpublished = ""
    isbn = ""
    journal = ""
    key = ""
    month = ""
    note = ""
    number = ""
    organization = ""
    pages = ""
    publisher = ""
    school = ""
    series = ""
    title = ""
    url = ""
    volume = ""
    year = ""
    key = ""
    isBook = False
    isProceedings = False
    isInProceedings = False
    isIncollection = False
    isArticle = False

    urlRegEx = "(URL:|url:)?\s*https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?"
    pageRegEx = "(?:pp\.? )?\d+(-|–)\d+"
    edition1 = "(?:[1-9]\d*th|11th|12th|13th|[1-9]\d*(?:st|nd|rd)) ed\."
    edition2 = "(?:[1-9]\d*th|11th|12th|13th|[1-9]\d*(?:st|nd|rd)) edn\."

    text, author = getAuthors(text)
    text, editor = getEditors(text)
    # print(f' main, text={{{text}}}')
    text, doi = getDoi(text)
    text, url = getSubstringByRegEx(text, [urlRegEx])
    text, month, year = getDate(text)
    # print(f' main 2, text={{{text}}}')
    text, pages = getSubstringByRegEx(text, [pageRegEx])
    if pages != "":
        pages = re.search(r'\d+(-|–)\d+', pages).group()
    # print(f' main 3, text={{{text}}}')
    text, volume, number = getVolumeNumber(text)
    text, edition = getSubstringByRegEx(text, [edition1, edition2])
    if edition != "":
        edition = re.search(r'\d+', edition).group()
    # BUGFIX: Wenn nur num vorkommt, dann schneidet volume die Zahl von num aus!!!!!!
    # volume3 darf also erst geprüft werden, wenn num1 und num2 geprüft wurden.
    # VOlumer erscheint aber immre vor number
    # print(f' main, text2={{{text}}}')
    text, address = getAddress(text)
    text, publisher = getPublisher(text, doi)
    school = publisher
    # print(f' main 4, text={{{text}}}')
    title, booktitle, series = getTitel(text)
    journal = booktitle
    if author != "":
        key = getKey(author, year)
    else:
        key = getKey(editor, year)

    bookFields = [author, title, publisher, year, volume, number, \
                  series, address, edition, month, note, key, editor, \
                  howpublished, organization, chapter, pages, isbn, url]
    inproceedingsFields = [author, title, booktitle, year, editor, volume, \
                           number, series, pages, address, month, organization, \
                           publisher, note, key, doi, url]
    proceedingsFields = [title, year, editor, volume, number, series, \
                         address, month, organization, publisher, note, key, doi, url]
    incollectionFields = [author, title, booktitle, publisher, year, editor, \
                          volume, number, series, chapter, pages, address, \
                          edition, month, note, key, doi, url]
    articleFields = [author, title, journal, year, volume, number, \
                     pages, month, note, key, doi, url]
    phdthesisFields = [author, title, publisher, year, address, month, \
                       note, key, doi, url]

    bookFieldsString = ["author", "title", "publisher", "year", "volume", "number", \
                        "series", "address", "edition", "month", "note", "key", "editor", \
                        "howpublished", "organization", "chapter", "pages", "isbn", "url"]
    inproceedingsFieldsString = ["author", "title", "booktitle", "year", "editor", "volume", \
                                 "number", "series", "pages", "address", "month", "organization", \
                                 "publisher", "note", "key", "doi", "url"]
    proceedingsFieldsString = ["title", "year", "editor", "volume", "number", "series", \
                               "address", "month", "organization", "publisher", "note", "key", "doi", "url"]
    incollectionFieldsString = ["author", "title", "booktitle", "publisher", "year", "editor", \
                                "volume", "number", "series", "chapter", "pages", "address", \
                                "edition", "month", "note", "key", "doi", "url"]
    articleFieldsString = ["author", "title", "journal", "year", "volume", "number", \
                           "pages", "month", "note", "key", "doi", "url"]
    phdthesisFieldsString = ["author", "title", "school", "year", "address", "month", \
                             "note", "key", "doi", "url"]

    models = [
        "LaLaf93/proceedings_recognizer",
        "LaLaf93/inproceedings_recognizer",
        "LaLaf93/book_recognizer",
        "LaLaf93/incollection_recognizer",
        "LaLaf93/article_recognizer",
        "LaLaf93/phdthesis_recognizer"
    ]

    labels = [
        "proceedings",
        "inproceedings",
        "book",
        "incollection",
        "article",
        "phdthesis"
    ]

    classifierDict = {}

    for model, label in zip(models, labels):
        result = pipeline("text-classification", model=model)(text)[0]
        classifierDict[label] = result

    # print(f'classifierDict: {classifierDict}')
    literatureType = ""
    highestScore = 0
    highetsScoreLabel = ""
    for entry in classifierDict.values():
        if entry['score'] > highestScore and not entry['label'].startswith('NON'):
            highestScore = entry['score']
            highetsScoreLabel = entry['label']
    literatureType = highetsScoreLabel
    # print(literatureType)
    if literatureType == "":
        for entry in classifierDict.values():
            lowestScore = 1
            lowestScoreLabel = ""
            if entry['score'] < lowestScore and entry['label'].startswith('NON'):
                lowestScore = entry['score']
                lowestScoreLabel = entry['label'].replace('NON', '')
        literatureType = lowestScoreLabel

    bibTex = "@"
    if literatureType == "book":
        zippedFieldsValues = zip(bookFieldsString, bookFields)
        zippedList = list(zippedFieldsValues)
        bibTex += f"book{{{key}, \n"
        for field in zippedList:
            bibTex += f'{field[0]}={{{field[1]}}},\n'
    elif literatureType == "proceedings":
        zippedFieldsValues = zip(proceedingsFieldsString, proceedingsFields)
        zippedList = list(zippedFieldsValues)
        bibTex += f"proceedings{{{key}, \n"
        for field in zippedList:
            bibTex += f'{field[0]}={{{field[1]}}},\n'
    elif literatureType == "inproceedings":
        zippedFieldsValues = zip(inproceedingsFieldsString, inproceedingsFields)
        zippedList = list(zippedFieldsValues)
        bibTex += f"inproceedings{{{key}, \n"
        for field in zippedList:
            bibTex += f'{field[0]}={{{field[1]}}},\n'
    elif literatureType == "incollection":
        zippedFieldsValues = zip(incollectionFieldsString, incollectionFields)
        zippedList = list(zippedFieldsValues)
        bibTex += f"incollection{{{key}, \n"
        for field in zippedList:
            bibTex += f'{field[0]}={{{field[1]}}},\n'
    elif literatureType == "article":
        zippedFieldsValues = zip(articleFieldsString, articleFields)
        zippedList = list(zippedFieldsValues)
        bibTex += f"article{{{key}, \n"
        for field in zippedList:
            bibTex += f'{field[0]}={{{field[1]}}},\n'
    else:
        zippedFieldsValues = zip(phdthesisFieldsString, phdthesisFields)
        zippedList = list(zippedFieldsValues)
        bibTex += f"phdthesis{{{key}, \n"
        for field in zippedList:
            bibTex += f'{field[0]}={{{field[1]}}},\n'

            # Idee: Mit Pos-Tagging herausfinden, wo Nomen etc. vorkommen und dann titel und Booktitel eingrenzen
    bibTex += '}'

    return bibTex
