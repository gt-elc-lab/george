import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

class KeyWordExtractor(object):

    def __init__(self):
        """
        Args:

        """
    @staticmethod
    def get_keywords(documents, text_accessor=lambda x: x, threshold=0.2, stop_words_list=None, ngram_range=(1, 1)):
        """
        Args:
            documents list(<T>):

        Returns:
            a set of keywords
        """
        tfidf_vectorizer = TfidfVectorizer(stop_words=stop_words_list, ngram_range=ngram_range)
        corpus = [text_accessor(doc) for doc in documents]
        matrix = tfidf_vectorizer.fit_transform(corpus)
        features = tfidf_vectorizer.get_feature_names()
        document_terms = []
        for vector in matrix:
            terms = [(features[feature_index], weight) for feature_index, weight in zip(vector.indices, vector.data)
                     if weight > threshold]
            document_terms.append(set(terms))
        return document_terms

    @staticmethod
    def stem_tokens(tokens, stemmer):
        return [stemmer.stem(item) for item in tokens]

    @staticmethod
    def tokenize(text):
        return nltk.word_tokenize(text)


class POSTagger(object):
    """ Performs POS tagging against a given document"""
    
    def __init__(self):
        return

    def _tag_sentence(self, sentence):
        return nltk.tag.pos_tag(nltk.tokenize.word_tokenize(sentence))

    def _tokenize_sentences(self, document):
        return nltk.tokenize.sent_tokenize(document)

    def perform_pos_tagging(self, document, tag_prefix=""):
        sentences = self._tokenize_sentences(document)
        tagged_text = []
        for sentence in sentences:
            tagged_text = tagged_text + (self._tag_sentence(sentence))
        return [word for (word, tag) in tagged_text if tag.startswith(tag_prefix)]