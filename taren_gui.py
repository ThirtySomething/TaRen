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

import logging.config
import logging
from taren.taren import TaRen
import PySimpleGUI as sg
import json
from taren.tarenconfig import TarenConfig

confvisible = False
width_Label = 20
width_Field = 50

TAREN_CONFIG = TarenConfig('program.ini')
TAREN_CONFIG.init()

# Setup logging for dealing with UTF-8, unfortunately not available for basicConfig
LOGGER_SETUP = logging.getLogger()
LOGGER_SETUP.setLevel(logging.INFO)
# LOGGER_SETUP.setLevel(logging.DEBUG)
LOGGER_HANDLER = logging.FileHandler(TAREN_CONFIG.logfile, 'w', 'utf-8')
LOGGER_HANDLER.setFormatter(logging.Formatter(TAREN_CONFIG.logstring))
LOGGER_SETUP.addHandler(LOGGER_HANDLER)


def collapse(layout, key, visible):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this section visible / invisible
    :param visible: visible determines if section is rendered visible or invisible on initialization
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key, visible=visible, pad=(0, 0)))


def tarenConfigLoad():
    TAREN_CONFIG.configurationLoad()
    window.find_element('-downloads-').Update(TAREN_CONFIG.downloads)
    window.find_element('-extension-').Update(TAREN_CONFIG.extension)
    window.find_element('-logfile-').Update(TAREN_CONFIG.logfile)
    window.find_element('-logstring-').Update(TAREN_CONFIG.logstring)
    window.find_element('-maxcache-').Update(TAREN_CONFIG.maxcache)
    window.find_element('-pattern-').Update(TAREN_CONFIG.pattern)
    window.find_element('-trash-').Update(TAREN_CONFIG.trash)
    window.find_element('-trashage-').Update(TAREN_CONFIG.trashage)
    window.find_element('-wiki-').Update(TAREN_CONFIG.wiki)


def tarenConfigSave(values):
    TAREN_CONFIG.downloads = values['-downloads-']
    TAREN_CONFIG.extension = values['-extension-']
    TAREN_CONFIG.logfile = values['-logfile-']
    TAREN_CONFIG.logstring = values['-logstring-']
    TAREN_CONFIG.maxcache = int(values['-maxcache-'])
    TAREN_CONFIG.pattern = values['-pattern-']
    TAREN_CONFIG.trash = values['-trash-']
    TAREN_CONFIG.trashage = int(values['-trashage-'])
    TAREN_CONFIG.wiki = values['-wiki-']
    TAREN_CONFIG.configurationSave()
    tarenConfigToggle(True)


def tarenConfigToggle(confvisible):
    if not confvisible:
        tarenConfigLoad()
    window['-taren-'].update(visible=confvisible)
    window['-conf-'].update(visible=(not confvisible))


def tarenProcess():
    logging.debug('startup')

    # logging.info('debugFlag is set to [%s]', '{}'.format(debugFlag))

    # Initialize program with
    # - Location of downloads
    # - Search pattern
    # - File extension
    # - URL to list of episodes
    # - Maximum age in days of cache file
    # - Trash folder
    # - Days to keep downloads/episodes in trash folder
    DATA = TaRen(
        TAREN_CONFIG.downloads,
        TAREN_CONFIG.pattern,
        TAREN_CONFIG.extension,
        TAREN_CONFIG.wiki,
        TAREN_CONFIG.maxcache,
        TAREN_CONFIG.trash,
        TAREN_CONFIG.trashage
    )

    # Start magic process :D
    DATA.rename_process()

    # Display logfile
    with open(TAREN_CONFIG.logfile, 'r') as protocolfile:
        processprotocol = protocolfile.readlines()
        for messageline in processprotocol:
            window.find_element('-result-').Update(messageline, append=True)


def_menu = [['Datei', ['Exit']],
            ['Bearbeiten', ['Einstellungen'], ],
            ['Über', 'TaRen'], ]

def_taren = [[sg.T('Ausgabe:'), sg.T('', size=(width_Field, 1)), sg.B('Start', key='-btn-start-')],
             [sg.Multiline(size=(2*width_Field, 20), key='-result-')],
             ]

def_conf = [[sg.T('Download Verzeichnis', size=(width_Label, 1)), sg.I(key='-downloads-', size=(width_Field, 1), enable_events=True), sg.FolderBrowse('...')],  # sg.B('...', key='-btn-dir-')],
            [sg.T('Dateiendung Film', size=(width_Label, 1)), sg.I(key='-extension-', size=(width_Field, 1))],
            [sg.T('Name Logfile', size=(width_Label, 1)), sg.I(key='-logfile-', size=(width_Field, 1))],
            [sg.T('Loggingstring', size=(width_Label, 1)), sg.I(key='-logstring-', size=(width_Field, 1))],
            [sg.T('Alter Cache (in Tagen)', size=(width_Label, 1)), sg.I(key='-maxcache-', size=(width_Field, 1))],
            [sg.T('Suchmaske', size=(width_Label, 1)), sg.I(key='-pattern-', size=(width_Field, 1))],
            [sg.T('Name Papierkorb', size=(width_Label, 1)), sg.I(key='-trash-', size=(width_Field, 1))],
            [sg.T('Alter Papierkorb (in Tagen)', size=(width_Label, 1)), sg.I(key='-trashage-', size=(width_Field, 1))],
            [sg.T('Liste der Tatortfolgen', size=(width_Label, 1)), sg.I(key='-wiki-', size=(width_Field, 1))],
            [sg.B('Reload', key='-btn-reload-'), sg.B('Speichern', key='-btn-save-')]
            ]


def_about = [[sg.T('TaRen GUI')],
             [sg.T('(C) 2021 by ThirtySomething')],
             [sg.T('https://github.com/ThirtySomething/TaRen')],
             [sg.Push(), sg.Button('OK')]
             ]

def_layout = [
    [sg.Menu(def_menu, tearoff=True)],
    [collapse(def_taren, '-taren-', True)],
    [collapse(def_conf, '-conf-', False)], ]

window = sg.Window('TaRen GUI', def_layout)

while True:
    # Read events and optional values
    event, values = window.read()

    # 1st check events
    if event == sg.WIN_CLOSED:
        break
    elif (event == '-btn-start-'):
        tarenProcess()
    elif (event == '-btn-reload-'):
        tarenConfigLoad()
    elif (event == '-btn-save-'):
        tarenConfigSave(values)

    # 2nd check values
    if (values[0] == 'Exit'):
        break
    elif (values[0] == 'Einstellungen'):
        tarenConfigToggle(confvisible)
        confvisible = not confvisible
    elif (values[0] == 'TaRen'):
        sg.Window('About', def_about, modal=True).read(close=True)

    logging.debug('Event [%s]', '{}'.format(json.dumps(event)))
    logging.debug('Values [%s]', '{}'.format(json.dumps(values)))

window.close()
