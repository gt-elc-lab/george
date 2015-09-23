import datetime

from collection import config
from collection import models
from collection.crawler import MultiThreadedCrawler
from collection.dao import MongoDao
from analysis.keyword_extractor import KeyWordExtractor

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
        mongo_dao = MongoDao()
        unanalysed_documents = mongo_dao.post_keys_exist(["keywords"])
        for post in unanalysed_documents:
            comments = mongo_dao.get_post_comments(post._id)
            corpus = [post] + comments
            corpus = filter(lambda x: x.text, corpus)
            if corpus:
                try:
                    keyword_extractor = KeyWordExtractor(corpus)
                    for index, document in enumerate(corpus):
                        keywords = list(keyword_extractor.get_keywords(index))
                        document.keywords = keywords
                        mongo_dao.insert_post(document.to_record())
                except Exception as e:
                    print e

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
    MainJob([CrawlTask, ExtractionTask]).run()