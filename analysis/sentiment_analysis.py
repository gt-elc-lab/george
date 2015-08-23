import vaderSentiment

class SentimentHelper(object):

    def __init__(self):
        return

    def compute_sentiment(self, text):
        """
            Input:
                text <string> : text on which sentiment analysis will be computed

            Returns:
                dictionary of sentiment score of sentence given from vader
        """
        return vaderSentiment.sentiment(text)