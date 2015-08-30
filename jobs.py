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
        instantiatedDao = MongoDao()
		docsThatDontHaveKeyword = instatiatedDao.post_exist(["keywords", "sentiment"])
		for post in docsThatDontHaveKeyword:
			post.comments = map(instantiatedDao.get_comment, post.comments)
			combinedList = [post]+post.comments
			instantiatedKeywordExtractor = KeyWordExtractor(combinedList)
			for index, document in enumerate(combinedList):
				keywords = instantiatedKeywordExtractor.get_keywords(index)
				document.keywords = keywords
				if isinstance(document, models.Post):
					dao.insert_post(document.to_record())
				else: 
					dao.insert_comment(document.to_record())
					
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