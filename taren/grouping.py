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

import fnmatch
import logging
import os

from taren.helper import Helper
from taren.tarenconfig import TarenConfig


class Grouping:
    """
    Group specified episodes by given data
    """

    ############################################################################
    def __init__(self: object, config: TarenConfig) -> None:
        self.config: TarenConfig = config
        try:
            self.groupingConfig = self.config.taren_grouping
            if not self.groupingConfig["active"]:
                raise
            self.active: bool = True
        except:
            self.active: bool = False

    ############################################################################
    def _buildDocument(self: object, outputFile: str, documentData: dict) -> None:
        with open(outputFile, "w") as groupfile:
            groupfile.write("<html>\n")
            groupfile.write("<head>\n")
            groupfile.write("   <title>TaRen Groups</title>\n")
            groupfile.write("</head>\n")
            groupfile.write("<body>\n")
            for group in documentData:
                groupfile.write("   <h2>{}</h2>\n".format(group))
                for episode in documentData[group]:
                    episodepath: str = os.path.join(self.config.taren_downloads, episode)
                    groupfile.write('   <a href="file:///{}">{}</a><br>\n'.format(episodepath, episode))
                groupfile.write("   <p>")
            groupfile.write("</body>\n")
            groupfile.write("</html>\n")

    ############################################################################
    def _getEpisodes(self: object, inspectors: list[str]) -> list[str]:
        episodes: list[str] = []
        for inspector in inspectors:
            logging.debug("Search episodes for inspector [{}]".format(inspector))
            searchpattern: str = "*{}*".format(inspector)
            files: list[str] = fnmatch.filter(os.listdir(self.config.taren_downloads), searchpattern)
            for file in files:
                if file not in episodes:
                    episodes.append(file)
        # Sort episode list
        episodes.sort()
        return episodes

    ############################################################################
    def _handleGroup(self: object, groupname: str, inspectors: list[str]) -> list[str]:
        inspectors.sort()
        logging.debug("Groupname [{}], inspectors(s) [{}]".format(groupname, inspectors))
        episodes: list[str] = self._getEpisodes(inspectors)
        return episodes

    ############################################################################
    def _handleGroups(self: object) -> None:
        documentData: dict = {}
        for key in self.groupingConfig["groups"]:
            episodes = self._handleGroup(key, self.groupingConfig["groups"][key])
            if 0 < len(episodes):
                documentData[key] = episodes
        documentData = dict(sorted(documentData.items()))
        self._buildDocument(self.groupingConfig["output"], documentData)

    ############################################################################
    def _prepareDirectory(self: object, dirname: str) -> bool:
        return Helper.ensureDirectory(dirname)

    ############################################################################
    def process(self: object) -> None:
        if not self.active:
            logging.info("Grouping feature not active")
            return

        self._handleGroups()
