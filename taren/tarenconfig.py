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

    def __init__(self: object, iniFileName: str = 'program.ini') -> None:
        '''
        Set default values for config
        '''
        self._downloads: str = 'v:\\tatort'
        self._extension: str = 'mp4'
        self._logfile: str = 'program.log'
        self._logstring: str = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s:%(funcName)s | %(message)s'
        self._maxcache: str = '1'
        self._pattern: str = 'Tatort'
        self._trash: str = '.trash'
        self._trashage: str = '3'
        self._wiki: str = 'https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen'
        self.iniFileName: str = iniFileName

    def __read(self: object) -> None:
        '''
        Parse INI file and read values
        '''
        config: configparser.RawConfigParser = configparser.RawConfigParser()
        config.read(self.iniFileName)
        self._downloads = config.get(TarenConfig.s_taren, TarenConfig.k_downloads, fallback=self._downloads)
        self._extension = config.get(TarenConfig.s_taren, TarenConfig.k_extension, fallback=self._extension)
        self._logfile = config.get(TarenConfig.s_taren, TarenConfig.k_logfile, fallback=self._logfile)
        self._logstring = config.get(TarenConfig.s_taren, TarenConfig.k_logstring, fallback=self._logstring)
        self._maxcache = config.get(TarenConfig.s_taren, TarenConfig.k_maxcache, fallback=self._maxcache)
        self._pattern = config.get(TarenConfig.s_taren, TarenConfig.k_pattern, fallback=self._pattern)
        self._trash = config.get(TarenConfig.s_taren, TarenConfig.k_trash, fallback=self._trash)
        self._trashage = config.get(TarenConfig.s_taren, TarenConfig.k_trashage, fallback=self._trashage)
        self._wiki = config.get(TarenConfig.s_taren, TarenConfig.k_wiki, fallback=self._wiki)

    def __write(self: object) -> None:
        '''
        Write INI file with values
        '''
        config: configparser.RawConfigParser = configparser.RawConfigParser()
        config[TarenConfig.s_taren] = {
            TarenConfig.k_downloads: self._downloads,
            TarenConfig.k_extension: self._extension,
            TarenConfig.k_logfile: self._logfile,
            TarenConfig.k_logstring: self._logstring,
            TarenConfig.k_maxcache: self._maxcache,
            TarenConfig.k_pattern: self._pattern,
            TarenConfig.k_trash: self._trash,
            TarenConfig.k_trashage: self._trashage,
            TarenConfig.k_wiki: self._wiki
        }
        with open(self.iniFileName, 'w') as configfile:
            config.write(configfile)

    def init(self: object) -> str:
        '''
        Either read existing INI file or create new one with defaults
        '''
        if os.path.exists(self.iniFileName):
            self.__read()
        else:
            self.__write()

    @property
    def downloads(self: object) -> str:
        '''
        Get path of downloads
        '''
        return self._downloads

    @downloads.setter
    def downloads(self: object, value: str) -> None:
        '''
        Set path of downloads
        '''
        self._downloads = value

    @property
    def extension(self: object) -> str:
        '''
        Get extension of movies
        '''
        return self._extension

    @extension.setter
    def extension(self: object, value: str) -> None:
        '''
        Set extension of movies
        '''
        self._extension = value

    @property
    def logfile(self: object) -> str:
        '''
        Get name of logfile
        '''
        return self._logfile

    @logfile.setter
    def logfile(self: object, value: str) -> None:
        '''
        Get name of logfile
        '''
        self._logfile = value

    @property
    def logstring(self: object) -> str:
        '''
        Get format of logstring
        '''
        return self._logstring

    @logstring.setter
    def logstring(self: object, value: str) -> None:
        '''
        Set format of logstring
        '''
        self._logstring = value

    @property
    def maxcache(self: object) -> int:
        '''
        Get maximum age in days of cached WIKI article
        '''
        return int(self._maxcache)

    @maxcache.setter
    def maxcache(self: object, value: int) -> None:
        '''
        Set maximum age in days of cached WIKI article
        '''
        self._maxcache = value

    @property
    def pattern(self: object) -> str:
        '''
        Get search pattern to identify episodes/downloads
        '''
        return self._pattern

    @pattern.setter
    def pattern(self: object, value: str) -> None:
        '''
        Set search pattern to identify episodes/downloads
        '''
        self._pattern = value

    @property
    def trash(self: object) -> str:
        '''
        Get name of trash folder
        '''
        return self._trash

    @trash.setter
    def trash(self: object, value: str) -> str:
        '''
        Set name of trash folder
        '''
        self._trash = value

    @property
    def trashage(self: object) -> int:
        '''
        Get maximum age in days of files in trash folder
        '''
        return int(self._trashage)

    @trashage.setter
    def trashage(self: object, value: int) -> None:
        '''
        Set maximum age in days of files in trash folder
        '''
        self._trashage = value

    @property
    def wiki(self: object) -> str:
        '''
        Get URL of Wiki article of all Tatort episodes
        '''
        return self._wiki

    @wiki.setter
    def wiki(self: object, value: str) -> None:
        '''
        Set URL of Wiki article of all Tatort episodes
        '''
        self._wiki = value

    def configurationLoad(self: object) -> None:
        '''
        Load configuration from file
        '''
        self.__read()

    def configurationSave(self: object) -> None:
        '''
        Save configuration from file
        '''
        self.__write()
