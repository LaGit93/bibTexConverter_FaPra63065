# BibTex-Konverter

## Kurzfassung
Der BibTex-Konverter wurde im Rahmen des Projektpraktikums Sprachtechnologie an der Fernuniversität in Hagen 
entwickelt. Mit ihm ist es möglich, die Referenz einer Veröffentlichung von einem 
einfachen String in das BibTex-Format zu konvertieren. Weiter Informationen
befinden sich im [Wiki](https://github.com/LaGit93/bibTexConverter_FaPra63065/wiki/BibTex%E2%80%90Konverter) dieses Projektes

## Installationsanleitung 

### 1. Clonen des Repositories

### 2. Installation von miniconda

### 3. Einrichten einer virtuellen Entwicklungsumgebung

### 4 (optional) Löschen von virtuellen Entwicklungsumgebungen in miniconda


## Bedienungsanleitung

### 1. Referenzen als Input

### 2. Konvertieren in BibTex

### 3. Speichern der konvertierten Referenzen

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
