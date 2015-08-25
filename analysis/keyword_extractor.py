
import re
import nltk
import string
import pymongo
from nltk.stem.porter import PorterStemmer
from sklearn import feature_extraction

class KeyWordExtractor(object):

    def __init__(self, analyser=None):
        self.analyser = analyser or TFIDFHelper(get_text=lambda x: x.text)

    def get_scores(self, documents):
        return self.analyser.perform_tfidf(documents)

class TFIDFHelper(object):

    def __init__(self, stopwords=nltk.corpus.stopwords.words('english'),
                get_text=lambda x: x):
        """
        Input:
            stopwords list<str>: list of terms to ignore
            get_text <function>: text accessor function to retrieve strings.

        """
        self.stopwords = set(stopwords)
        self.tfidf_transformer = feature_extraction.text.TfidfTransformer()
        self.cv = feature_extraction.text.CountVectorizer(
            stop_words=stopwords, ngram_range=(1,1))
        self.get_text = get_text
        self.vocabulary_keys = None
        self.vocabulary_values = None
        return

    def _count_vectorize(self, documents):
        """

        Args:
            documents list(str): list of documents

        Returns:

        """
        return self.cv.fit_transform(documents)


    def _fit_transform(self, vectors):
        """

        Args:
            vectors:

        Returns:

        """
        return self.tfidf_transformer.fit_transform(vectors)


    def perform_tfidf(self, documents):
        """

        Args:
            documents list(T) : list of documents

        Returns:

        """
        word_counts = self._count_vectorize(
            [self.get_text(document) for document in documents])
        self.vocabulary_keys = self.cv.vocabulary_.keys()
        self.vocabulary_values = self.cv.vocabulary_.values()
        return self._fit_transform(word_counts).toarray()

    def compute_scores(self, documents, threshold=0.25):
        """
        Args:
            documents list(T) : list of documents
        Returns:
            [[(term, score).....] for each document]
        """
        tfidf_vectors = self.perform_tfidf(documents)
        document_terms = []
        for i, document in enumerate(tfidf_vectors):
            terms = []
            for j, score in enumerate(document):
                term = self.vocabulary_keys[self.vocabulary_values.index(j)]
                terms.append((term, score))
            document_terms.append(terms)
        return document_terms

