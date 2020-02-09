import logging
from bs4 import BeautifulSoup
from episode import Episode
from wikicache import WikiCache

class TaRen:
    def __init__(self, searchdir, pattern, extension, url, cachetime):
        logging.debug('searchdir [{}]'.format(searchdir))
        logging.debug('pattern [{}]'.format(pattern))
        logging.debug('extension [{}]'.format(extension))
        logging.debug('url [{}]'.format(url))
        logging.debug('cachetime [{}]'.format(cachetime))
        self.searchdir = searchdir
        self.pattern = pattern
        self.extension = extension
        self.url = url
        self.cachetime = cachetime
        self.episodes = []
        if (not self.extension.startswith('.')):
            self.extension = '.{}'.format(self.extension)

    def renameProcess(self):
        websitecontent = self.readWebsite()
        self.parseWebsite(websitecontent)
        # list_of_episodes = self.buildListOfEpisodes(list_of_episodes_raw)
        # files = self.collectFilenames()
        # logging.debug('files [{}]'.format(files))
        # logging.debug('content [{}]'.format(self.content))

    def collectFilenames(self):
        searchpattern = '*{}*{}'.format(self.pattern, self.extension)
        files = fnmatch.filter(os.listdir(self.searchdir), searchpattern)
        return files

    def readWebsite(self):
        cache = WikiCache(self.pattern, self.url, self.cachetime)
        return cache.getWebsiteFromCache()

    def parseWebsite(self, websitecontent):
        websitedata = BeautifulSoup(websitecontent, 'html.parser')
        table = websitedata.find('table')
        rows = table.find_all('tr')
        self.episodes = self.buildListOfEpisodes(rows)

    def buildListOfEpisodes(self, raw_data):
        episodes = []
        for tr in raw_data:
            td = tr.find_all('td')
            row = [i.text for i in td]
            currentEpisode = Episode()
            if currentEpisode.parse(row):
                episodes.append(currentEpisode)
                # logging.debug('data_row [{}]'.format(currentEpisode))
        logging.debug('total number of episodes [{}]'.format(len(episodes)))
        return episodes
