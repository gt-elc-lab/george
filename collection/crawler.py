import dao
import logging
import pymongo
import praw
import random
import string
import threading
import re

import models
from datetime import datetime, timedelta
from Queue import Queue
from analysis import sentiment_analysis, keyword_extractor

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

class RedditApiClient(object):
    """ Wrapper around praw """

    CLOUD_QUERY = 'timestamp:{end}..{start}'
    CLOUD_SEARCH = 'cloudsearch'

    def __init__(self):
        self.reddit = praw.Reddit(user_agent=self.random_name())
        return

    def get_posts(self, subreddit, start, end, sort='new'):
        """
        Gets posts between the start and end time for a given subreddit.

        Args:
            subreddit (str) : subreddit to crawl
            start (datetime.datetime) : start time
            end (datetime.datetime) : end time

        Returns:
            A list of praw.post objects
        """
        start_seconds = self.to_seconds(start)
        end_seconds = self.to_seconds(end)
        # Format the string to create a cloud query that restricts the returned
        # posts to those between the start and end date.
        query = self.CLOUD_QUERY.format(start=start_seconds, end=end_seconds)
        posts = self.reddit.search(query, subreddit=subreddit,
            sort=sort, limit=None, syntax=self.CLOUD_SEARCH)
        return posts

    @staticmethod
    def get_comments(post):
        """
        Retrieve the comments of a post

        Args:
            post (praw.post) : the post to get the comments for

        Returns:
            a list of praw.comment objects
        """
        try:
            post.replace_more_comments(limit=None, threshold=0)
            return praw.helpers.flatten_tree(post.comments)
        except AssertionError as e:
            return []

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

    def to_seconds(self, dt):
        """
        Convert a datetime object to seconds.

        Args:
            dt (datetime.datetime):

        Returns:
            an int of the datetime seconds
        """
        return int((dt - datetime(1970,1,1)).total_seconds())


class RedditWorker(threading.Thread):
    """ self contained thread object """

    def __init__(self, reddit_client, database_client, q,
            interval=timedelta(days=14)):
        """
        Args:
            reddit_client (praw.reddit) : praw.reddit object used for
                communicating with reddit api
            database_client: custom class that has a save method
            q (Queue>) : queue containing college infos
            interval (timedelta): amount to shift the window every time a query
                is created, defaults to two weeks
        """
        threading.Thread.__init__(self)
        self.reddit_client = reddit_client
        self.database_client = database_client
        self.q = q
        self.interval = interval
        return

    def run(self):
        """
        Crawl the college retrieved from the queue.
        """
        while True:
            college_info = self.q.get()
            logging.info('Started {}'.format(college_info['name']))
            start_date = datetime.now()
            end_date = self.get_start_time(college_info)
            if end_date:
            	# Pad by a few hours to make sure we pick up any new comments
            	# for relatively new posts.
                end_date -= timedelta(hours=6)
            else:
                # The college is not in the database so just get the last weeks
                # worth of data.

                # NOTE(simplyfaisal): Ideally we should go further back than 12
                # hours. However AlchemyAPI only gives us 1000 requests per day
                # and we would most likely exceed the limit if we crawled any
                # further back.
                end_date = start_date - timedelta(hours=24)
            self.crawl(college_info, start_date, end_date)
            logger.info('Finished {} from {} to {}'.format(
                college_info['name'], start_date, end_date))
            self.q.task_done()

    def crawl(self, college_info, start, end):
        """
        Retrieve all the activity on a subreddit between the start and end dates.

        Args:
            college_info (dict): a dictionary with 'subreddit' and 'name' keys
            start (datetime.datetime):
            end (datetime.datetime):
        """
        subreddit = college_info['subreddit']
        upper = start
        lower = upper - self.interval
        while upper > end:
            if lower < end:
                lower = end
            posts = self.reddit_client.get_posts(subreddit, upper, lower)
            self.database_client.save(posts, college_info, RedditApiClient.get_comments)
            upper = lower
            lower -= self.interval

    def get_start_time(self, college_info):
        """
        Get the time of the most recent post in the database from the specified
        college.

        Args:
            college_info (dict): a dictionary with 'subreddit' and 'name' keys

        Returns:
            a datetime object
        """
        return self.database_client.last_post_date(college_info)


class MultiThreadedCrawler(object):

    def __init__(self, colleges):
        """
        Input:
            colleges (list<dict>): list of {'name': "?", 'subreddit':"?"} dicts
        """
        self.colleges = colleges

    def start(self):
        """
        Activate the threads
        """
        q = Queue()
        for i in range(len(self.colleges)):
            logger.info('Spawned #{}'.format(i))
            client = MongoDBService()
            worker = RedditWorker(
                RedditApiClient(), client,  q)
            worker.daemon = True
            worker.start()
        for college in self.colleges:
            logger.info('Queueing {}'.format(college['name']))
            q.put(college)
            # Lets the main thread exit even if the workers are blocking.

        # Forces the main thread to wait for the queue to finish processing
        # all the tasks.
        q.join()


class MongoDBService(object):

    def __init__(self):
        self.dao = dao.MongoDao()
        self.alchemy_api_service = keyword_extractor.AlchemyApiService()

    def save(self, posts, college_info, get_comments):
        """
        Save the posts to the database.

        Args:
            posts (list<praw.comments>):
            college_info (dict): a dictionary with 'subreddit' and 'name' keys
            get_comments (function): function used to retrieve comments for a
                given post.
        """
        post_count = 0
        comment_count = 0
        for post in posts:
            post_model = self.serialize_post(post, college_info)
            comment_models = [self.serialize_comment(comment, college_info) for comment in get_comments(post)]
            for comment in comment_models:
                self.save_and_update_keywords(comment)
            post_model.comments = comment_models
            self.save_and_update_keywords(post_model)
            post_count += 1
            comment_count += len(comment_models)
        logger.info('Saved: {} {} posts {} comments'.format(
            college_info['name'], post_count, comment_count))
        return

    def save_and_update_keywords(self, model):
        """
        Gets keywords for model if needed, then persists the model.

        Args:
            model (mongoengine model)
        """
        if model.content:
            if not model.pos:
                sentiment = sentiment_analysis.SentimentHelper.compute_sentiment(
                    model.content)
                model.pos = sentiment['pos']
                model.neg = sentiment['neg']
                model.neu = sentiment['neu']
            if not model.keywords:
                model.keywords = self.alchemy_api_service.get_keywords(
                    model.content.lower())
        model.save()
        return

    def last_post_date(self, college_info):
        """
        Returns the date of the last post crawled for the request school

        Args:
            college_info (dict): { 'name': name of the college,
                'subreddit': name of the subreddit}

        Returns: A datetime object
        """
        # college = college_info['name']
        # latest_submission = models.Submission.objects(college=college).order_by('-created').first()
        # if latest_submission:
        #     return latest_submission.created
        return None

    @staticmethod
    def serialize_post(submission, college_info):
        """
        Convert a praw post object to a mongoengine model.

        Args:
            submission (praw.post): praw post object
            college_info (dict) :

        Returns:
            a dictionary
        """
        college = college_info['name']
        subreddit = college_info['subreddit']
        return models.Post(r_id=submission.id,
                           ups=submission.ups,
                           downs=submission.downs,
                           score=submission.score,
                           permalink=submission.permalink,
                           content=submission.selftext,
                           title=submission.title,
                           num_comments=submission.num_comments,
                           num_reports=submission.num_reports,
                           created=datetime.utcfromtimestamp(submission.created_utc),
                           subreddit=subreddit,
                           college=college)
    @staticmethod
    def serialize_comment(comment, college_info):
        """
        Convert a praw  comment object to a mongoengine model

        Args:
            submission (praw.comment) : praw comment object
            college_info (str) : college name
        """
        college = college_info['name']
        subreddit = college_info['subreddit']
        return models.Comment(r_id=comment.id,
                              ups=comment.ups,
                              downs=comment.downs,
                              score=comment.score,
                              permalink=comment.permalink,
                              content=comment.body,
                              num_replies=len(comment.replies),
                              num_reports=comment.num_reports,
                              created=datetime.utcfromtimestamp(comment.created_utc),
                              subreddit=subreddit,
                              college=college)