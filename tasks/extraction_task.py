import datetime
import threading
import Queue
import nltk
from stop_words import get_stop_words
from vaderSentiment import vaderSentiment

from collection import models
import task
from analysis.keyword_extractor import KeyWordExtractor, AlchemyApiKeywordExtractor


class ExtractionTask(task.Task):
    """ Extracts sentiment analysis scores and keywords """

    @staticmethod
    def execute():
        start = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        match = {'$match': {'created': {'$gte': start}, 'college': 'Georgia Tech'}}
        group = {'$group': {'_id': '$college', 'posts': {'$push': '$_id'}}}
        query_result = {college['_id']: college['posts']
                        for college in models.Submission.objects.aggregate(match, group)}
        q = Queue.Queue()
        # Having each thread independently load the stop word list causes an error so we just do it
        # here and pass it into the threads.
        stop_words_list = set(
            nltk.corpus.stopwords.words('english') + get_stop_words('english'))
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
            # corpus_unigram_list = KeyWordExtractor.get_keywords(corpus, text_accessor=lambda x: x.get_content(),
            #                                      stop_words_list=self.stop_words_list, ngram_range=(1, 1))
            # corpus_bigram_list = KeyWordExtractor.get_keywords(corpus, text_accessor=lambda x: x.get_content(),
            #                                      stop_words_list=self.stop_words_list, ngram_range=(2, 2))
            # for document, unigrams, bigrams in zip(corpus, corpus_unigram_list, corpus_bigram_list):
            #     if not document.pos and document.content:
            #         sentiment = vaderSentiment.sentiment(document.content.encode('utf8'))
            #         document.pos = sentiment['pos']
            #         document.neu = sentiment['neu']
            #         document.neg = sentiment['neg']
            #     finalized_keywords = set([term for term, value in unigrams])
            #     bigrams = list(bigrams)
            #     bigrams.sort(key=lambda x: x[1], reverse=True)
            #     for bigram in [term for term, value in bigrams]:
            #         first, second = bigram.split(' ')
            #         if first in finalized_keywords and second in finalized_keywords:
            #             merged_term = ' '.join([first, second])
            #             if merged_term in document.content:
            #                 finalized_keywords.discard(first)
            #                 finalized_keywords.discard(second)
            #                 finalized_keywords.add(merged_term)
            keyword_sets = AlchemyApiKeywordExtractor.get_keywords(corpus, text_accessor=lambda x: x.get_content())
            for document, keywords in zip(corpus, keyword_sets):
                document.keywords = list(keywords)
                document.save()
            task.logger.info('Finished {} {} submissions'.format(self.college, len(corpus)))
            self.q.task_done()

if __name__ == '__main__':
    ExtractionTask.execute()