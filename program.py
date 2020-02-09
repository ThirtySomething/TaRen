'''Script to rename files downloaded with MediathekView to a specific format
'''

from taren import TaRen

import logging

# logging.basicConfig(
#     filename='program.log',
#     level=logging.DEBUG,
#     filemode='w',
#     encoding='UTF-8',
#     format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s:%(funcName)s | %(message)s'
# )

# Setup logging for dealing with UTF-8, unfortunately not available for basicConfig
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('program.log', 'w', 'utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s:%(funcName)s | %(message)s'))
root_logger.addHandler(handler)


if __name__ == '__main__':
    logging.debug('startup')

    data = TaRen('V:', 'Tatort', 'mp4', 'https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen', 1)
    data.renameProcess()
