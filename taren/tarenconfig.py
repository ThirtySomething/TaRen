"""
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
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../vendor/MDO/MDO/"))

from MDO import MDO


class TarenConfig(MDO):
    """
    Contains dynamic settings of TaRen
    """

    ############################################################################
    def setup(self: object) -> bool:
        self.add("logging", "logfile", "program.log")
        self.add("logging", "loglevel", "info")
        self.add("logging", "logstring", "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s:%(funcName)s | %(message)s")
        self.add("taren", "downloads", "v:\\tatort")
        self.add("taren", "extension", "mp4")
        self.add(
            "taren",
            "grouping",
            {
                "active": True,
                "groups": {
                    "Baden-Baden - Gerber": ["Gerber"],
                    "Baden-Baden - Pflüger": ["Pflüger"],
                    "Baden-Baden - Wiegand": ["Wiegand"],
                    "Baden-Württemberg - Lutz": ["Lutz"],
                    "Berlin - Behnke": ["Behnke"],
                    "Berlin - Bülow": ["Bülow"],
                    "Berlin - Karow": ["Bonard", "Karow", "Rubin"],
                    "Berlin - Kasulke": ["Kasulke"],
                    "Berlin - Markowitz": ["Markowitz"],
                    "Berlin - Ritter": ["Hellmann", "Ritter", "Stark"],
                    "Berlin - Roiter": ["Roiter", "Zorowski"],
                    "Berlin - Schmidt": ["Schmidt"],
                    "Berlin - Walther": ["Walther"],
                    "Bern - Carlucci": ["Carlucci"],
                    "Bern - Howald": ["Howald"],
                    "Bern - von Burg": ["von Burg", "Gertsch"],
                    "Bonn - Delius": ["Delius"],
                    "Braunschweig - Nagel": ["Nagel"],
                    "Bremen - Böck": ["Böck"],
                    "Bremen - Lürsen": ["Lürsen", "Stedefreund"],
                    "Bremen - Moormann": ["Andersen", "Moormann", "Selb"],
                    "Bremen - Piper": ["Piper"],
                    "Bremerhaven - Schnoor": ["Schnoor"],
                    "Dortmund - Faber": ["Bönisch", "Dalay", "Faber", "Herzog", "Kossik", "Pawlak"],
                    "Dresden - Ehrlicher": ["Ehrlicher", "Kain"],
                    "Dresden - Gorniak": ["Gorniak", "Schnabel", "Sieland", "Winkler"],
                    "Duisburg - Schimanski": ["Schimanski", "Thanner"],
                    "Düsseldorf - Flemming": ["Flemming", "Koch"],
                    "Erfurt - Funck": ["Funck", "Grewel", "Schaffert"],
                    "Essen - Haferkamp": ["Haferkamp"],
                    "Essen - Kreutzer": ["Kreutzer"],
                    "Essen, Frankfurt - Enders": ["Enders"],
                    "Frankfurt/Main - Bergmann": ["Bergmann"],
                    "Frankfurt/Main - Brinkmann": ["Brinkmann"],
                    "Frankfurt/Main - Dellwo": ["Dellwo", "Sänger"],
                    "Frankfurt/Main - Dietze": ["Dietze"],
                    "Frankfurt/Main - Felber": ["Felber"],
                    "Frankfurt/Main - Janneke": ["Brix", "Janneke"],
                    "Frankfurt/Main - Konrad": ["Konrad"],
                    "Frankfurt/Main - Rolfs": ["Rolfs"],
                    "Frankfurt/Main - Sander": ["Sander"],
                    "Frankfurt/Main - Steier": ["Mey", "Steier"],
                    "Freiburg - Tobler": ["Berg", "Tobler", "Weber"],
                    "Freiburg, Mainz - Berlinger": ["Berlinger", "Rascher"],
                    "Göttingen - Lindholm": ["Lindholm", "Schmitz"],
                    "Hamburg - Batu": ["Batu"],
                    "Hamburg - Castorff": ["Castorff", "Holicek"],
                    "Hamburg - Falke": ["Falke", "Lorenz", "Grosz"],
                    "Hamburg - Ronke": ["Ronke"],
                    "Hamburg - Sommer": ["Sommer"],
                    "Hamburg - Stoever": ["Brockmöller", "Stoever"],
                    "Hamburg - Trimmel": ["Trimmel"],
                    "Hamburg - Tschiller": ["Gümer", "Tschiller"],
                    "Hannover - Brammer": ["Brammer"],
                    "Heppenheim - Rullmann": ["Rullmann"],
                    "Kiel - Borowski": ["Borowski", "Brandt", "Jung", "Sahin"],
                    "Kiel - Finke": ["Finke"],
                    "Konstanz - Blum": ["Blum", "Perlmann"],
                    "Köln - Ballauf und Schenk": ["Ballauf", "Schenk"],
                    "Köln - Kressin": ["Kressin"],
                    "Leipzig - Ehrlicher": ["Ehrlicher", "Kain"],
                    "Leipzig - Saalfeld": ["Keppler", "Saalfeld"],
                    "Ludwigshafen - Odenthal": ["Kopper", "Odenthal", "Stern"],
                    "Luzern - Flückiger": ["Flückiger", "Ritschard"],
                    "Lübeck - Beck": ["Beck"],
                    "Lübeck - Greve": ["Greve"],
                    "Mainz - Buchmüller": ["Buchmüller"],
                    "München - Batic Leitmayr": ["Batic", "Leitmayr"],
                    "München - Brandenburg": ["Brandenburg"],
                    "München - Lenz": ["Lenz"],
                    "München - Riedmüller": ["Riedmüller"],
                    "München - Scherrer": ["Scherrer"],
                    "München - Veigl": ["Veigl"],
                    "Münster - Thiel": ["Börne", "Thiel"],
                    "Nürnberg - Voss": ["Ringelhahn", "Voss"],
                    "Saarbrücken - Kappl": ["Deininger", "Kappl"],
                    "Saarbrücken - Palu": ["Palu", "Deininger"],
                    "Saarbrücken - Schäfermann": ["Schäfermann"],
                    "Saarbrücken - Schürk": ["Holzer", "Schürk"],
                    "Saarbrücken - Stellbrink": ["Stellbrink", "Marx"],
                    "Schwarzwald - Tobler": ["Berg", "Tobler"],
                    "Stuttgart - Bienzle": ["Bienzle", "Gächter"],
                    "Stuttgart - Lannert": ["Bootz", "Lannert"],
                    "Stuttgart - Schreitle": ["Schreitle"],
                    "Weimar - Dorn": ["Dorn", "Lessing"],
                    "Wien - Becker": ["Becker"],
                    "Wien - Eisner": ["Eisner", "Fellner"],
                    "Wien - Fichtl": ["Fichtl"],
                    "Wien - Hirth": ["Hirth"],
                    "Wien - Kant": ["Kant", "Varanasi"],
                    "Wien - Lutinsky": ["Lutinsky"],
                    "Wien - Marek": ["Marek"],
                    "Wien - Pfeifer": ["Pfeifer", "Passini"],
                    "Wiesbaden - Murot": ["Murot"],
                    "Zürich - Grandjean": ["Grandjean", "Ott"],
                },
                "output": "v:\\tatort\\Tatort.html",
            },
        )
        self.add("taren", "maxcache", "1")
        self.add("taren", "pattern", "Tatort")
        self.add("taren", "trash", ".trash")
        self.add("taren", "trashage", "3")
        self.add("taren", "wiki", "https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen")
