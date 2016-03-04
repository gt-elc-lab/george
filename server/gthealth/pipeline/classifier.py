import nltk
import config

class Classifier(object):
    """ Interface """

    def classify(submission):
        raise NotImplementedError()

class SimpleClassifier(object):

    def classify(self, submission):
        tokens = nltk.tokenize.word_tokenize(submission.content)
        for word in tokens:
            if word in config.keywords:
                return True
        return False

