import nltk
import config

class Classifier(object):
    """ Interface """

    def classify(submission):
        raise NotImplementedError()


    def classifyAccuracy(submission):
        raise NotImplementedError()
    
class SimpleClassifier(object):

    def classify(self, submission):
        tokens = nltk.tokenize.word_tokenize(submission.content)
        for word in tokens:
            if word in config.keywords:
                return True
        return False

    def computeAccuracy(self, arraySamples):
        countSamples = 0.0;
        numLabelled = 0.0;
        for submission in arraySamples:
            tokens = nltk.tokenize.word_tokenize(submission.content)
            countSamples += 1
            for word in tokens:
                if word in config.keywords:
                    if submission.label:
                        numLabelled += 1
                    break
        return numLabelled/countSamples        


