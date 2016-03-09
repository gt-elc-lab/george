import nltk

from gthealth import config
from gthealth import model

class Classifier(object):
    """ Interface """

    def classify(submission):
        raise NotImplementedError()


class SimpleClassifier(Classifier):

    def classify(self, submission):
        tokens = nltk.tokenize.word_tokenize(submission.content)
        for word in tokens:
            if word in config.keywords:
                return True
        return False

def test_classifier(classifier, samples):
    correct = sum(1.0 for sample in samples
        if sample.label == classifier.classify(sample))
    return correct / len(samples)


if __name__ == '__main__':
    samples = model.Sample.objects(label__exists=True)
    print test_classifier(SimpleClassifier(), samples)
