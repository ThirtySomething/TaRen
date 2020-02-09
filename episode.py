import logging
import re

class Episode:
    def __init__(self):
        self.episode_id = 0
        self.episode_name = ''
        self.episode_inspectors = ''

    def parse(self, data_row):
        if len(data_row) == 0:
            # logging.debug('invalid data row [{}]'.format(data_row))
            return False
        # logging.debug('data row [{}]'.format(data_row))
        self.episode_id = int(data_row[0].replace('\n', '').strip())
        self.episode_name = re.sub(r'\(Folge [0-9]+(.)+\)', '', data_row[1].replace('\n', '').strip()).strip()
        self.episode_inspectors = re.sub(r'\(Gastauftritt(.)+\)', '', data_row[4].replace('\n', '').strip()).strip()
        return True

    def __repr__(self):
        measstring = '{:04d} - {} - {}'.format(self.episode_id, self.episode_name, self.episode_inspectors)
        return measstring
