import re
from vaderSentiment.vaderSentiment import sentiment as vader

class SentimentHelper(object):

    def __init__(self):
        return

    @staticmethod
    def compute_sentiment(text):
        """
        Get sentiment analysis scores for the given text.
        Args:
            text (str) : text on which sentiment analysis will be computed

        Returns:
            dictionary of sentiment scores
        """
        return vader(text.encode('utf8'))