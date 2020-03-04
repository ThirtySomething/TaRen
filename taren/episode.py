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

import logging
import re


class Episode:
    '''
    Object with episode information. Retrieve data from given data row, do some
    cleanup and represents the default episode name in __repr__ method.
    '''

    # Invalid characters inside filenames on Windows
    invalid_characters = ['"', '*', '<', '>', '?', '\\', '|', '/', ':']

    def __init__(self):
        '''
        Default is an empty episode for __repr__ method
        '''
        self.episode_id = 0
        self.episode_name = ''
        self.episode_inspectors = ''
        self.episode_broadcast = ''
        self.empty = True

    def __gt__(self, other):
        '''
        Used for sorting
        '''
        if isinstance(other, Episode):
            return self.__repr__() > other.__repr__()
        raise Exception("Cannot compare Episode to Not-A-Episode")

    def __repr__(self):
        '''
        Default string representation of an episode
        '''
        measstring = 'Tatort - {:04d} - {} - {} - {}'.format(self.episode_id, self.episode_broadcast, self.episode_name, self.episode_inspectors)
        return measstring

    def _strip_invalid_characters(self):
        '''
        Remove characters which are invalid for filenames
        '''
        for current_invalid_character in Episode.invalid_characters:
            self.episode_broadcast = self.episode_broadcast.replace(current_invalid_character, ' ').strip()
            self.episode_inspectors = self.episode_inspectors.replace(current_invalid_character, ' ').strip()
            self.episode_name = self.episode_name.replace(current_invalid_character, ' ').strip()

    def parse(self, data_row):
        '''
        Fill episode object with episode number, name and inspectors. Perform some cleanup on episode name and inspectors.
        '''
        if len(data_row) == 0:
            return
        logging.debug('data row %s', '{}'.format(data_row))
        # Episode number is first element of row
        episode_id_raw = re.search(r'([0-9]+)', data_row[0])
        self.episode_id = int(episode_id_raw.group(1))
        # Episode name is second element of row, strip unwanted information like '(Folge 332 tr�gt den gleichen Titel)' using regexp
        self.episode_name = re.sub(r'\(Folge [0-9]+(.)+\)', '', data_row[1].strip()).strip()
        # Inspectors of episode, 5th element of row, strip unwanted information like '(Gastauftritt Trimmel und Kreutzer)' using regexp
        self.episode_inspectors = re.sub(r'\(Gastauftritt(.)+\)', '', data_row[4].strip()).strip()
        # Get name of broadcast station, 3rd element of row
        self.episode_broadcast = data_row[2].strip()
        # Strip invalid characters
        self._strip_invalid_characters()
        # Mark as not empty
        self.empty = False

    def matches(self, filename):
        '''
        Check if episode matches the filename
        '''
        # Check leading episode number => download marked as special episode manually
        filename_match = re.search(r'(^[0-9]{4} )', filename)
        if filename_match:
            filename_id = int(filename_match.group(1))
            # logging.debug('match filename [%s] by id [%s|%s] = [%s]', '{}'.format(filename), '{}'.format(filename_id), '{}'.format(self.episode_id), '{}'.format(match))
            return self.episode_id == filename_id

        # Check episode prefix with number => alredy handled by TaRen
        filename_match = re.search(r'^(Tatort - ([0-9]{4}) )', filename)
        if filename_match:
            filename_id = int(filename_match.group(2))
            # logging.debug('match filename [%s] by id [%s|%s] = [%s]', '{}'.format(filename), '{}'.format(filename_id), '{}'.format(self.episode_id), '{}'.format(match))
            return self.episode_id == filename_id

        # Last check => Is episode name part of filename
        # logging.debug('match filename [%s] by episode_name [%s] = [%s]', '{}'.format(filename), '{}'.format(self.episode_name), '{}'.format(match))
        return self.episode_name.lower() in filename.lower()
