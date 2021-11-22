# TaRen

TaRen steht für `Ta`tort`Ren`amer. Was soll denn das sein?

## Motivation

Über die [Mediathekview][mediathekview] lade ich mir die Tatort Filme aus der
ARD Mediathek herunter. Dabei haben diese Downloads dann teilweise sehr
kryptische Dateinamen. Sicher, der Kontent ist immer ersichtlich. Aber es sind
zusätzliche Informationen vorhanden, die mich eigentlich nicht interessieren.
Da sind zum Beispiel die Film ID, verschiedene Präfixe wie `Film & Serie`
und dergleichen mehr.

## Die Lösung

TaRen holt sich den Artikel über die Tatortfolgen aus der [Wikipedia][tatortwiki]
und bennent die Dateien vernünftig um. Vernünftig heißt, dass der Download dann
dem Muster `Tatort - 0000 - Sender - Titel - Kommissare.mp4` entspricht.
Also das Präfix Tatort, vierstellig die Nummer der Folge, der Sender, der Titel
des Tatorts und zum Schluss die ermittelnden Kommissare.

## Technisch

### Voraussetzungen

- Damit das Ganze funktioniert, wird [Python 3][python] benötigt - entwickelt
und getestet wurde mit Python 3.8.1.
- Das Python Modul [Beautiful Soup][beautifulsoup] muss installiert sein.
- [Logging][logging] wird ebenfalls benötigt.
- Das Paket [Requests][requests] ist ebenfalls notwendig.
- Für die UI wird [PySimpleGui][pysimplegui] benötigt.

```cmd
pip install beautifulsoup4
pip install logging
pip install requests
pip install pysimplegui
```

### Prozess

Der Wikipedia Artikel wird geparst und die Tatortfolgen in eine interne
Liste eingetragen. Dann werden auf der Festplatte alle `*.mp4` Dateien
gesucht, in denen das Keyword `Tatort` vorkommt. In dem Dateinamen wird
dann gesucht, ob dieser den Namen einer Tatortfolge enthält. In diesem Fall
wird die Datei dann umbenannt. Gibt es diese Datei bereits, wird die Dateigröße
verglichen - der Download mit der HD Auflösung ist größer und wird eher
behalten. Ist also der Tatort bereits in SD Auflösung vorhanden, und es wurde
der gleiche Tatort in HD Auflösung ebenfalls heruntergeladen, dann wird die
SD Version ~~gelöscht~~ in den Papierkorb von TaRen verschoben und die HD
Version behalten. Ansonsten wird der Download nicht umbenannt, sondern
~~gelöscht~~ in den Papierkorb von TaRen verschoben.

### Matching

Da es ja Folgen gibt, die den gleichen Namen haben, wurde das Matching
überarbeitet. Das passiert auf folgende Weise:

- Es wird geprüft, ob der Dateiname mit einer vierstelligen Zahl und einem
Leerzeichen beginnt. Diese vierstellige Zahl wird als eine Folgennummer
verwendet. Gibt es also eine Folge, die diese Nummer hat, ist das der Match.
Damit kann man Downloads so markieren, dass sie gleich die richtige Folge haben.
Sinnvoll ist das dann, wenn es Folgen mit gleichem Titel gibt, z. B.
[Taxi nach Leipzig][tnlo] vs. [Taxi nach Leipzig][tnln].
- Es wird geprüft, ob in dem Dateinamen ein `_Exxx_` enthalten ist. Das
`xxx` ist eine drei- oder vierstellige Zahl. Das wäre die Episodennummer
von einem Download bei Dailymotion.
- Es wird geprüft, ob der Dateiname mit `Tatort` und einer vierstelligen
Zahl beginnt. Wenn die vierstellige Zahl die Folge einer Nummer ist, wird dies
als Indiz dafür gewertet, dass es sich hierbei um eine bestimmte Folge handelt.
- Erst zum Schluß wird geprüft, ob der Dateiname des Downloads den Namen einer
Tatort Folge enthält.

### Oberfläche

An dem Bedinkonzept gibt es noch Verbesserungspotential.

#### Standardansicht

Zum Beispiel das Layout hier.

![Startup][gui01]

#### Einstellungen

Hier könnten die Eingabefelder etwas breiter sein.

![Settings][gui02]

#### Prozess erfolgreich

Und Umlaute sind auch ein Thema.

![Done][gui03]

## Zum Nachdenken

- Über [Reguläre Ausdrücke][regexp] wird der Name der Folge bereinigt. Es steht
dann kein `(Folge XXXX hat den gleichen Titel)` im Titel. Das kann
offensichtlich zu Schwierigkeiten führen. Eventuell sollte man diese Bereinigung
nochmal überdenken.
- Ebenfalls über [Reguläre Ausdrücke][regexp] werden die Namen der Kommissare
bearbeitet. Es steht dann kein `(Gastauftritt XXX)` bei den Kommisaren. Auch
hierüber kann man nachdenken.

## Stolpersteine

### UTF-8

Tjoa, man sollte es kaum glauben, aber im Jahr 2020 ist noch immer nicht alles
[UTF-8][utf8], auch bei [Python][python] nicht. Der [Wikipedia][tatortwiki]-
Artikel ist in [UTF-8][utf8]. Damit ich jedoch nicht bei jedem Test und
Durchlauf die Webseite abfrage, habe ich einen Cache eingebaut. Das heißt,
frühestens alle X Tage wird die Seite neu geladen, ansonsten aus dem Cache
(sprich, einer Datei) geladen. Allerdings kann man in [Python][python] mit den
Standard Funktionen keine [UTF-8][utf8] Dateien lesen und schreiben. Dazu muss
man die Funktionen aus dem `codecs` Package verwenden. Auch das Package
`logging` kann nicht so ohne weiteres mit [UTF-8][utf8] umgehen. Das ist
mit der `basicConfig` nicht machbar bzw. vorgesehen. Es geht nur
umständlich. Und beides, weder das mit den Dateien noch das mit dem Logging ist
vernünftig erklärt. Zum Glück gibt es [stackoverflow][stackoverflow], da findet
man dann die richtigen Hinweise.

### False-Positives

Unter Umständen gibt es [False-Positives][fapo]. Die normale Vorgehensweise ist,
die existierende Episode zu löschen und dann die neue Episode entsprechend
umzubenennen. Unschön wird das ganze aber dann, wenn die Erkennung nicht gut
genug war und es sich dabei um zwei verschiedene Episoden handelt - dann geht
die eine davon ins digitale Nirwana und verschwindet aus der Sammlung. Um das
zu verhindern, wurde ein `Trash` eingebaut. Die Dateien werden jetzt nicht
sofort gelöscht, sondern erst einmal in den `Trash` verschoben. Erst nach
`n` Tagen im Trash werden sie dann tatsächlich gelöscht. Dabei wird mit dem
verschieben in den `Trash` das Datum der `*.mp4`-Datei auf den
Löschzeitpunkt gesetzt. Dies ermöglicht beim Programmende zu prüfen, ob die
Datei bereits die `n` Tage im `Trash` war und zu löschen ist, oder ob
sie noch etwas länger dort liegen bleibt.

## Hinweise

Damit das mit [UTF-8][utf8] auch korrekt funktioniert, muß die Umgebungsvariable

```SHELL
PYTHONIOENCODING="utf-8"
```

gesetzt sein.

## ToDos

- ~~Verwendung einer INI Datei zur einfachen Konfiguration~~ Done
- ~~Schreiben einer INI Datei mit Defaults~~ Done
- ~~Verbeserung des INI Handlings bei fehlenden Einträgen~~ Done
- ~~Einbau eines `Trash`~~ Done
- ~~Eine GUI für das Programm~~ Done
- `Trash` als Klasse
- Berücksichtigung eines Ordners mit bereits angeschauten Folgen

## Lizenz

******************************************************************************
Copyright 2020 ThirtySomething
******************************************************************************
This file is part of TaRen.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
******************************************************************************

See also attached file [`LICENSE`](./LICENSE "MIT License").

[beautifulsoup]: https://www.crummy.com/software/BeautifulSoup/
[fapo]: https://en.wikipedia.org/wiki/False_positives_and_false_negatives
[gui01]: ./images/Taren_GUI.png "Startup"
[gui02]: ./images/Taren_GUI_Config.png "Settings"
[gui03]: ./images/Taren_GUI_Done.png "Process done"
[logging]: https://docs.python.org/3/library/logging.html
[mediathekview]: https://mediathekview.de/
[pysimplegui]: https://pysimplegui.readthedocs.io/en/latest/
[python]: https://de.wikipedia.org/wiki/Python_(Programmiersprache)
[regexp]: https://de.wikipedia.org/wiki/Regul%C3%A4rer_Ausdruck
[requests]: https://docs.python-requests.org/en/master/
[stackoverflow]: https://www.stackoverflow.com
[tatortwiki]: https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen
[tnln]: https://de.wikipedia.org/wiki/Tatort:_Taxi_nach_Leipzig_(2016)
[tnlo]: https://de.wikipedia.org/wiki/Tatort:_Taxi_nach_Leipzig_(1970)
[utf8]: https://de.wikipedia.org/wiki/UTF-8
