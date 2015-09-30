import datetime
import sys

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
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(days=3)
        match = {'$match': {
            '$or': [
                {'keywords': {'$exists': False}},
                {'created_utc': {'$gte': start, '$lte': end}},
            ]
        }}
        group = {'$group': {
            '_id': '$college',
            'posts': {'$push': '$$ROOT'}
        }}
        pipeline = [match, group]
        # Query matches post that do not have a keyword or were crawled within the last three days.
        # By mixing the two we ensure that we the scores returned by tfidf are more relevant.
        # In addition the keywords that we attach to documents will become much better the longer
        # they are in the pipeline.
        query_result = mongo_dao.post_collection.aggregate(pipeline)
        for college in query_result:
            documents = map(models.Post.from_record, college['posts'])
            corpus = [doc for doc in documents if doc.body]
            # Only perform keyword extraction if there are documents. Otherwise the keyword
            # extractor will error.
            if corpus:
                keyword_extractor = KeyWordExtractor(corpus, text_accessor=lambda x: x.body)
                for index, document in enumerate(corpus):
                    document.keywords = list(keyword_extractor.get_keywords(index))
                    mongo_dao.insert(document.to_record())


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
