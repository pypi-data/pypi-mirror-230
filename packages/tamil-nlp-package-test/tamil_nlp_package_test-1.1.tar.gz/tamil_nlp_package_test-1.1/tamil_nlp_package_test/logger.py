import logging
log = logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s %(levelname)s: %(lineno)d, %(funcName)s        %(message)s', level=logging.INFO)
logger = logging.getLogger()