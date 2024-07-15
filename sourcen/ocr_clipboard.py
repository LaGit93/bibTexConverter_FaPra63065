from PIL import ImageGrab
import pytesseract
from io import BytesIO
import re
import pandas as pd


def language_codes():
    # Liste mit den 30 häufigsten Sprachen in deutscher Abkürzung
    language_codes_de = [
        'eng', 'afr', 'ara', 'ben', 'bul', 'cat', 'ces', 'chi_sim', 'chi_tra', 'chr', 'dan',
        'deu', 'ell', 'enm', 'epo', 'equ', 'est', 'eus', 'fin', 'fra',
        'frk', 'frm', 'glg', 'grc', 'heb', 'hin', 'hrv', 'hun', 'ind', 'isl',
        'ita', 'ita_old', 'jpn', 'kan', 'kor', 'lav', 'lit', 'mal', 'mkd', 'mlt',
        'msa', 'nld', 'nor', 'pol', 'por', 'ron', 'rus', 'slk', 'slv', 'spa',
        'sqi', 'srp', 'swe', 'tam', 'tel', 'tgl', 'tha', 'tur', 'ukr', 'vie'
    ]

    return language_codes_de


def language_names():
    # Deutsche Namen der Sprachen
    language_names_de = [
        'Englisch', 'Afrikaans', 'Arabisch', 'Bengalisch', 'Bulgarisch', 'Katalanisch', 'Tschechisch',
        'Chinesisch (vereinfacht)', 'Chinesisch (traditionell)', 'Cherokee', 'Dänisch',
        'Deutsch', 'Griechisch', 'Englisch (Mittelalter)', 'Esperanto', 'Mathematik / Gleichung', 'Estnisch',
        'Baskisch', 'Finnisch', 'Französisch',
        'Fränkisch', 'Französisch (Mittelalter)', 'Galicisch', 'Altgriechisch', 'Hebräisch', 'Hindi', 'Kroatisch',
        'Ungarisch', 'Indonesisch', 'Isländisch',
        'Italienisch', 'Italienisch (Alt)', 'Japanisch', 'Kannada', 'Koreanisch', 'Lettisch', 'Litauisch', 'Malayalam',
        'Mazedonisch', 'Maltesisch',
        'Malaiisch', 'Niederländisch', 'Norwegisch', 'Polnisch', 'Portugiesisch', 'Rumänisch', 'Russisch', 'Slowakisch',
        'Slowenisch', 'Spanisch',
        'Albanisch', 'Serbisch (Lateinisch)', 'Schwedisch', 'Tamilisch', 'Telugu', 'Tagalog', 'Thailändisch',
        'Türkisch', 'Ukrainisch', 'Vietnamesisch'
    ]

    # Englische Namen der Sprachen
    language_names_en = [
        'English', 'Afrikaans', 'Arabic', 'Bengali', 'Bulgarian', 'Catalan', 'Czech', 'Chinese (Simplified)',
        'Chinese (Traditional)', 'Cherokee', 'Danish',
        'German', 'Greek', 'Middle English', 'Esperanto', 'Math / Equation', 'Estonian', 'Basque', 'Finnish', 'French',
        'Frankish', 'Middle French', 'Galician', 'Ancient Greek', 'Hebrew', 'Hindi', 'Croatian', 'Hungarian',
        'Indonesian', 'Icelandic',
        'Italian', 'Old Italian', 'Japanese', 'Kannada', 'Korean', 'Latvian', 'Lithuanian', 'Malayalam', 'Macedonian',
        'Maltese',
        'Malay', 'Dutch', 'Norwegian', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Slovak', 'Slovenian', 'Spanish',
        'Albanian', 'Serbian (Latin)', 'Swedish', 'Tamil', 'Telugu', 'Tagalog', 'Thai', 'Turkish', 'Ukrainian',
        'Vietnamese'
    ]
    # Falls die Auswahl der Sprache auf Deutsch umgestellt werden soll:
    # return_language_names_de
    return language_names_en


def lang_name2code(lang_name):
    # Umwandlung der Sprachauswahl in Language Code

    spalten = ['Language Name', 'Language Code']
    lang_names_en = language_names()
    lang_codes = language_codes()

    df = pd.DataFrame(list(zip(lang_names_en, lang_codes)), columns=spalten)
    language = df.loc[df['Language Name'] == lang_name, 'Language Code'].values[0]

    return language


def remove_enumeration(text):
    # Entfernt Aufzählungen aus String
    #
    lines = text.split('\n')
    result = []
    for line in lines:
        # Entfernt führende Zahlen mit Punkt oder eckigen Klammern und Leerzeichen
        cleaned_line = re.sub(r'^\s*\d+\.\s*|\[\d+\]\s*', '', line)

        # Entfernt Leerzeichen am Anfang und Ende der Zeile
        cleaned_line = cleaned_line.strip()

        result.append(cleaned_line)
    result = list(filter(None, result))
    return '\n\n'.join(result)


def newocr(selected_language):
    # DataFrame aus Language_Code und Language_Name erstellen
    df_languages = pd.DataFrame(list(zip(language_codes(), language_names())),
                                columns=['Language Code', 'Language Name'])

    # Inhalt der Zwwischenablage als Bild importieren
    img = ImageGrab.grabclipboard()

    # language wird benötigt, um Sonderzeichen aus verschiedenen europäischen Sprachen gut zu erkennen
    language = df_languages.loc[df_languages['Language Name'] == selected_language, 'Language Code'].values[0]

    # Prüfen, ob sich ein Screenshot in der Zwischenablage befindet
    try:
        converted_text = pytesseract.image_to_string(img, lang=language)
        if converted_text == "":
            converted_text = "No text in screenshot recognized"
    except:
        converted_text = "No valid image in clipboard"

    # Mögliche Spliteinstellungen
    split = {'Bibliographie_style': ['Aufzählung durch Ordinalzahlen', 'Aufzählung durch geklammerte Zahlen',
                                     'Keine Aufzählungszeichen']}
    df_split = pd.DataFrame(data=split)

    # Wahl der Aufzählungsmethode, CS: es wird standardmäßig ohne Aufzählung gesplittet und nachträglich die Aufzählungen entfernt
    Methode = df_split["Bibliographie_style"][2]

    if Methode == 'Aufzählung durch Ordinalzahlen':
        # Splitte den String nach der Zeichenkombination "\n\n. "
        split_text = converted_text.split("\n\n. ")

        # Entferne die Zeichenkombination ". " beim ersten Element
        if split_text:
            split_text[0] = split_text[0].replace(". ", "", 1)

        # Entferne Zeilenumbrüche in allen Strings der Liste
        split_text = [s.replace('\n', '') for s in split_text]

    if Methode == 'Aufzählung durch geklammerte Zahlen':
        # Splitte den String an Stellen, wo [Zahl] vorkommt
        split_text = re.split(r'\s*\[\d+\]\s*', converted_text)

        # Entferne führende und nachfolgende Leerzeichen von jedem Element in der Liste
        split_text = [s.strip() for s in split_text]

        # Entferne Zeilenumbrüche in allen Strings der Liste
        split_text = [s.replace('\n', '') for s in split_text]

    if Methode == 'Keine Aufzählungszeichen':
        # Splitte den String nach der Zeichenkombination "\n\n. "
        split_text = converted_text.split("\n\n")

        # Entferne Zeilenumbrüche in allen Strings der Liste
        split_text = [s.replace('\n', '') for s in split_text]

    # Umwandeln der Liste in einen String
    multi_outstring = ""
    for element in split_text:
        multi_outstring = multi_outstring + element + "\n\n"

    # Alle Aufzählungszeichen werden entfernt
    multi_outstring = remove_enumeration(multi_outstring)

    return multi_outstring


