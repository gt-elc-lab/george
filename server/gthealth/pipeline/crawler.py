from datetime import datetime
import praw

from gthealth import config
import classifier
import model

class Crawler(object):

    def __init__(self, classifier):
        self.classifier = classifier

    def run(self, subreddit='depression'):
        r = praw.Reddit(user_agent='gthealth')
        posts = map(Crawler.post_from_praw_submission,
            r.get_subreddit(subreddit).get_new(limit=20))
        for post in filter(self.classifier.classify, posts):
            post.save()

    @staticmethod
    def sample_from_praw_submission(submission):
        return model.Sample(r_id=submission.id,
                            title = submission.title,
                            content=submission.selftext,
                            date=datetime.utcfromtimestamp(
                                submission.created_utc),
                            subreddit=submission.subreddit.display_name)


    @staticmethod
    def post_from_praw_submission(submission):
        return model.Post(r_id=submission.id,
                          content=submission.selftext,
                          title=submission.title,
                          created=datetime.utcfromtimestamp(
                            submission.created_utc))

def download_corpus():
    """ Performs a search for depression related posts on all of our subreddits"""
    r = praw.Reddit(user_agent='gthealth')
    for school in config.SUBREDDITS:
        print 'Searching posts from %s' % (school['name'])
        query = ' OR '.join(config.keywords)
        samples = map(Crawler.sample_from_praw_submission,
            r.search(query, subreddit=school['subreddit'], limit=1000))
        print 'found %d results' % (len(samples))
        for sample in samples:
            sample.save()
    return


if __name__ == '__main__':
    Crawler(classifier.SimpleClassifier()).run()
