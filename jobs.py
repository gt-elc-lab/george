import datetime
import logging
import threading
import sys
import Queue
import nltk
from stop_words import get_stop_words

from collection import config
from collection import models
from collection.crawler import MultiThreadedCrawler
from collection.dao import MongoDao
from analysis.keyword_extractor import KeyWordExtractor

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

class ExtractionTask(Task):
    """ Extracts sentiment analysis scores and keywords """
    @staticmethod
    def execute():
        mongo_dao = MongoDao()
        start = datetime.datetime.utcnow()- datetime.timedelta(days=1)
        match = {'$match': {
            '$and': [
                {'keywords': {'$exists': False}},
                {'created_utc': {'$gte': start}},
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
        query_result = list(mongo_dao.post_collection.aggregate(pipeline))
        q = Queue.Queue()
        # Having each thread independently load the stop word list causes an error so we just do it
        # here and pass it into the threads.
        stop_words_list = set(nltk.corpus.stopwords.words('english') + get_stop_words('english'))
        for college in query_result:
            worker = ExtractionWorker(college['_id'], MongoDao(), q, stop_words_list)
            worker.daemon = True
            worker.start()
        for college in query_result:
            documents = map(models.Post.from_record, college['posts'])
            corpus = [doc for doc in documents if doc.body]
            if corpus:
                q.put(corpus)
        q.join()

class CrawlTask(Task):
    """ Task for scraping reddit """
    @staticmethod
    def execute():
        MultiThreadedCrawler(config.SUBREDDITS).start()
        return

class ExtractionWorker(threading.Thread):
    def __init__(self, college, dao, q, stop_words_list):
        threading.Thread.__init__(self)
        self.dao = dao
        self.q = q
        self.college = college
        self.stop_words_list = stop_words_list
        return

    def run(self):
        while True:
            logger.info('Starting {}'.format(self.college))
            corpus = self.q.get()
            keyword_extractor = KeyWordExtractor(corpus, text_accessor=lambda x: x.body,
                                                 stop_words_list=self.stop_words_list)
            for index, document in enumerate(corpus):
                document.keywords = list(keyword_extractor.get_keywords(index))
                self.dao.insert(document.to_record())
            logger.info('Finished {} {} submissions'.format(self.college, len(corpus)))
            self.q.task_done()



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
