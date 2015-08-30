import dao
import logging
import pymongo
import praw
import random
import string
import threading
from pymongo.collection import ReturnDocument
from datetime import datetime, timedelta
from config import SUBREDDITS, CREDENTIALS
from Queue import Queue
from analysis import sentiment_analysis

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        post.replace_more_comments(limit=None, threshold=0)
        return praw.helpers.flatten_tree(post.comments)

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
        return int(dt.strftime('%s'))
   

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
                end_date -= timedelta(hours=12)
            else:
                # The college is not in the database so just get the last month
                # worth of data.
                end_date = start_date - timedelta(weeks=4)
            self.crawl(college_info, start_date, end_date)
            logger.info('Finished {} from {} to {}'.format(
                college_info['name'], start_date, end_date))
            logging.info('{} items left in queue'.format(self.q.qsize()))
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
        for i in range(16):
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
        self.sentiment = sentiment_analysis.SentimentHelper()

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
            # TODO(faisal): add error handling capability.
            comment_records = [self.serialize_comment(comment, college_info)
                               for comment in get_comments(post)]
            post_record = self.serialize_post(post, college_info)
            comment_ids = []
            if comment_records:
                comment_ids = [projection['_id']
                               for projection in self.insert_comments(comment_records)]
            # Join the post to its comments by storing the object ids of the
            # comments
            post_record['comments'] = comment_ids
            post_record.update(self.sentiment.compute_sentiment(post_record['text']))
            self.dao.insert_post(post_record)
            post_count += 1
            comment_count += len(comment_ids)
        logger.info('Saved: {} {} posts {} comments'.format(
            college_info['name'], post_count, comment_count))
        return

    def insert_comments(self, comments):
        """
        Save the comments in the database.

        Args:
            comments (list<praw.comment>):

        Returns:
            a list of the ids that mongodb assigns to the comments. Used to 
            create a reference to the comments within the posts
        """
        inserted = []
        for comment in comments:
            comment.update(self.sentiment.compute_sentiment(comment['text']))
            _id = self.dao.insert_comment(comment)
            inserted.append(_id)
        return inserted

    def last_post_date(self, college_info):
        """
        Returns the date of the last post crawled for the request school

        Args:
            college_info (dict): { 'name': name of the college, 
                'subreddit': name of the subreddit}

        Returns: A datetime object
        """
        college = college_info['name']
        last_post_query = self.dao.post_collection.find(
            {'college': college}).sort(
                'created_utc', pymongo.DESCENDING).limit(1)
        last_post = list(last_post_query)
        if last_post:
            return last_post[0]['created_utc']
        # We haven't crawled the subreddit at all.
        return False

    @staticmethod
    def serialize_post(submission, college_info):
        """
        Convert a praw post object to a dictionary.

        Args:
            submission (praw.post): praw post object
            college_info (dict) :

        Returns:
            a dictionary
        """
        college = college_info['name']
        subreddit = college_info['subreddit']
        return {
            'title': submission.title,
            'reddit_id': submission.id,
            'text': submission.selftext,
            'url': submission.url,
            'ups': submission.ups,
            'downs': submission.downs,
            'subreddit': subreddit,
            'college': college,
            'created_utc': datetime.utcfromtimestamp(submission.created_utc),
            'comments': []
        }

    @staticmethod
    def serialize_comment(comment, college_info):
        """
        Convert a praw  comment object to a dictionary
        
        Args:
            submission (praw.comment) : praw comment object
            college_info (str) : college name
        """
        college = college_info['name']
        subreddit = college_info['subreddit']
        return {
            'text': comment.body,
            'reddit_id': comment.id,
            'ups': comment.ups,
            'downs': comment.downs,
            'college': college,
            'subreddit' : subreddit,
            'created_utc': datetime.utcfromtimestamp(comment.created_utc)
        }
