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


class Stats:
    """
    Statistic object, contains counter for
    - Episodes total
    - Episodes owned
    - Downloads deleted
    - Downloads in trash
    """

    ############################################################################
    def __init__(self: object) -> None:
        self.downloads_deleted: int = 0
        self.downloads_moved: int = 0
        self.downloads_renamed: int = 0
        self.downloads_total: int = 0
        self.downloads_trash: int = 0
        self.episodes_owned: int = 0
        self.episodes_total: int = 0

    ############################################################################
    def __repr__(self):
        """Represent statistics as string"""
        return self.__str__()

    ############################################################################
    def __str__(self):
        """Represent statistics as string"""
        return "ET [{}], EO [{}/{:3.2f}%], DD[{}], DM [{}], DR [{}], DT [{}], DT [{}]".format(
            self.episodes_total, self.episodes_owned, (100 / self.episodes_total * self.episodes_owned), self.downloads_deleted, self.downloads_moved, self.downloads_renamed, self.downloads_total, self.downloads_trash
        )
