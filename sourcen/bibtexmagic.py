import torch
import pandas as pd
torch.cuda.is_available()
from transformers import pipeline
import re
import string
import spacy


def find_First_Term(text, search_terms):
    # Initialisiere mit einem hohen Wert
    min_index = float('inf')
    end_index = 0
    andTyp = ""
    
    # Suche jeden Suchbegriff in dem Text und behalte den kleinsten Index
    for term in search_terms:
        index = text.find(term)
        if index != -1 and index < min_index:
            min_index = index
            end_index = min_index + len(term) - 1
            andTyp = term
    
    # Wenn min_index unverändert ist, wurde keiner der Begriffe gefunden
    return (min_index, end_index, andTyp) if min_index != float('inf') else (-1, -1, "")

def is_SurenameFirst(names):
    if re.search(r'^(\w+\.)', names) or re.search(r'^(\w+\s\w+(.,)?)+$', names):
        return True
    return False
    
def is_NameShortened(df_PER):
    for index in df_PER.index.values.tolist():
        if "." == text[df_PER["end"].iloc[index]] and len(text[df_PER["start"].iloc[index]:df_PER["end"].iloc[index] + 1]) == 2:
            return True
    return False


def is_punctuation(text, replaceCharacter = []):
    allowed_chars = string.punctuation + ' '
    for character in replaceCharacter:
        allowed_chars = allowed_chars.replace(character, '')
    return all(char in allowed_chars for char in text)

def is_Editor(editorRegEx, textBetweenNames, index):
    if re.search(editorRegEx, textBetweenNames):
        x = re.search(editorRegEx, text)
        #print(f'x: {x.start()}')
        if is_punctuation(text[index:x.start()], ["&"]):
            return True
    return False

def processNames(authors):
    finalAuthors = ""
    search_terms = [" and ", ", and ", " & ", ", & "]
    andInAuthors = find_First_Term(authors, search_terms)[2]
    surenameFirst = is_SurenameFirst(authors)
    #print(f'surenameFirst: {surenameFirst}')
    if surenameFirst:
        #hier völlig egal, ob er einzelne Initialen in ein eigenes Word gesteckt hat, obwohl es noch Nachnamen gib
        authors = authors.replace(andInAuthors, " and ")
        #print(f'authors: {authors}')
        finalAuthors = authors.replace(", ", " and ")
    elif andInAuthors != "":
        if "., " in authors:
            print("Fall ., {0}".format(authors))
            search_terms = ["., and ", "., & ", ". and ", ". & "]
            andInAuthors = find_First_Term(authors, search_terms)[2]
            authors = authors.replace(andInAuthors, "., ")
            authors = authors.split("., ")
            authors = [name + "." for name in authors]
            authors = [name.replace("..",".") for name in authors]
            for author in authors[:-1]:
                buffer = author.split(", ")
                finalAuthors = finalAuthors + buffer[1] + " " + buffer[0] + " and "
            buffer = authors[-1].split(", ")
            finalAuthors = finalAuthors + buffer[1] + " " +  buffer[0]
        elif ", " in authors:
            print("Fall , {0}".format(authors))
            search_terms = [", and ", ", & ", " and ", " & "]
            andInAuthors = find_First_Term(authors, search_terms)[2]
            authors = authors.replace(andInAuthors, ", ")
            authors = authors.split(", ")
            for i in range(0, len(authors) - 3, 2):
                finalAuthors = finalAuthors + authors[i+1] + " " + authors[i] + " and "
            finalAuthors = finalAuthors + authors[len(authors) - 1] + " " + authors[len(authors) - 2]
    else:
        print("Fall else {0}".format(authors))
        authors = authors.split(", ")
        finalAuthros = authors[1] + authors[0]
    return finalAuthors

def getAuthorsAndEditors(df_PER, text):
    search_terms = [" and ", ", and ", " & ", ", & ", "., & ", "., and ", ". and ", ". & "]
    editorRegEx = " (\()?(Eds\.|Eds|Ed|ed|Ed\.|ed\.|eds\.|editor|editors)(\))?"
    index_df_PER_List = df_PER.index.values.tolist()
    onlyPunctuation = False
    onlyAnd = False
    authorsDetected = False
    setChainStart = True
    startIndexAuthors = -1
    endIndexAuthors = -1
    startIndexEditors = -1
    endIndexEditors = -1
    chainStartIndex = -1


    for index in index_df_PER_List:
        #beachte: Hiermit lese ich immer schon vor!
        if index < len(index_df_PER_List) - 1:
            textBetweenNames = text[df_PER["end"].iloc[index]:df_PER["start"].iloc[index + 1]]
        else:
            textBetweenNames = text[df_PER["end"].iloc[index]:]
        onlyPunctuation = is_punctuation(textBetweenNames, ["&"])
        #print(f'getAuthorsAndEditors: textBetweenNames: {textBetweenNames}')
        #print(f'getAuthorsAndEditors: Author: {text[df_PER["start"].iloc[index]:df_PER["end"].iloc[index]]}')
        #print(f'getAuthorsAndEditors: onlyPunctuation: {onlyPunctuation}')
        firstStartIndex, firstEndIndex, andTyp = find_First_Term(textBetweenNames, search_terms)
        onlyAnd = textBetweenNames == andTyp
        #print(f'getAuthorsAndEditors: onlyAnd: {onlyAnd}')
        #print(f'getAuthorsAndEditors: nothing: {not onlyAnd and not onlyPunctuation}')
        if setChainStart: 
            chainStartIndex = df_PER["start"].iloc[index]
            #Solange das auf False, sollen der Substring erweitert werden, also start bleibt konstant
            #print(f'chainStartIndex: {chainStartIndex}')
            setChainStart = False
        #Dann gab es einen Bruch in der Autorenkette. Also bin ich in einer Lücke zwischen den AUtoren
        #Dann ist Nächster Block wieder ein Autor
        if not onlyPunctuation and not onlyAnd:
            setChainStart = True
            #Es können auch nur Editoren und keine Autoren vorkommen
            authorsDetected = not is_Editor(editorRegEx, textBetweenNames, df_PER["end"].iloc[index])
            #print(f'getAuthorsAndEditors: authorsDetected: {authorsDetected}')
            #print(f'getAuthorsAndEditors: is_Editor: {is_Editor(editorRegEx, textBetweenNames, df_PER["end"].iloc[index])}')
            #print(f'getAuthorsAndEditors: chainStartIndex: {chainStartIndex}')
            # endIndexAuthors == -1, damit Autoren im Titel nicht wieder als Autoren erkannt werden
            if authorsDetected and endIndexAuthors == -1:
                startIndexAuthors = chainStartIndex
                endIndexAuthors = df_PER["end"].iloc[index]
            #nicht nur ein else, falls Namen im Titel des Buches auftauchen
            elif is_Editor(editorRegEx, textBetweenNames, df_PER["end"].iloc[index]):
                startIndexEditors = chainStartIndex
                endIndexEditors = df_PER["end"].iloc[index]
                break
    #print(f'getAuthorsAndEditors: return: {[startIndexAuthors,endIndexAuthors],[startIndexEditors, endIndexEditors]}')
    return startIndexAuthors,endIndexAuthors,startIndexEditors, endIndexEditors

def replaceSubstring (startIndex, endIndex, text, substituteString):
    if endIndex > 0:
        startIndexReplace = -1
        endIndexReplace = -1
        changedText = text
        if startIndex > 0:
            for i in range(startIndex - 1, 0, -1):
                if not is_punctuation(text[i], ["&", "(", ")"]):
                    startIndexReplace = i + 1
                    break
        else:
            startIndexReplace = 0
            substituteString = ""
        print(f'startIndexReplace : {startIndexReplace}')
        if endIndex < len(text):
            for i in range(endIndex, len(text), 1):
                if not is_punctuation(text[i], ["&", "(", ")"]):
                    endIndexReplace = i
                    break
        else:
            endIndexReplace = len(text)
        print(f'endIndexReplace : {endIndexReplace}')
        changedText = text[0:startIndexReplace] + substituteString + text[endIndexReplace:len(text)]
        return changedText, text[startIndexReplace:endIndexReplace]
    return text, ""

def getIndexOfSubstring(text, regEx = [], reverse = False):
    for regExElement in regEx:
        print(f'regExElement: {regExElement}')
        print(f'text: {text}')
        matches = list(re.finditer(regExElement, text))
        print(f'matches: {matches}')
        if matches:
            if reverse:
                match = matches[-1]
            else:
                match = matches[0]
            return match.start(), match.end()
    return -1,-1

#search_terms = [", et al.", " et al."]
#firstStartIndex, firstEndIndex, etAl = find_First_Term(text, search_terms)
#if firstStartIndex > -1:
    #text = replaceSubstring(firstStartIndex, firstEndIndex, text, ", ")

def create_bibtex(text):
    ner_tagger = pipeline("ner", aggregation_strategy="simple")
    print(text)
    outputs = ner_tagger(text)
    df_outputs = pd.DataFrame(outputs)
    print(df_outputs)
    #index neu setzen, da diese nicht automatich geupdates werden
    df_PER = df_outputs[df_outputs["entity_group"] == "PER"].reset_index(drop=True)


    print(df_PER)

    doiUrlRegEx = "https:\/\/doi\.org(\/[^\s]*)?$"
    doiUrlRegEx2 = "(DOI|doi):(https:\/\/doi\.org)?([^\s]*)+$"
    editorRegEx = "(\()?(Eds\.|Eds|Ed|ed|Ed\.|ed\.|eds\.|editor|editors)(\))?"
    year1 = "(\(\d{4}\)|\. \d{4}\.)"
    year2 = "(\.|,) \d{4}(\.|,)"


    finalAuthors = ""
    finalEditors = ""
    startIndexAuthors,endIndexAuthors,startIndexEditors, endIndexEditors = getAuthorsAndEditors(df_PER, text)
    if startIndexAuthors > -1:
        text, authors = replaceSubstring(startIndexAuthors, endIndexAuthors, text, "#")
        print(f'text after replace authors : {text}')
        startIndexEditors = startIndexEditors - len(authors)
        endIndexEditors = endIndexEditors - len(authors)
        finalAuthors = processNames(authors)
    else:
        startIndexAuthors, endIndexAuthors = 0, 0

    if startIndexEditors > -1:
        text, editors = replaceSubstring(startIndexEditors, endIndexEditors, text, ".#")
        endIndexEditors = endIndexEditors - len(editors)
        print(f'text after replace editors : {text}')
        print(f'endIndexEditors : {endIndexEditors}')
        #es soll erst ab Editors gesucht werden, daher text[endIndexEditors:]. Sonst Verwechslungsgefahr
        print(f'text[endIndexEditors:] : {text[endIndexEditors:]}')
        startIndexEditorMarker, endIndexEditorMarker = getIndexOfSubstring(text[endIndexEditors:], [editorRegEx])
        print(f'startIndexEditorMarker : {startIndexEditorMarker}')
        print(f'endIndexEditorMarker : {endIndexEditorMarker}')
        startIndexEditorMarker = startIndexEditorMarker + endIndexEditors
        endIndexEditorMarker = endIndexEditorMarker + endIndexEditors
        print(f'startIndexEditorMarker : {startIndexEditorMarker}')
        print(f'endIndexEditorMarker : {endIndexEditorMarker}')
        finalEditors = processNames(editors)
        text, replacedEditorMarker = replaceSubstring(startIndexEditorMarker, endIndexEditorMarker, text, ".#")
        print(f'text after replace EditorMarker : {text}')

    else:
        startIndexEditors, endIndexEditors = 0, 0

    print("")

    startIndex, endIndex = getIndexOfSubstring(text, [doiUrlRegEx, doiUrlRegEx2], True)
    text, finalDoi = replaceSubstring(startIndex, endIndex, text, "#")
    print(f'text after replace DOI: {text}')

    urlRegEx = "https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?"
    startIndex, endIndex = getIndexOfSubstring(text, [urlRegEx], True)
    text, finalURL = replaceSubstring(startIndex, endIndex, text, ".#")
    print(f'text after replace DOI: {text}')

    startIndex, endIndex = getIndexOfSubstring(text, [year1])
    if startIndex < 0:
        startIndex, endIndex = getIndexOfSubstring(text, [year2], True)
    text, finalYear = replaceSubstring(startIndex, endIndex, text, ".#")
    finalYear = re.search(r'\d+', finalYear).group(0) if re.search(r'\d+', finalYear) else ""

    pageFinder = "(?:pp\.? )?\d+(-|–)\d+"

    startIndex, endIndex = getIndexOfSubstring(text, [pageFinder], True)
    text, finalPage = replaceSubstring(startIndex, endIndex, text, ".#")
    finalPage = re.search(r'\d+', finalPage).group(0) if re.search(r'\d+', finalPage) else ""

    print(f'text after replace Page: {text}')

    number1 = " no\. \d+"
    number2 = " Issue \d+"
    number3 = "\d+"

    #Volume, Seite, Number stehen IMMEr nach dem Titel. Also diese von Hinten suchen
    startIndex, endIndex = getIndexOfSubstring(text, [number1, number2, number3], True)
    text, finalNumber = replaceSubstring(startIndex, endIndex, text, ".#")
    finalNumber = re.search(r'\d+', finalNumber).group(0) if re.search(r'\d+', finalNumber) else ""

    print(f'text after replace Number: {text}')

    volume1 = "Vol\. \d+"
    volume2 = "vol\. \d+" 
    volume3 = "\d+"
    edition1 = "(?:[1-9]\d*th|11th|12th|13th|[1-9]\d*(?:st|nd|rd)) ed\."
    edition2 = "(?:[1-9]\d*th|11th|12th|13th|[1-9]\d*(?:st|nd|rd)) edn\."

    startIndex, endIndex = getIndexOfSubstring(text, [volume1, volume2, volume3], True)
    text, finalVolume = replaceSubstring(startIndex, endIndex, text, ".#")
    finalVolume = re.search(r'\d+', finalVolume).group(0) if re.search(r'\d+', finalVolume) else ""

    print(f'text after replace Volume: {text}')

    startIndex, endIndex = getIndexOfSubstring(text, [edition1, edition2], True)
    text, finalEdition = replaceSubstring(startIndex, endIndex, text, ".#")
    finalEdition = re.search(r'\d+', finalEdition).group(0) if re.search(r'\d+', finalEdition) else ""

    print(f'text after replace Edition: {text}')
    text = text.replace('(', '.')
    text = text.replace(')', '.')
    text = re.sub(r'\.{2,}', '.', text)
    text = text.replace('.#', '#')
    text = text.replace('#.', '#')
    print(f'text after replace : {text}')
    textList = [element.strip() for element in text.split('#')]
    #print(textList)
    finalPublisher = ""
    for text in reversed(textList):
        outputs = ner_tagger(text)
        df_outputs = pd.DataFrame(outputs)
        print(df_outputs)
        if not df_outputs.empty and finalPublisher == "":
            df_PER = df_outputs[(df_outputs["entity_group"] == "ORG") & (df_outputs["score"] >= 0.9) & df_outputs["score"].idxmax()].reset_index(drop=True).tail(1)
            print(df_PER)
            if not df_PER.empty:
                startIndex, endIndex = df_PER["start"].iloc[0], df_PER["end"].iloc[0]
                print(df_PER)
                #double Check
                nlp = spacy.load("en_core_web_sm")
                doc = nlp(text)
                for ent in doc.ents:
                    if ent.label_ == "ORG":
                        print(ent.text, ent.start_char, ent.end_char, ent.label_)
                        if ent.start_char >= startIndex and ent.end_char <= endIndex:
                            #nimm kleinste gemeinsame Übereinstimmung
                            startIndex = ent.start_char
                            endIndex = ent.end_char
                    print(ent.text, ent.start_char, ent.end_char, ent.label_)
            text, finalPublisher = replaceSubstring(startIndex, endIndex, text, "#")
            
    return f'authors: {finalAuthors}' + ", \r\n" + f'editors: {finalEditors}' \
+ ", \r\n" + f'doi: {finalDoi}' +  ", \r\n"  +  f'year: {finalYear}' +  ", \r\n"  + f'number : {finalNumber}' \
+  ", \r\n" + f'volume : {finalVolume}' +  ", \r\n"  + f'edition: {finalEdition}' +  ", \r\n"  + f'page: {finalPage}' \
+  ", \r\n"  + f'url: {finalURL}' +  ", \r\n"  + f'publisher: {finalPublisher}'

