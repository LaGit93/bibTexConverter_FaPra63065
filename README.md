# BibTexConverter

---

## Kurzbeschreibung
Der BibTexConverter dient zur Übersetzung von Literaturverzeichnis-Einträgen in BibTex-Einträge, die in Folge für die Erstellung von Literaturverzeichnissen in eigenene Dokumenten verwendet werden können. Dem BibTexConverter können die zu konvertierenden Einträge über das Clipboard sowohl in Textform, als auch in Bildform (z.B. Ausschnitt aus einem Screenshot) als Eingabe zur Verfügung gestellt werden. 

---

## Lösungsbeschreibung
Der Konverter muss dabei die Informationen aus Literaturverzeichniseinträgen in einzelne Bestandteile zerlegen und den Attributen der BibTex-Struktur zuordnen können. Dazu sollte er möglichst viele der verwendeten Formate und Formatvarianten erkennen können. Im Fall von als Bildaten angegebenen Literaturverzeichnis-Komponenten ist die Erkennung des Textes in Images (OCR) zur Vorverarbeitung, um sie dann entsprechend weiter verarbeiten zu können. Der grobe Ablauf der Logik ist damit:

1. Texterkennung (OCR) - falls Bilddaten verwendet werden
2. Erkennung der Art des Eintrages (Buch, Artikel, Webseite, ...)
3. Extraktion der BibTex-Attribute aus dem Text des Literaturverzeichnis-Eintrags
4. Nachbereitung und Überführung des Ergebnisses in das BibTex-Format

Die Schritte (insbesondere Schritt 2-4) können dabei je nach gewählter Lösung zusammengefasst werden. Es ist auch denkbar, dass sich im Laufe des Projektes zeigt, dass es besser ist, die Schritte 2 und 3 zu vertauschen.

### Texterkennung (OCR)
Für die Texterkennung kann ggf. auf bestehende OCR-Frameworks, wie Tesseract zurückgegriffen werden.

### Erkennung der Art des Eintrages
Es handelt sich dabei um eine Klassifikationsaufgabe. Die Erkennung der Art des Eintrages ist erforderlich, da sie für die Erstellung des BibTex-Eintrages erforderlich ist. 

### Extraktion der BibTex-Attribute
Für die Extraktion der BibTex-Attribute sind mehrere Lösungsansätze denkbar, die abgewogen werden sollten.
* Extraktion mittels Prompt-Engineering über ChatGPT
* Extraktion mittels eines vortrainierten LLMs mit ggf. weiterer Verfeinerung durch Nachtraining
* Lösung, die Textpassagen klassifiziert (z.B. auf Token-Ebene), wobei die Klassen den Attributen des BibTex-Formates entsprechen

### Nachbereitung und Überführung des Ergebnisses in das BibTex-Format
Ggf. müssen die extrahierten Daten noch normiert bzw. nachbereitet werden und in das BibTex-Fromat überführt werden, wenn das verwendete Modell die erforderlichen Schritte nicht selbst abdeckt. Zu möglichen Normierungen bzw. Nachbereitungen zählen Beispielsweise die Vervollständigung von Konverenznamen und ggf. die Schreibweise bei mehreren Autoren (teilweise wird und, and oder & verwendet, um mehrere Autoren anzugeben). 

---

## Roadmap
| Datum  | Uhrzeit     | Termin                         |
|:-------|:------------|:-------------------------------|
| 17.04. |             | Kickoff (Call)                 |
| 25.04. |             | Themenauswahl & Gruppenbildung |
| 02.05. | 14:00-15:30 | Pitches (Call)                 |
| 13.05. |             | Projektplan angefertigt        |
| 17.05. |             | Feedback Projektplan           |
| 13.06. | 17:00-18:30 | Prototyp Pitches "Durchstich"  |
| 21.06. |             | Peer-Feedback                  |
| 18.07. | 8:00-10:00  | Abschlussdemo (Call)           |
| 30.09. |             | Abgabe Dokumentation           |

### Projektverlauf

```mermaid
gantt
    
    dateFormat  DD.MM.YYYY
    axisFormat %d.%m
    %%tickInterval 1week
    %%weekday monday
    
    title       BibTexConverter
    %%excludes    weekends
    todayMarker stroke-width:5px,stroke:#0f0,opacity:0.5
    %% oder todayMarker off 
    
    
    section Orga-Milestones
        Gruppenbildung  :des1, 26.04.2024,  5d
        Fertigstellung Projektplan:       milestone, m2, 13.05.2024,
        Durchstich-Pitch : milestone, m5, 13.06.2024, 
        Abschlussdemo:     milestone, m10, 18.07.2024,
        Beginn Dokumentation:     milestone, m20, 22.07.2024,
        %%Abgabe Dokumention:   milestone, m20, 30.09.2024,  
    
%%    section Wochenübersicht
%%        W1     : W1, 13.05.2024, 7d
%%        W2     : W2, 20.05.2024, 7d
%%        W3     : W3, 27.05.2024, 7d
%%        W4     : W4, 03.06.2024, 7d
%%        W5     : W5, 10.06.2024, 7d
%%        W6     : W6, 17.06.2024, 7d
%%        W7     : W7, 24.06.2024, 7d
%%        W8     : W8, 01.07.2024, 7d
%%        W9     : W9, 08.07.2024, 7d
%%        W10    : W10, 15.07.2024, 7d

    section Porjektinitiierung
        Way Of Working : P01, 03.05.2024, 14d
        Auswahl Tools + Plattformen : P01, 03.05.2024, 14d

    section Analyse + Design
    
        Anforderungsanalyse: P01, 13.05.2024, 14d
        Prozessbeschreibung: P02, 13.05.2024, 14d
        Daten- und IT-Architektur : P03, 13.05.2024, 14d
        Glossar erstellen : P05, 13.05.2024, 14d
        Literangabeformate analysisieren : P06, 20.05.2024, 14d
        Datenquellen bestimmen : P07, 13.05.2024, 14d
        Web Scraping : P08, 13.05.2024, 14d
        Webserver + Filesystem aufbauen : P09, 20.05.2024, 14d
    
    section Data-Wrangling

        Explorative Datenenalyse : P10, 20.05.2024, 14d
        Datenqualität definieren : P10, 20.05.2024, 14d
        Datenbereinigung : P10, 20.05.2024, 14d
        Datenvorverarbeitung : P08, 20.05.2024, 14d
    
    section Modellierung

        Eruierung und Modellauswahl : P9, 27.05.2024, 14d
        Feature Engineering : P9, 03.06.2024, 14d
        Training + Testing : P9, 03.06.2024, 14d
        Evaluation : P9, 10.06.2024, 14d
        Weboberfläche : P9, 10.06.2024, 14d
        Feedbackaufarbeitung : crit,P12, 17.06.2024, 14d
        
    section Benchmarking und Dokumentation

        Benchmarking : P16, 01.07.2024, 14d
        Abschlusspräsentation erstellen : P18, 08.07.2024, 7d


%%    section Lars
%%        Task1    : L1, 13.05.2024, 7d
%%        Task2    : L2, after L1, 7d
%%        Task3    : L3, after L2, 7d
        
%%    section David
%%        Task1    : D1, 13.05.2024, 7d
%%        Task2    : D2, after D1, 7d
%%        Task3    : D3, after D2, 7d

%%    section Jürgen
%%        Task1    : J1, 13.05.2024, 7d
%%        Task2    : J2, after J1, 7d
%%        Task3    : J3, after J2, 7d

%%    section Constantin
%%        Task1    : C1, 13.05.2024, 7d
%%       Task2    : C2, after C1, 7d
%%       Task3    : C3, after C2, 7d

    
```

### Projektphasen

#### Phase 1: Analyse

* Anforderungsanalyse: <br> Beschreibung
* Rohdaten (Text/Bild) aquirieren: <br> Beschreibung
* BibTex-Formate/Syntax: <br> Beschreibung  
* Ansatz-Recherche: <br> Beschreibung 
* Datenbereinigung: <br> Beschreibung

#### Phase 2: Implementierung        
* LLM-Screening: <br> Beschreibung 
* Tokenisierung: <br> Beschreibung 
* Prompt Engineering: <br> Beschreibung  
* Implememtierung: <br> Beschreibung 
* Testing: <br> Beschreibung

#### Phase 3 : Optimierung 
* Fehlerbehebung: <br> 
  Beschreibung 
* Feedbackaufarbeitung: <br> Beschreibung
* Optimierung: <br> Beschreibung 
* Weboberfläche: <br> Beschreibung 

#### Phase 4 : Benchmarking und Dokumentation
* Benchmarking: <br> Beschreibung
* Texterkennung: <br> Beschreibung 
* Visualisierung: <br> Beschreibung 
* Abschlusspräsentation erstellen: <br> Beschreibung 

---

## Backlog Priorisierungen

### Prio1

### Prio2

* Texterkennung von Bildern

### Prio3
* Texterkennung von pdf
* Vervollständigung von Vornamen
* Abgleich mit Google-Scholar

---

## Verzeichnisstruktur
### dokumentation
Verzeichnis für die Beschreibung der Lösung und die Planung der Umsetzung etc.

### rohdaten
Rohdaten für das Training.

### (aufbereitete_daten / trainingsdaten / validierungsdaten)
Ggf. ergibt sich später, dass wir die Rohdaten doch noch vorbereiten müssen, oder wir splitten die die Daten fix in trainings- und testdaten, dann könnten wir ggf. noch diese Verzeichnisse anlegen. Aktuell 

### sourcen
Sourcen für die Umsetzung der Lösung.

### test
Sourcen für unittests (pytest).

### modelle
Ablageort für trainierte Modelle zur Wiederherstellung (pickle dumps etc).


---

## Quellen für Testdaten
https://aclanthology.org/
https://writemd.rz.tuhh.de/jkQeRnMWQ8a2sJFD4crhhg?both


---

## Sonstiges
Link zur Modulseite:
https://moodle.fernuni-hagen.de/course/index.php?categoryid=4
Direktlink:
https://moodle.fernuni-hagen.de/course/view.php?id=1461

Link zum Zoom Raum:
https://fernuni-hagen.zoom.us/j/68338461344?pwd=UTZJZXRsV29SYnVzSUt6aFV2WDBwQT09

