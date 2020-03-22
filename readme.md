# TaRen

TaRen steht für ```Ta```tort```Ren```anmer. Was soll denn das sein?

## Motivation

Über die [Mediathekview][mediathekview] lade ich mir die Tatort Filme aus der
ARD Mediathek herunter. Dabei haben diese Downloads dann teilweise sehr
kryptische Dateinamen. Sicher, der Kontent ist immer ersichtlich. Aber es sind
zusätzliche Informationen vorhanden, die mich eigentlich nicht interessieren.
Da sind zum Beispiel die Film ID, verschiedene Präfixe wie ```Film & Serie```
und dergleichen mehr.

## Die Lösung

TaRen holt sich den Artikel über die Tatortfolgen aus der [Wikipedia][tatortwiki]
und bennent die Dateien vernünftig um. Vernünftig heißt, dass der Download dann
dem Muster ```0000 - Sender - Titel - Kommissare.mp4``` entspricht. Also
vierstellig die Nummer der Folge, dann der Titel des Tatorts und zum Schluss
die ermittelnden Kommissare.

## Technisch

### Voraussetzungten

- Damit das Ganze funktioniert, wird [Python 3][python] benötigt - entwickelt
und getestet wurde mit Python 3.8.1.
- Das Python Modul [Beautiful Soup][beautifulsoup] muss installiert sein.
- [Logging][logging] wird ebenfalls benötigt.

### Prozess

Der Wikipedia Artikel wird geparst und die Tatortfolgen in eine interne
Liste eingetragen. Dann werden auf der Festplatte alle ```*.mp4``` Dateien
gesucht, in denen das Keyword ```Tatort``` vorkommt. In dem Dateinamen wird
dann gesucht, ob dieser den Namen einer Tatortfolge enthält. In diesem Fall
wird die Datei dann umbenannt. Gibt es diese Datei bereits, wird die Dateigröße
verglichen - der Download mit der HD Auflösung ist größer und wird eher
behalten. Ist also der Tatort bereits in SD Auflösung vorhanden, und es wurde
der gleiche Tatort in HD Auflösung ebenfalls heruntergeladen, dann wird die
SD Version gelöscht und die HD Version behalten. Ansonsten wird der Download
nicht umbenannt, sondern gelöscht.

### Matching

Da es ja Folgen gibt, die den gleichen Namen haben, wurde das Matching
überarbeitet. Das passiert auf folgende Weise:

- Es wird geprüft, ob der Dateiname mit einer vierstelligen Zahl und einem
Leerzeichen beginnt. Diese vierstellige Zahl wird als eine Folgennummer verwendet.
Gibt es also eine Folge, die diese Nummer hat, ist das der Match. Damit kann man
Downloads so markieren, dass sie gleich die richtige Folge haben. Sinnvoll ist
das dann, wenn es Folgen mit gleichem Titel gibt, z. B. [Taxi nach Leipzig][tnlo]
vs. [Taxi nach Leipzig][tnln].
- Es wird geprüft, ob der Dateiname mit 'Tatort' und einer vierstelligen Zahl
beginnt. Wenn die vierstellige Zahl die Folge einer Nummer ist, wird dies als
Indiz dafür gewertet, daß es sich hierbei um eine bestimmte Folge handelt.
- Erst zum Schluß wird geprüft, ob der Dateiname des Downloads den Namen einer
Tatort Folge enthält.

## Zum Nachdenken

- Über [Reguläre Ausdrücke][regexp] wird der Name der Folge bereinigt. Es steht
dann kein ```(Folge XXXX hat den gleichen Titel)``` im Titel. Das kann
offensichtlich zu Schwierigkeiten führen. Eventuell sollte man diese Bereinigung
nochmal überdenken.
- Ebenfalls über [Reguläre Ausdrücke][regexp] werden die Namen der Kommissare
bearbeitet. Es steht dann kein ```(Gastauftritt XXX)``` bei den Kommisaren. Auch
hierüber kann man nachdenken.

## Stolpersteine

### UTF-8

Tjoa, man solle es kaum glauben, aber im Jahr 2020 ist noch immer nicht alles
[UTF-8][utf8], auch bei [Python][python] nicht. Der [Wikipedia][tatortwiki]-Artikel
ist in [UTF-8][utf8]. Damit ich jedoch nicht bei jedem Test und Durchlauf die
Webseite abfrage, habe ich einen Cache eingebaut. Das heißt, frühestens alle X
Tage wird die Seite neu geladen, ansonsten aus dem Cache (sprich, einer Datei)
geladen. Allerdings kann man in [Python][python] mit den Standard Funktionen
keine [UTF-8][utf8] Dateien lesen und schreiben. Dazu muss man die Funktionen
aus dem ```codecs``` Package verwenden. Auch das Package ```logging``` kann
nicht so ohne weiteres mit [UTF-8][utf8] umgehen. Das ist mit der
```basicConfig``` nicht machbar bzw. vorgesehen. Es geht nur umständlich. Und
beides, weder das mit den Dateien noch das mit dem Logging ist vernünftig
erklärt. Zum Glück gibt es [stackoverflow][stackoverflow], da findet man dann
die richtigen Hinweise.

## Hinweise

Damit das mit [UTF-8][utf8] auch korrekt funktioniert, muß die Umgebungsvariable

```SHELL
PYTHONIOENCODING="utf-8"
```

gesetzt sein.

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
[logging]: https://docs.python.org/3/library/logging.html
[mediathekview]: https://mediathekview.de/
[python]: https://de.wikipedia.org/wiki/Python_(Programmiersprache)
[regexp]: https://de.wikipedia.org/wiki/Regul%C3%A4rer_Ausdruck
[stackoverflow]: https://www.stackoverflow.com
[tatortwiki]: https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen
[tnln]: https://de.wikipedia.org/wiki/Tatort:_Taxi_nach_Leipzig_(2016)
[tnlo]: https://de.wikipedia.org/wiki/Tatort:_Taxi_nach_Leipzig_(1970)
[utf8]: https://de.wikipedia.org/wiki/UTF-8
