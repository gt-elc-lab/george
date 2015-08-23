from vaderSentiment import vaderSentiment

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
        return vaderSentiment.sentiment(text)