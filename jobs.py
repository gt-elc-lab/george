from collection import config
from collection.crawler import MultiThreadedCrawler
from collection.dao import MongoDao
from analysis.keyword_extractor import KeyWordExtractor
from analysis.sentiment_analysis import SentimentHelper

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
        return

class CrawlTask(Task):
    """ Task for scraping reddit """
    @staticmethod
    def execute():
        MultiThreadedCrawler(config.SUBREDDITS).start()

class MainJob(object):

    def __init__(self, tasks):
        """
            Args:
                task (list<jobs.Task>):
        """
        self.tasks = tasks

    def run(self):
        """ Run all of the tasks """
        for task in self.tasks:
            try:
                task.execute()
            except Exception as e:
                print e

if __name__ == '__main__':
    MainJob([CrawlTask]).run()