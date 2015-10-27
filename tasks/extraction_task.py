import datetime
import threading
import Queue
import nltk
from stop_words import get_stop_words

from collection import models
import task
from analysis.keyword_extractor import KeyWordExtractor

class ExtractionTask(task.Task):
    """ Extracts sentiment analysis scores and keywords """

    @staticmethod
    def execute():
        start = datetime.datetime.utcnow() - datetime.timedelta(days=3)
        match = {'$match': {'created': {'$gte': start}}}
        group = {'$group': {'_id': '$college', 'posts': {'$push': '$_id'}}}
        query_result = {college['_id']: college['posts']
                        for college in models.Submission.objects.aggregate(match, group)}
        q = Queue.Queue()
        # Having each thread independently load the stop word list causes an error so we just do it
        # here and pass it into the threads.
        stop_words_list = set(nltk.corpus.stopwords.words('english') + get_stop_words('english'))
        for college in query_result:
            worker = ExtractionWorker(college, q, stop_words_list)
            worker.daemon = True
            worker.start()
        for corpus in query_result.itervalues():
            documents = models.Submission.objects(r_id__in=corpus)
            corpus = [doc for doc in documents if doc.get_content()]
            if corpus:
                q.put(corpus)
        q.join()

class ExtractionWorker(threading.Thread):
    def __init__(self, college, q, stop_words_list):
        threading.Thread.__init__(self)
        self.q = q
        self.college = college
        self.stop_words_list = stop_words_list
        return

    def run(self):
        task.logger.info('Starting {}'.format(self.college))
        while True:
            corpus = self.q.get()
            unigram_list = KeyWordExtractor.get_keywords(corpus, text_accessor=lambda x: x.get_content(),
                                                 stop_words_list=self.stop_words_list, ngram_range=(1, 1))
            for document, unigrams in zip(corpus, unigram_list):
                keywords = {unigram: value for unigram, value in unigrams}
                document.keywords = [keyword for keyword in keywords]
                document.save()
            task.logger.info('Finished {} {} submissions'.format(self.college, len(corpus)))
            self.q.task_done()

if __name__ == '__main__':
    ExtractionTask.execute()