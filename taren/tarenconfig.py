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
    Build list of filenames
    '''

    s_taren = 'TaRen'
    k_downloads = 'downloads'
    k_extension = 'extension'
    k_logfile = 'logfile'
    k_logstring = 'logstring'
    k_maxcache = 'maxcache'
    k_pattern = 'pattern'
    k_wiki = 'wiki'

    def __init__(self):
        self.downloads = 'v:\\tatort'
        self.extension = 'mp4'
        self.logfile = 'program.log'
        self.logstring = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s:%(funcName)s | %(message)s'
        self.maxcache = '1'
        self.pattern = 'Tatort'
        self.wiki = 'https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen'

    def __read(self, iniFileName):
        config = configparser.RawConfigParser()
        config.read(iniFileName)
        self.downloads = config.get(TarenConfig.s_taren, TarenConfig.k_downloads)
        self.extension = config.get(TarenConfig.s_taren, TarenConfig.k_extension)
        self.logfile = config.get(TarenConfig.s_taren, TarenConfig.k_logfile)
        self.logstring = config.get(TarenConfig.s_taren, TarenConfig.k_logstring)
        self.maxcache = config.get(TarenConfig.s_taren, TarenConfig.k_maxcache)
        self.pattern = config.get(TarenConfig.s_taren, TarenConfig.k_pattern)
        self.wiki = config.get(TarenConfig.s_taren, TarenConfig.k_wiki)

    def __write(self, iniFileName):
        config = configparser.RawConfigParser()
        config[TarenConfig.s_taren] = {
            TarenConfig.k_downloads: self.downloads,
            TarenConfig.k_extension: self.extension,
            TarenConfig.k_logfile: self.logfile,
            TarenConfig.k_logstring: self.logstring,
            TarenConfig.k_maxcache: self.maxcache,
            TarenConfig.k_pattern: self.pattern,
            TarenConfig.k_wiki: self.wiki
        }
        with open(iniFileName, 'w') as configfile:
            config.write(configfile)

    def init(self, iniFileName):
        if path.exists(iniFileName):
            self.__read(iniFileName)
        else:
            self.__write(iniFileName)

    def getDownloads(self):
        return self.downloads

    def getExtension(self):
        return self.extension

    def getLogfile(self):
        return self.logfile

    def getLogstring(self):
        return self.logstring

    def getMaxcache(self):
        return int(self.maxcache)

    def getPattern(self):
        return self.pattern

    def getWiki(self):
        return self.wiki
