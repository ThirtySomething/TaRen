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

import logging
import os

from taren.downloadlist import DownloadList
from taren.episode import Episode
from taren.episodelist import EpisodeList
from taren.helper import Helper
from taren.tarenconfig import TarenConfig
from taren.team import Team
from taren.teamlist import TeamList


class Grouping:
    """
    Group specified episodes by given data
    """

    ############################################################################
    def __init__(self: object, config: TarenConfig, teams: TeamList, episodes: EpisodeList, downloads: list[str]) -> None:
        self._config: TarenConfig = config
        self._teams: TeamList = teams
        self._episodes: EpisodeList = episodes
        self._downloads: DownloadList = downloads

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
                    episodepath: str = os.path.join(self._config.taren_downloads, episode)
                    groupfile.write('   <a href="file:///{}">{}</a><br>\n'.format(episodepath, episode))
                groupfile.write("   <p>")
            groupfile.write("</body>\n")
            groupfile.write("</html>\n")

    ############################################################################
    def process(self: object) -> None:
        for currentDownload in self._downloads:
            logging.debug("-" * 80)
            episode: Episode = self._episodes.find_episode(currentDownload)
            if episode.empty:
                logging.error("No episode found for [{}]".format(currentDownload))
                continue
            team: Team = self._teams.find_team(episode)
            if team.empty:
                logging.error("No team found for [{}]".format(episode))
                continue

            logging.debug("Team [{}]".format(team))
            logging.debug("Episode [{}]".format(episode))
            logging.debug("Download [{}]".format(currentDownload))
