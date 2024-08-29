# BibTex-Konverter

## Kurzfassung
Der BibTex-Konverter wurde im Rahmen des Projektpraktikums Sprachtechnologie an der Fernuniversität in Hagen 
entwickelt. Mit ihm ist es möglich, die Referenz einer Veröffentlichung von einem 
einfachen String in das BibTex-Format zu konvertieren:
![Intro.png](Dokumente%2FIntro.png)
Weiter Informationen
befinden sich im [Wiki](https://github.com/LaGit93/bibTexConverter_FaPra63065/wiki/BibTex%E2%80%90Konverter) dieses Projektes.

## Installationsanleitung 

### 1. Clonen des Repositories
Es gibt verschiedene Möglichkeiten, den BibTex-Konverter auf Ihrem System zu installieren. 
Wählen Sie eine Möglichkeit aus den folgenden aus:

#### a. Clonen über die Kommandozeile
Öffnen Sie ein Terminal und wechseln Sie in das Verzeichnis, in das Sie das Repository
clonen möchten. Führen Sie anschließend folgenden Befehl für das Clonen aus:

```
git clone https://github.com/LaGit93/bibTexConverter_FaPra63065
```

#### b. Download als .zip-Datei
Laden sie den BibTex-Konverter als [.zip-Datei](https://github.com/LaGit93/bibTexConverter_FaPra63065/archive/refs/heads/main.zip) auf ihr System und entpacken Sie die Datei.

#### c. selektiver Download

Sollten Sie die Testdaten, Trainingsdaten und die Dokumentation nicht benötigen, ist es ausreichend, 
folgende Dateien und Ordner aus dem Verzeichnis ```sourcen``` in Ihrem Projektverzeichnis zu speichern:
1. main.py
2. ocr_clipboard.py
3. BibTexMagic.py 
4. conda.yaml
5. templates


Für den Fall, dass Sie bereits alle erforderlichen Pakete lokal installiert haben, die in der
Datei [conda.yaml](https://github.com/LaGit93/bibTexConverter_FaPra63065/blob/main/sourcen/conda.yaml)
aufgelistet sind, können Sie den Installationsvorgang hier abbrechen. Wenn Sie die 
Nutzung von virtuellen Umgebungen bevorzugen, fahren Sie bitte mit den 
Schritten 2 und 3 fort.


### 2. Installation von miniconda

Die für die unterschiedlichen Aufgaben verwendeten Python-Bibliotheken sind in der Datei 
[conda.yaml](https://github.com/LaGit93/bibTexConverter_FaPra63065/blob/main/sourcen/conda.yaml) zusammengestellt. 
Zum reproduzierbaren Aufbau einer Umgebung mit allen benötigten Bibliotheken wird
[miniconda](https://docs.anaconda.com/miniconda/) verwendet. 

Installieren Sie [miniconda](https://docs.anaconda.com/miniconda/), 
wie auf https://docs.anaconda.com/free/miniconda/miniconda-install/ 
beschrieben.



### 3. Einrichten einer virtuellen Entwicklungsumgebung

Nach dem Aktivieren von conda (üblicherweise muss die Shell nach der Installation neu gestartet werden, bzw. unter Windows
über das Start-Menü eine spezielle Conda-Shell gestartet werden) wechseln Sie in das Projektverzeichnis, in dem sich die 
Datei conda.yaml befindet. Führen Sie zur Erstellung der virtuellen Umgebung mit dem Namen 
*bibTexConverter* folgenden Befehl aus:

```
conda env create -f conda.yaml -n bibTexConverter
```

Das Erzeugen der virtuellen Umgebung wird einmalig durchgeführt und kann etwas Zeit in 
Anspruch nehmen (ca. 2,6 GB).

### 4. (optional) Löschen von virtuellen Entwicklungsumgebungen in miniconda
Wenn Sie den BibTex-Konverter nicht mehr verwenden möchten, können Sie die virtuelle
Umgebung wieder löschen. Öffnen Sie hierfür wieder eine Shell (für Windows die Conda-Shell)
und führen Sie folgende Befehle aus, um die virtuelle Umgebung *bibTexConverter* zu löschen:
1. Deaktivieren der virtuellen Umgebungen:
```
conda deactivate
```
2. Löschen der *bibTexConverter* Umgebung:
```
conda env remove -n bibTexConverter
```
3. Auflisten der virtuellen Umgebungen zur Überprüfung:
```
conda env list
```

Sollte die virtuelle Umgebung nicht entfernt worden sein, können Sie auf Ihrem System
im Ordner miniconda den Ordner ```bibTexConverter``` manuell löschen.


## Workflow

An dieser Stelle soll die Funktionsweise des BibTex-Konverters komprimiert dargestellt werden.
Eine detaillierte Beschreibung der Benutzeroberfläche befindet sich im [Wiki](https://github.com/LaGit93/bibTexConverter_FaPra63065/wiki/BibTex%E2%80%90Konverter/#Benutzeroberfl%C3%A4che)
dieses Repositories. 

<p align="center">
<img src="https://github.com/LaGit93/bibTexConverter_FaPra63065/blob/main/Dokumente/WebApp.jpeg" width="500"/>
</p>

Die Nutzung des Tools erfolgt in drei Schritten:

### 1. Referenzen als Input:
Fügen Sie die Referenz als Text (Referenzstring) in das obere Textfeld ein. Liegt die 
Referenz hingegen als Bild o.ä. vor, erstellen Sie ein Screenshot der Referenz und klicken Sie auf den Button ```OCR Read```. 
Stellen Sie für das Erkennen sprachspezifischer Sonderzeichen die korrekte Sprache ein (default ist Englisch).
Der BibTex-Konverter kann mehrere Referenzen als Batch-Konvertierung durchführen. Trennen Sie die Referenzen jeweils mit einer Leerzeile.

### 2. Konvertieren in BibTex
Überprüfen Sie den Referenzstring auf offensichtliche Fehler (Sonderzeichen, fehlerhafte Namen etc.), die durch das Kopieren oder durch die OCR entstanden sind und klicken Sie auf den Button ```Convert```.
Im unteren Textfeld wird der BibTex-Code erzeugt. Passen Sie den Code ggf. händisch an.

### 3. Speichern der konvertierten Referenzen
Der Inhalt des unteren Textfeldes wird als txt-Datei im Standardordner des Browsers gespeichert, wenn Sie den Button ```Download txt-file``` klicken.
Sie können vorher noch einen Dateinamen vergeben (default ist *BibTexConverter*)

