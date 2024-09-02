import torch
import pandas as pd
from transformers import pipeline
import re
import string
import requests

def create_bibtex_loop(multi_refstrings):

    '''
    Schleife, die create_bibtex mehrfach aufruft, sollten sich mehrere Referenzen in der Eingabe befinden
    
    Parameter:
    multi_refstrings: String, in dem sich eine oder mehrere Referenzen befinden.
    
    return: String mit BibTex Code für jede einzelne Referenz. 
    '''
    # Schleife für mehrfaches Aufrufen des Parsers
    split_refstrings = multi_refstrings.split('\r\n')
    split_refstrings = list(filter(None, split_refstrings))

    multi_outstring = ""

    for element in split_refstrings:
        multi_outstring = multi_outstring + create_bibtex(element) + "\n\n"

    return multi_outstring

def custom_strip(text, replaceCharacter = []):
    
    '''
    Strip-Funktion, die standardmäßig neben Whitespace auch Zeichen aus string.punctuation und die 
    Zeichen “ und ” entfernt.
    
    Parameter:
    text: String, der gestripped werden soll.
    replaceCharacter: Liste von Zeichen, die für den Strip nicht berücksichtigt werden sollen.
    
    return: gestrippter String.
    '''
    
    allowed_chars = string.punctuation + string.whitespace + "“" + "”"
    for character in replaceCharacter:
        allowed_chars = allowed_chars.replace(character, '')
    return text.strip(allowed_chars)


def getIndexOfSubstring(text, regEx = [], reverse = False):
    
    '''
    Prüft für eine Liste von RegEx, ob sie im String namens text vorkommen. Pro RegEx wird nur 
    der erste Match berücksichtigt. Der Match, der den Substring mit der größten Länge ermittelt, kommt zum Zuge. 
    
    Parameter:
    text: Text, wo das Auftreten des RegEx geprüft wird.
    regEx = []: Liste mit RegEx. 
    reverse: Ob das erste oder letzte Auftreten eines Matches geprüft maßgeblich ist. Wenn reverse = False, dann wird das
    erste Auftreten geprüft.
    
    return: Substring und den zugehörigen Start- und Endindex.
    '''
    
    length = 0
    matches = []
    substring = ""
    for regExElement in regEx:
        matches = list(re.finditer(regExElement, text))
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

def getSubstringByRegEx(text, regex = []):
    
    '''
    Prüft für eine Liste von RegEx, ob sie im String namens text vorkommen. Der RegEx, der den Substring mit der grötßen
    Länge ermittelt, kommt zum Zuge. Dieser Substring wird dann aus dem text ausgeschnitten. Ein RegEx wird
    dabei von hinten beginnend in text geprüft und der erste Match zählt.
    
    Parameter:
    text: Literaturstring.
    regEx = []: Liste mit RegEx. 
    
    return: String ohne Substring (changedText) und ausgeschnittenen Substring
    '''
    
    startIndex, endIndex, substring = getIndexOfSubstring(text, regex, True)
    changedText, substring = replaceSubstring(startIndex, endIndex, text, "")
    return changedText, custom_strip(substring)

def replaceSubstring (startIndex, endIndex, text, substituteString, ignorePunctuation = ["&", "(", ")"]):
    
    '''
    Ersetzt in dem String namens text einen Substring durch einen anderen String namens substituteString.
    Die Variablen startIndex und endIndex können dabei noch verändert werden, webb vor der Postion startIndex oder nach der
    Position endIndex bestimmte Zeichen folgen, die mit entfernt werden sollen. Die Existenz dieser bestimmten Zeichen 
    wird mit der Funktion isSpeceficPunctuation geprüft. Mit dem Parameter ignorePunctuation wird auf die Prüfung
    bestimmter Zeichen in der Funktion isSpeceficPunctuation verzichtet.
    
    Parameter:
    startIndex: Index, wo der zu ersetztende Substring im String namens text eingefügt werden soll.
    endIndex: Index, wo der zu ersetztende Substring im String text enden soll.
    text: Text, wo das Auftreten des Substrings geprüft wird.
    substituteString: Der einzufügende Substring.
    ignorePunctuation: Zeichen, die für die Indexverschiebung nicht berücksichtigt werden sollen.
    
    return: Substring und den zugehörigen Start- und Endindex.
    '''
    
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
        if endIndex < len(text):
            for i in range(endIndex-1, len(text), 1):
                if isSpeceficPunctuation(text[i], ignorePunctuation):
                    endIndexReplace = i + 1
                    break
                elif i == len(text)-1:
                    endIndexReplace = len(text)
        else:
            endIndexReplace = len(text)
        if endIndexReplace > 0:
            changedText = text[0:startIndexReplace] + substituteString + text[endIndexReplace:len(text)]
            return changedText, text[startIndexReplace:endIndexReplace]
    return text, ""

def is_SurenameFirst(names):
    
    '''
    Prüft, ob die Autoren- oder Editornamen mit dem Vornamen beginnen. 
    
    Parameter:
    names: Substring vom Literaturstring, der die Autoren- oder Editornamen enthält.
    
    return: True, wenn die Namen mit dem Vornamen beginnen. Ansonsten False.
    '''
    
    splitedNames = names.split(" ")
    #regex wie w+ erkennt bspw. KEIN è 
    if splitedNames[0].endswith("."):
        return True
    splitedNames = names.split(",")
    if all(" " in item.strip() for item in splitedNames):
        return True
    return False
    
def is_NameShortened(df_PER):
    
    '''
    Prüft, ob die Namen mit einem Punkt abgekürzt sind.
    
    Parameter:
    df_Per: Dataframe der durch Named Entity Recognition erkannten dictionaries vom Typ Person.
    
    return: True, falls der Name mit einem Punkt abgekürzt ist. Ansonsten False.
    '''
    
    for index in df_PER.index.values.tolist():
        if "." == text[df_PER["end"].iloc[index]] and len(text[df_PER["start"].iloc[index]:df_PER["end"].iloc[index] + 1]) == 2:
            return True
    return False


def isSpeceficPunctuation(text, replaceCharacter = []):
    
    '''
    Prüft, ob ein Srting nur aus bestimmten Satzzeichen besteht. Standardmäßig wird string.punctuation + string.whitespace
    geprüft.
    
    Parameter:
    text: Text, der geprüft werden soll.
    replaceCharacter = []: Liste von Zeichen, die aus der standardmäßigen Prüfung entfernt werden sollen.
    '''
        
    allowed_chars = string.punctuation + string.whitespace
    for character in replaceCharacter:
        allowed_chars = allowed_chars.replace(character, '')
    return all(char in allowed_chars for char in text)

def is_Editor(editorRegEx, textBetweenNames, startIndexTextBetweenNames, markerBehind = True):
    
    '''
    Prüft, ob in dem String textBetweenNames ein Signalwort für Editoren enthalten ist.
    
    Parameter:
    editorRegEx: RegEx, die Signalwörter für das Auftreten von Editoren erkennen sollen.
    textBetweenNames: Substring vom Literaturstring, der geprüft weden soll, ob das Signalwort enthalten ist. Dieser 
    Substring steht stehts zwischen potententiellen Namen.
    startIndexTextBetweenNames: Startindex, wo Substring im original Literaturstring steht. Signalwörter können dabei nicht
    Bestandteil von einer Namenskette sein, sondern immer nur zwischen solchen Namensketten. Daher der Name des Parameters.
    markerBehind: Ob das Signalwort für Editoren vor oder hinter den Editorennamen im original Literaturstring steht.
    
    return: Boolean, ob gefunden, und Start- und Endindizies, wo es im original Literaturstring vorkommt.
    '''
    
    startSubstring, endSubstring, substring = getIndexOfSubstring(textBetweenNames, [editorRegEx])
    if startIndexTextBetweenNames > -1 and markerBehind:
        if isSpeceficPunctuation(textBetweenNames[startIndexTextBetweenNames:startSubstring], ["&"]):
            ''' Signalwörter, die das Vorliegen von Editoren markieren, werden durch die editorRegEx geprüft.
            Es gilt folgende Heuristik: Ein Signalwort für Editoren, das vor oder hinter den Editorenamen steht, 
            darf nur von bestimmten Satzzeichen/Punkuationen und nicht von Wörtern unterbrochen sein.
            Es kann schließlich zufällig sein, dass ein RegEx ein Editor-Signalwort erkennt, 
            das jedoch eigentlich keins ist, da sie die zuvor genannte Heuristik nicht erfüllen. 
            
            Beispiel: 
            Gegeben sei folgender Ausschnitt eines Literaturstrings: "Bennett, C. H., DiVincenzo, D. P., Eds."
            Das Signalwort "Eds." befindet sich direkt hinter den beiden Autorennamen, da es nur von einem Punkt, Komma und
            einem Leerzeichen (also bestimmten Satzzeichen) unterbrochen ist. Also ist die Heuristik erfüllt.
            
            Dieses Vorgehen gilt für den elif-Teil analog.'''
            return True, startSubstring + startIndexTextBetweenNames, endSubstring + startIndexTextBetweenNames
    elif startIndexTextBetweenNames > -1:
        if isSpeceficPunctuation(textBetweenNames[endSubstring:startIndexTextBetweenNames], ["&"]):
            return True, startSubstring + startIndexTextBetweenNames, endSubstring + startIndexTextBetweenNames
    return False, -1, -1

def processNames(authors):
    
    '''
    Bereitet die Autorennamen in ein Standardformat auf.
    
    Parameter:
    authors: Substring aus dem original Literaturstring, der die Autoren enthält.
    
    return: Standardformat für Autoren.
    '''
    
    finalAuthors = ""
    search_terms = [" and ", ", and ", " & ", ", & "]
    surenameFirst = is_SurenameFirst(authors.strip())
    authors = custom_strip(authors)
    if surenameFirst:
        startIndex, endIndex, andInAuthors = getIndexOfSubstring(authors, search_terms)
        if startIndex >= 0:
            authors = authors.replace(andInAuthors, " and ")
            finalAuthors = authors.replace(", ", " and ")
        else:
            finalAuthors = authors
    elif "., " in authors:
        search_terms = ["., and ", "., & ", ". and ", ". & "]
        andInAuthors = getIndexOfSubstring(authors, search_terms)[2]
        authors = authors.replace("., ", "#., ")
        if andInAuthors != "":
            authors = authors.replace(andInAuthors, "#., ")
        authors = authors.split("., ")
        authors = [name.replace("#",".") for name in authors]
        authors = [name.replace("..",".") for name in authors]
        for author in authors[:-1]:
            buffer = author.split(", ")
            finalAuthors = finalAuthors + buffer[1] + " " + buffer[0] + " and "
        buffer = authors[-1].split(", ")
        finalAuthors = finalAuthors + buffer[1] + " " +  buffer[0]
    elif ", " in authors:
        search_terms = [", and ", ", & ", " and ", " & "]
        andInAuthors = getIndexOfSubstring(authors, search_terms)[2]
        if andInAuthors != "":  
            authors = authors.replace(andInAuthors, ", ")
        authors = authors.split(", ")
        for i in range(0, len(authors) - 3, 2):
            finalAuthors = finalAuthors + authors[i+1] + " " + authors[i] + " and "
        finalAuthors = finalAuthors + authors[len(authors) - 1] + " " + authors[len(authors) - 2]
    return custom_strip(finalAuthors)

def getAuthors(text):
    
    '''
    Schneidet die Autoren aus dem original Literaturstring aus. Es können mehrere Autoren vorliegen und diese
    können mit einem "and" oder "&" verknüpft sein. Die Funktion soll alle Autoren einschließlich dem "and" und "&"
    in einem Block extrahieren. Dieser Block ist sinnbildlich eine Kette von Namen. Die Variable textBetweenNames 
    beinhaltet die Substrings, die zwischen solchen Namensketten stehen. 
    Wenn eine solche Kette von Namen gefunden wird, wird setChainStart = True gesetzt und geprüft, 
    ob es sich auch um Autorennamen handelt.
    
    Beispiel:
    "Nielsen, M. A.; Chuang, I. L. Quantum Computation and Quantum Information. In Handbook of Quantum Information Science;
    Bennett, C. H., DiVincenzo, D. P., Eds.; Quantum Science and Technology; Springer: Berlin, Germany, 2026; Vol. 4, 
    pp 250–300. https://doi.org/10.1007/springerreference-303198."
    
    Da Autoren und Editoren vorliegen, liegen zwei Abschnitte vor, die textBetweenNames sind, nämlich zwischen Index
    28 und 118 sowie zwischen 151 und dem Ende des Strings. Entsprechend liegen zwischen 0 und 27 und 119 bis 150 
    Namensketten vor. Ob Sonderzeichen wie der Punkt zur Abkürzung von Nachnamen mit zum Namen gezählt werden, hängt
    von der NER ab.

    
    Parameter:
    text: Literaturstring.
    
    return: Literaturstring ohne Autoren und die Autoren.
    '''
    
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
                '''Wenn ein Substring, der in textBetweenNames gespeichert wird, nicht nur Satzzeichen oder ein "und" ist, 
                dann ist es nicht Bestandteil einer Namenskette und somit ein echter Substring zwischen Autorenketten. 
                Solch ein Substring heißt im Folgenden "echtes textBetweenNames".
                
                Beispiel: 
                Der Stringteil "Yann LeCun, Léon Bottou, Yoshua Bengio, and Patrick Haffner" ist eine Autorenkette. Der Teil
                ", and" gehört folglich mit zur Autorenkette und ist kein echtes textBetweenNames.
                
                Weil Autoren immer am Anfang des Literaturstrings stehen gilt: Ist ein echtes TextBetweenNames 
                erkannt worden, das direkt hinter der Autorenkette mit Stardindex 0 folgt, so muss vor diesem TextBetweenNames
                eine Namenskette stehen, die die Autoren enthält. Daher setChainStart = True.
                '''    
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
    
    '''
    Schneidet die Editoren aus dem original Literaturstring aus. Es können mehrere Editoren vorliegen und diese
    können mit einem "and" oder "&" verknüpft sein. Die Funktion soll alle Editoren einschließlich dem "and" und "&"
    in einem Block extrahieren. Dieser Block ist sinnbildlich eine Kette von Namen.
    Wenn eine solche Kette von Namen gefunden wird, wird setChainStart = True gesetzt und geprüft, 
    ob es sich auch um Editoren handelt.
    
    Parameter:
    text: Literaturstring.
    
    return: Literaturstring ohne Editoren und die ausgeschnittenen Editoren.
    '''
    
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
            if setChainStart: 
                chainStartIndex = df_PER["start"].iloc[index]
                setChainStart = False
            if not onlyPunctuation and not onlyAnd:
                '''
                Zur Erklärung des Codes siehe analoge Implementierung in getAuthors
                '''
                setChainStart = True
                textFromStartUntilFirstName = text[0:df_PER["start"].iloc[0]]
                isEditor, startIndexEditorMarker, endIndexEditorMarker = is_Editor(editorRegEx, textFromStartUntilFirstName, 0, False)
                if startIndexEditorMarker == -1:
                    isEditor, startIndexEditorMarker, endIndexEditorMarker = is_Editor(editorRegEx, textBetweenNames, df_PER["end"].iloc[index])                         
                if isEditor:
                    startIndexEditors = chainStartIndex
                    endIndexEditors = df_PER["end"].iloc[index]
                    break
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
        for i in range(startIndexEditors-1, -1, -1):
            if isSpeceficPunctuation(changedText[i], [":", " "]):
                startIndexIn = i + 1
                break
        changedText, replacedEditorMarker = replaceSubstring(startIndexIn, startIndexEditors, changedText, ".")
        return changedText, editor
    return text, ""
    
def getPersonTags(text):
    
    '''
    Gibt die durch Named Entity Recognition erkannten dictionaries vom Typ Person in einem Dataframe zurück.
    
    Parameter:
    text: Literaturstring.
    
    return: Dataframe der durch Named Entity Recognition erkannten dictionaries vom Typ Person.
    '''
    
    ner_tagger = pipeline("ner", aggregation_strategy="simple")
    outputs = ner_tagger(text)
    df_outputs = pd.DataFrame(outputs)
    if not df_outputs.empty: 
        return df_outputs[df_outputs["entity_group"] == "PER"].reset_index(drop=True)
    return pd.DataFrame()

def getORGTag(text, score):
    
    '''
    Gibt die durch Named Entity Recognition erkannten dictionaries vom Typ Organization in einem Dataframe zurück.
    Um in das Dataframe aufgenommen zu werden, muss ein bestimmter Score erreicht sein.
    
    Parameter:
    text: Literaturstring.
    score: Schwellenwert zwischen 0 und 1.
    
    return: Dataframe der durch Named Entity Recognition erkannten dictionaries vom Typ Organization.
    '''
    
    ner_tagger = pipeline("ner", aggregation_strategy="simple")
    outputs = ner_tagger(text)
    df_outputs = pd.DataFrame(outputs)
    if not df_outputs.empty:
        return df_outputs[(df_outputs["entity_group"] == "ORG") & (df_outputs["score"] >= score)].reset_index(drop=True).tail(1)
    return pd.DataFrame()

def getLOCTag(text):
    
        
    '''
    Gibt die durch Named Entity Recognition erkannten dictionaries vom Typ Location in einem Dataframe zurück.
    
    Parameter:
    text: Literaturstring.
    
    return: Dataframe der durch Named Entity Recognition erkannten dictionaries vom Typ Location.
    '''
    
    ner_tagger = pipeline("ner", aggregation_strategy="simple")
    outputs = ner_tagger(text)
    df_outputs = pd.DataFrame(outputs)
    if not df_outputs.empty:
        return df_outputs[(df_outputs["entity_group"] == "LOC")].reset_index(drop=True)
    return pd.DataFrame()

def getDoi(text):
    
    '''
    Schneidet die DOI aus dem Literaturstring aus.
    
    Parameter:
    text: Literaturstring.
    
    return: Literaturstring ohne DOI und die ausgeschnittene DOI.
    '''
    
    doiUrlRegEx1 = "https:\/\/doi\.org(\/[^\s]*)?$"
    doiUrlRegEx2 = "(DOI|doi):\s?(https:\/\/doi\.org)?([^\s]*)+$"
    changedText, doi  = getSubstringByRegEx(text, [doiUrlRegEx1, doiUrlRegEx2])
    httpsDomainRegEx1 = "https:\/\/doi\.org\/"
    httpsDomainRegEx2 = "(DOI|doi):\s?(https:\/\/doi\.org\/)?"
    doi, httpsDomain = getSubstringByRegEx(doi, [httpsDomainRegEx1, httpsDomainRegEx2])
    return changedText, custom_strip(doi)

def getURL(text):
        
    '''
    Schneidet die URL aus dem Literaturstring aus.
    
    Parameter:
    text: Literaturstring.
    
    return: Literaturstring ohne URL und die ausgeschnittene URL.
    '''
    
    urlRegEx = "(URL:|url:)?\s*https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?"
    changedText, url = getSubstringByRegEx(text, [urlRegEx])
    urlPrefixRegEx = r"(url:\s*|URL:\s*)"
    url = re.sub(urlPrefixRegEx, '', url).strip()
    return changedText, custom_strip(url)

def getDate(text):
            
    '''
    Schneidet Date aus dem Literaturstring aus.
    
    Parameter:
    text: Literaturstring.
    
    return: Literaturstring ohne Date und ausgeschnittene Date.
    '''
    
    monthYearRegex = "(January|Jan\.?|February|Feb\.?|March|Mar\.?|April|Apr\.?" \
    "|May|May\.?|June|Jun\.?|July|Jul\.?|August|Aug\.?|September|Sep\.?|Sept\.?|October|" \
    "Oct\.?|November|Nov\.?|December|Dec\.?)\s\d{4}"
    changedText, monthYear  = getSubstringByRegEx(text, [monthYearRegex])
    if monthYear == "":
        yearRegEx1 = "(\.|,)? \(\d{4}\)(\.|,|:)"
        yearRegEx2 = "(\.|,) \d{4}(\.|,|;)"
        changedText, year  = getSubstringByRegEx(text, [yearRegEx1, yearRegEx2])
        return changedText, "", f'{year}'
    monthYear = monthYear.split(' ')
    return changedText, f'{monthYear[0]}', f'{monthYear[1]}'

def getPage(text):
                
    '''
    Schneidet Page aus dem Literaturstring aus.
    
    Parameter:
    text: Literaturstring.
    
    return: Literaturstring ohne Page und ausgeschnittene Page.
    '''
    
    pageRegEx = "(?:pp\.? )?\d+(-|--|–)\d+"
    changedText, pages = getSubstringByRegEx(text, [pageRegEx])
    if pages != "":
        pages = re.search(r'\d+(-|--|–)\d+', pages).group()
    return changedText, custom_strip(pages)

def getVolumeNumber(text):
                    
    '''
    Schneidet Volume und Number aus dem Literaturstring aus.
    
    Parameter:
    text: Literaturstring.
    
    return: Literaturstring ohne Volume und Number und ausgeschnittene Volume und Number.
    '''
    
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
        startIndex, endIndex, number = getIndexOfSubstring(changedText, [number1RegEx, number2RegEx, number3RegEx, number4RegEx], True)
        changedText, substring = replaceSubstring(startIndex, endIndex, changedText, "")
        if volume != "":
            volume = re.search(r'\d+', volume).group(0)
        if number != "":
            number = re.search(r'\d+', number).group(0)
        return changedText, volume, number

def getEdition(text):
                        
    '''
    Schneidet Edition aus dem Literaturstring aus.
    
    Parameter:
    text: Literaturstring.
    
    return: Literaturstring ohne Edition und ausgeschnittene Edition.
    '''
    
    editionRegEx1 = "(?:[1-9]\d*th|11th|12th|13th|[1-9]\d*(?:st|nd|rd)) ed\."
    editionRegEx2 = "(?:[1-9]\d*th|11th|12th|13th|[1-9]\d*(?:st|nd|rd)) edn\."
    changedText, edition = getSubstringByRegEx(text, [editionRegEx1, editionRegEx2])
    if edition != "":
        edition = re.search(r'\d+', edition).group()
    return changedText, custom_strip(edition)

def getAddress(text):
                            
    '''
    Schneidet Address aus dem Literaturstring aus.
    
    Parameter:
    text: Literaturstring.
    
    return: Literaturstring ohne Address und ausgeschnittene Address.
    '''
    
    df_LOC = getLOCTag(text)
    addressFound = False
    index_df_Loc_List = df_LOC.index.values.tolist()
    textBetweenAddress = ""
    setChainStart = True
    startIndex = 0
    endIndex = 0
    if not df_LOC.empty:
        for index in reversed(index_df_Loc_List):
            if index < len(index_df_Loc_List) and index > 0:
                textBetweenAddress = text[df_LOC["end"].iloc[index-1]:df_LOC["start"].iloc[index]]
            else:
                textBetweenAddress = text[:df_LOC["start"].iloc[index]]
            onlyPunctuation = isSpeceficPunctuation(textBetweenAddress, [])
            if setChainStart: 
                chainEnIndex = df_LOC["end"].iloc[index]
                setChainStart = False
            if not onlyPunctuation:
                startIndex = df_LOC["start"].iloc[index]
                endIndex = chainEnIndex
                break
        address = text[startIndex:endIndex]
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

def getPublisher(text, doi):
                                
    '''
    Schneidet Publisher aus dem Literaturstring aus.
    
    Parameter:
    text: Literaturstring.
    doi: DOI, um Publisher in externen Datenbanken zu suchen.
    
    return: Literaturstring ohne Publisher und ausgeschnittenen Publisher.
    '''
    
    publisher = ""
    if doi != "":
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            publisher = data['message'].get('publisher', 'Publisher not found')
    if publisher != "":
        startIndex, endIndex, publisher = getIndexOfSubstring(text, [publisher], True)
        if endIndex < len(text) -1:
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
        if endIndex < len(text) -1:
            if isSpeceficPunctuation(text[startIndex - 2]) and isSpeceficPunctuation(text[endIndex + 1]):
                changedText, publisher = replaceSubstring(startIndex, endIndex, text, "")
                return changedText, custom_strip(publisher)
        else:
            if isSpeceficPunctuation(text[startIndex - 2]):
                changedText, publisher = replaceSubstring(startIndex, endIndex, text, "")
                return changedText, custom_strip(publisher)
    return text, ""
    
def getTitel(text):
                                    
    '''
    Schneidet Titel aus dem Literaturstring aus.
    
    Parameter:
    text: Literaturstring.
    
    return: Literaturstring ohne Titel und ausgeschnittenen Titel.
    '''
    
    ignoreCharacters = ["?", "!", "(", ")", "“", "”", "\""]
    text = custom_strip(text, ignoreCharacters)
    ignoreCharacters = ["?", ":", "-", "(", ")", "“", "”", "\""]
    limit = len(text) - 1
    i = 0
    maxIndex = 0
    while i < limit:
        if (i + 2 < limit) and not (text[i] == "," and text[i+1] == " " and not isSpeceficPunctuation(text[i+2])):
            if isSpeceficPunctuation(text[i], ignoreCharacters) and isSpeceficPunctuation(text[i+1], ignoreCharacters):
                text = text[:i] + "." + text[i+2:]
                i = i - 1
                limit = limit - 1
        i = i +1
    
    ignoreCharacters = ["?", "!", "(", ")"]
    if text[0] == "“":
        text = text.rsplit('”', 1)
        return custom_strip(text[0], ignoreCharacters), custom_strip(text[1], ignoreCharacters), ""
    elif text[0] == "\"":
        text = text.rsplit("\"", 1)
        return custom_strip(text[0], ignoreCharacters), custom_strip(text[1], ignoreCharacters), ""
    elif text.count(".") == 1:
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
        text = text.split(",")
        return custom_strip(text[0]), custom_strip(text[1]), ""
    elif maxIndex == 0 and text.count(",") > 1:
        text = text.rsplit(',', 1)
        return custom_strip(text[0]), custom_strip(text[1]), ""
    return custom_strip(text), "", ""
    
    
def getKey(author, year):
                                        
    '''
    Erzeugt einen Key aus dem Nachnamen des ersten Autors und dem Jahr.
    
    Parameter:
    author: Autoren.
    year: Jahr.
    
    return: Erzeugter Schlüssel.
    '''
    
    lastNameFirstAuthor = author.split(" and ")[0].strip().split(" ")[-1]
    return f'{lastNameFirstAuthor}_{year}'


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
    
    text, author = getAuthors(text)
    text, editor = getEditors(text)
    text, doi = getDoi(text)
    text, url = getURL(text)
    text, month, year = getDate(text)
    text, pages = getPage(text)
    text, volume, number = getVolumeNumber(text)
    text, edition = getEdition(text)
    text, address = getAddress(text)
    text, publisher = getPublisher(text, doi)
    school = publisher
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
    inproceedingsFieldsString  = ["author", "title", "booktitle", "year", "editor", "volume", \
                            "number", "series", "pages", "address", "month", "organization", \
                            "publisher", "note", "key", "doi", "url"]
    proceedingsFieldsString  = ["title", "year", "editor", "volume", "number", "series", \
                          "address", "month", "organization", "publisher", "note", "key", "doi", "url"]
    incollectionFieldsString  = ["author", "title", "booktitle", "publisher", "year", "editor", \
                           "volume", "number", "series", "chapter", "pages", "address", \
                           "edition", "month", "note", "key", "doi", "url"]
    articleFieldsString  = ["author", "title", "journal", "year", "volume", "number", \
                      "pages", "month", "note", "key", "doi", "url"]
    phdthesisFieldsString  = ["author", "title", "school", "year", "address", "month", \
                        "note", "key", "doi", "url"]

    model = "LaLaf93/LiteratureTyp_recognizer"
    classifier = pipeline("text-classification", model=model)
    literatureType = classifier(title + "." + booktitle)[0]['label']
    
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
    
    bibTex += '}'

    return bibTex 
