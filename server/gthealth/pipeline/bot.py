import praw
from gthealth import config
import random
import string

class RedditBot(object):
    def __init__(self):
        self.reddit = praw.Reddit(user_agent=self.random_name())
        self.login()
        return

    def login(self, username=config.BOT_CREDENTIALS['username'], password=config.BOT_CREDENTIALS['password']):
        """
        Instantiate Reddit login.

        Args:
            username (str)
            password (str)
        """
        self.reddit.login(username, password)

    def submit(self, subreddit, title, text, url=None):
        self.reddit.submit(subreddit, title, text=text, url=url)

    def comment(self, submission_id, text):
        submission = praw.objects.Submission.from_id(submission_id)
        comment_on_submission(submission, text)

    def comment_on_submission(self, submission, text):
        submission.add_comment(text)

    def random_name(self, length=10):
        """
        Generate random alphabetical string for the instances name.

        Args:
            length (int) : length of the generated string

        Returns:
            a random string

        """
        return ''.join(random.choice(string.ascii_letters)
            for i in range(length))