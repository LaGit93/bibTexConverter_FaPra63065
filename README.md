# BibTex-Konverter

## Kurzfassung
Der BibTex-Konverter wurde im Rahmen des Projektpraktikums Sprachtechnologie an der Fernuniversität in Hagen 
entwickelt. Mit ihm ist es möglich, die Referenz einer Veröffentlichung von einem 
einfachen String in das BibTex-Format zu konvertieren. Weiter Informationen
befinden sich im [Wiki](https://github.com/LaGit93/bibTexConverter_FaPra63065/wiki/BibTex%E2%80%90Konverter) dieses Projektes

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
Laden sie den BibTex-Konverter über folgenden Link auf ihr System:

https://github.com/LaGit93/bibTexConverter_FaPra63065/archive/refs/heads/main.zip

Entpacken Sie anschließend die .zip-Datei.

#### c. selektiver Download

Sollten Sie die Testdaten, Trainingsdaten und die Dokumentation nicht benötigen, ist es ausreichend, 
folgende Dateien und Ordner aus dem Verzeichnis ```sourcen``` in Ihrem Projektverzeichnis zu speichern:
1. main.py
2. ocr_clipboard.py
3. BibTexMagic.py
4. conda.yaml
5. templates

Für den Fall, dass Sie bereits alle Pakete lokal installiert haben, die in der
Datei [conda.yaml](https://github.com/LaGit93/bibTexConverter_FaPra63065/blob/main/sourcen/conda.yaml)
aufgelistet sind, können Sie den Installationsvorgang hier abbrechen. Wenn Sie die 
Nutzung von virtuellen Umgebungen nutzen bevorzugen, fahren Sie bitte mit den 
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

### 4 (optional) Löschen von virtuellen Entwicklungsumgebungen in miniconda
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

---

## Bedienungsanleitung

### 1. Referenzen als Input

### 2. Konvertieren in BibTex

### 3. Speichern der konvertierten Referenzen


## Nachher löschen
(inklusive Vorbedingungen, externe Abhängigkeiten)

Die für die unterschiedlichen Aufgaben verwendeten Python-Bibliotheken sind in der Datei conda.yaml zusammengestellt. 
Zum Reproduzierbaren Aufbau einer Umgebung mit allen benötigten Bibliotheken
Zur Verwendung, miniconda installieren, wie auf URL https://docs.anaconda.com/free/miniconda/miniconda-install/ beschrieben,
dann nach Aktivieren von conda (Üblicherweise muss die Shell nach der Installation neu gestartet werden, bzw unter Windows
über das Start-Menü eine spezielle Conda-Shell gestartet werden, dann vom git-root-Verzeichnis, in dem sich die Datei conda.yaml
befindet folgendes ausführen: 

	conda env create -f conda.yaml -n bibTexConverter
	conda activate bibTexConverter

Der zweite Befehl muss ggf. jedes mal vor dem Start der Arbeit eingegeben werden. Ggf. muss beim ersten Befehl noch `--solver classic` angehängt werden, falls beim Ausführen der Zeile eine Fehlermeldung bezüglich des Solvers erscheint.
