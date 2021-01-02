import logging
def config(filename):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    file_handler = logging.FileHandler(filename, 'w')
    file_handler.setLevel(logging.INFO)
    formater = logging.Formatter('%(asctime)s %(message)s')
    file_handler.setFormatter(formater)
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    # global print
    # print = logger.debug

if __name__ == '__main__':
    logging.info('info')
    logging.debug('debug')
    logging.warning('warning')
    logging.error('error')