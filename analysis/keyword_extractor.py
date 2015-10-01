
import re
import nltk
from stop_words import get_stop_words
import string
import pymongo
from nltk.stem.porter import PorterStemmer
from sklearn import feature_extraction

class KeyWordExtractor(object):

    def __init__(self, documents, analyser=None, text_accessor=lambda x: x, stop_words_list=None):
        """
        Args:
            documents (list<T>):
            analyser (analysis.TFIDFHelper):
            text_accessor (function): function to get text from document object
        """
        self.analyser = analyser or TFIDFHelper(stopwords=stop_words_list, get_text=text_accessor)
        self.vectors = self.analyser.compute_scores(documents)

    def get_keywords(self, document_index, threshold=0.20):
        """
        Args:
            document_index (int): the index of the document. Used to find the
                vector for the words to filter
            threshold (float): TFIDF score to filter by

        Returns:
            a set of keywords
        """
        return set([term for term, weight in self.vectors[document_index]
            if weight >= threshold])

class TFIDFHelper(object):

    def __init__(self, stopwords=None,
                get_text=lambda x: x):
        """
        Input:
            stopwords list<str>: list of terms to ignore
            get_text <function>: text accessor function to retrieve strings.

        """
        self.stopwords = stopwords or set(nltk.corpus.stopwords.words('english') + get_stop_words('english'))
        self.tfidf_transformer = feature_extraction.text.TfidfTransformer()
        self.count_vectorizer = feature_extraction.text.CountVectorizer(
            stop_words=self.stopwords, ngram_range=(1, 1))
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
        return self.count_vectorizer.fit_transform(documents)


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
        self.vocabulary_keys = self.count_vectorizer.vocabulary_.keys()
        self.vocabulary_values = self.count_vectorizer.vocabulary_.values()
        return self._fit_transform(word_counts).toarray()

    def compute_scores(self, documents):
        """
        Args:
            documents list(T) : list of documents
        Returns:
            [[(term, score).....] for each document]
        """
        tfidf_vectors = self.perform_tfidf(documents)
        document_terms = []
        for document in tfidf_vectors:
            terms = []
            for j, score in enumerate(document):
                term = self.vocabulary_keys[self.vocabulary_values.index(j)]
                terms.append((term, score))
            document_terms.append(terms)
        return document_terms

