'''
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
'''

import configparser
import os.path
from os import path

# https://docs.python.org/3/library/configparser.html#legacy-api-examples


class TarenConfig:
    '''
    Contains dynamic settings of TaRen
    '''

    k_downloads: str = 'downloads'
    k_extension: str = 'extension'
    k_logfile: str = 'logfile'
    k_logstring: str = 'logstring'
    k_maxcache: str = 'maxcache'
    k_pattern: str = 'pattern'
    k_trash: str = 'trash'
    k_trashage: str = 'trashage'
    k_wiki: str = 'wiki'
    s_taren: str = 'TaRen'

    def __init__(self: object) -> None:
        '''
        Set default values for config
        '''
        self.downloads: str = 'v:\\tatort'
        self.extension: str = 'mp4'
        self.logfile: str = 'program.log'
        self.logstring: str = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s:%(funcName)s | %(message)s'
        self.maxcache: str = '1'
        self.pattern: str = 'Tatort'
        self.trash: str = '.trash'
        self.trashage: str = '3'
        self.wiki: str = 'https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen'

    def __read(self: object, iniFileName: str) -> None:
        '''
        Parse INI file and read values
        '''
        config: configparser.RawConfigParser = configparser.RawConfigParser()
        config.read(iniFileName)
        self.downloads = config.get(TarenConfig.s_taren, TarenConfig.k_downloads, fallback=self.downloads)
        self.extension = config.get(TarenConfig.s_taren, TarenConfig.k_extension, fallback=self.extension)
        self.logfile = config.get(TarenConfig.s_taren, TarenConfig.k_logfile, fallback=self.logfile)
        self.logstring = config.get(TarenConfig.s_taren, TarenConfig.k_logstring, fallback=self.logstring)
        self.maxcache = config.get(TarenConfig.s_taren, TarenConfig.k_maxcache, fallback=self.maxcache)
        self.pattern = config.get(TarenConfig.s_taren, TarenConfig.k_pattern, fallback=self.pattern)
        self.trash = config.get(TarenConfig.s_taren, TarenConfig.k_trash, fallback=self.trash)
        self.trashage = config.get(TarenConfig.s_taren, TarenConfig.k_trashage, fallback=self.trashage)
        self.wiki = config.get(TarenConfig.s_taren, TarenConfig.k_wiki, fallback=self.wiki)

    def __write(self: object, iniFileName: str) -> None:
        '''
        Write INI file with values
        '''
        config: configparser.RawConfigParser = configparser.RawConfigParser()
        config[TarenConfig.s_taren] = {
            TarenConfig.k_downloads: self.downloads,
            TarenConfig.k_extension: self.extension,
            TarenConfig.k_logfile: self.logfile,
            TarenConfig.k_logstring: self.logstring,
            TarenConfig.k_maxcache: self.maxcache,
            TarenConfig.k_pattern: self.pattern,
            TarenConfig.k_trash: self.trash,
            TarenConfig.k_trashage: self.trashage,
            TarenConfig.k_wiki: self.wiki
        }
        with open(iniFileName, 'w') as configfile:
            config.write(configfile)

    def init(self: object, iniFileName: str) -> str:
        '''
        Either read existing INI file or create new one with defaults
        '''
        if path.exists(iniFileName):
            self.__read(iniFileName)
        else:
            self.__write(iniFileName)

    def getDownloads(self: object) -> str:
        '''
        Get path to episodes/downloads
        '''
        return self.downloads

    def getExtension(self: object) -> str:
        '''
        Get extension of movies
        '''
        return self.extension

    def getLogfile(self: object) -> str:
        '''
        Get name of logfile
        '''
        return self.logfile

    def getLogstring(self: object) -> str:
        '''
        Get format of logstring
        '''
        return self.logstring

    def getMaxcache(self: object) -> int:
        '''
        Get maximum age in days of cached WIKI article
        '''
        return int(self.maxcache)

    def getPattern(self: object) -> str:
        '''
        Get search pattern to identify episodes/downloads
        '''
        return self.pattern

    def getTrash(self: object) -> str:
        '''
        Get name of trash folder
        '''
        return self.trash

    def getTrashage(self: object) -> int:
        '''
        Get maximum age in days of files in trash folder
        '''
        return int(self.trashage)

    def getWiki(self: object) -> str:
        '''
        Get URL of Wiki article of all Tatort episodes
        '''
        return self.wiki
