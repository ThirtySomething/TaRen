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
    def __init__(self):
        '''
        Default is an empty episode for __repr__ method
        '''
        self.episode_id = 0
        self.episode_name = ''
        self.episode_inspectors = ''
        self.episode_broadcast = ''
        self.empty = True

    def __repr__(self):
        '''
        Default string representation of an episode
        '''
        measstring = '{:04d} - {} - {} - {}'.format(self.episode_id, self.episode_broadcast, self.episode_name, self.episode_inspectors)
        return measstring

    def parse(self, data_row):
        '''
        Fill episode object with episode number, name and inspectors. Perform some cleanup on episode name and inspectors.
        '''
        if len(data_row) == 0:
            logging.error('invalid data row %s', '{}'.format(data_row))
            return
        logging.debug('data row %s', '{}'.format(data_row))
        self.episode_id = int(data_row[0].replace('\n', '').strip())
        self.episode_name = re.sub(r'\(Folge [0-9]+(.)+\)', '', data_row[1].replace('\n', '').strip()).strip()
        self.episode_inspectors = re.sub(r'\(Gastauftritt(.)+\)', '', data_row[4].replace('\n', '').strip()).strip()
        self.episode_broadcast = data_row[2].replace('\n', '').strip()
        self.empty = False
