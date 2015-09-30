import datetime
import sys

from collection import config
from collection import models
from collection.crawler import MultiThreadedCrawler
from collection.dao import MongoDao
from route_handlers import MultiThreadedExtraction

class Task(object):
    """ Abstract class for defining tasks """

    def __init__(self):
        return

    @staticmethod
    def execute():
        raise NotImplementedError()

class ExtractionTask(Task):
    """ Extracts sentiment analysis scores and keywords """
    @staticmethod
    def execute():
        MultiThreadedExtraction(config.SUBREDDITS).start()

class CrawlTask(Task):
    """ Task for scraping reddit """
    @staticmethod
    def execute():
        MultiThreadedCrawler(config.SUBREDDITS).start()

if __name__ == '__main__':
    argument = sys.argv[1:]
    if len(argument) > 1:
        print 'Too many arguments, exiting.'
        exit()
    task = argument[0]
    if task == "crawl":
        CrawlTask.execute()
    elif task == "extract":
        ExtractionTask.execute()
    else:
        print 'Unrecognized arguments, exiting'
        exit()