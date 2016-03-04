import logging

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

class Task(object):
    """ Abstract class for defining tasks """

    def __init__(self):
        return

    @staticmethod
    def execute():
        raise NotImplementedError()