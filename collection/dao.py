import pymongo
import os
from datetime import datetime
from datetime import timedelta

import models
import config
from bson.objectid import ObjectId


class MongoDao(object):
    """ Object to get data from MongoDB"""


    def __init__(self, mongo_client=None):
        if mongo_client:
            self.db = mongo_client
        else:
            if True:
                self.db = pymongo.MongoClient()['reddit']
            else:
                self.db = pymongo.MongoClient(config.TEST_DB_URI)[config.TEST_DB_NAME]

    @property
    def post_collection(self):
        """
        The collection where the posts are stored.
        """
        return self.db.posts


    def get_post(self, post_id):
        """
        Get a post model for the post with the given id.

        Args:
            post_id (str):

        Returns
            models.Post object
        """
        if isinstance(post_id, str):
            post_id = ObjectId(post_id)
        post_record = self.db.posts.find_one({'_id': post_id})
        return models.Post.from_record(post_record)

    def get_latest_posts(self, college='Georgia Tech'):
        """
        Get the latest posts from the given college.

        Args:
            college (str):

        Returns
            list<models.Post>
        """
        post_records = self.db.posts.find({'college': college}).limit(30)
        return [models.Post.from_record(record) for record in post_records]

    def get_comments(self, post_id):
        """
        Get comments for a given post.

        Args:
            post_id (str):

        Returns:
            a list of models.Comment object
        """
        post = self.get_post(post_id)
        return [self.get_post(comment_id) for comment_id in post.comments]


    def get_colleges(self):
        """
        Returns: A list of all the colleges present in the database.
        """
        colleges = self.db.posts.find({}).distinct('college')
        colleges.sort()
        return colleges

    def insert(self, record):
        """
        Inserts a post object into the database

        Args:
            record (dict):

        Returns:
            an ObjectId for the post
        """
        return self.db.posts.find_one_and_replace(
            {'reddit_id': record['reddit_id']}, record, projection={'_id': True},
            return_document=pymongo.collection.ReturnDocument.AFTER, upsert=True)

    def get_term_frequency(self, collection, term, colleges, start, end):
        """
        Get usage data for a term across the given colleges with the specified
        date range.

        Args:
            term (str):
            colleges (list<str>):
            start (datetime): defaults to 30 days ago
            end (datetime): defaults to today

        Returns:
            a cursor containing the results in a dictionary with the keys year,
                month, day, college.
        """
        return self.term_frequency_query(collection, term, colleges, start, end)

    def term_frequency_query(self, collection, term, colleges, lower, upper):
        """
        Perform the query to retrieve the counts for a term across the given
        colleges within the specified range.

        Args:
            collection (): the collection to perform the query on
            term (str): does not have to be a single term i.e 'time ticket'
            lower (datetime):
            upper (datetime):

        Returns:
            a pymongo.Cursor
        """
        match = {'$match':
                     {'college': {'$in': colleges},
                      'created_utc': {'$gte': lower, '$lte': upper},
                      '$text': {'$search': term}}}
        project = {'$project': {
                'college': 1,
                'y': {'$year': '$created_utc'},
                'm': {'$month': '$created_utc'},
                'd': {'$dayOfMonth': '$created_utc'}
        }}
        group = {'$group': {
         '_id': {
             'year': '$y',
             'month': '$m',
             'day': '$d',
             'college': '$college'
         },
        'total': {'$sum': 1},
         }}
        sort = {'$sort':{
             '_id.year': -1,
             '_id.month': -1,
             '_id.day' : -1
             }}
        pipeline = [match, project, group, sort]
        return collection.aggregate(pipeline)

    def posts_term_frequency(self, term, colleges, start, end):
        return self.get_term_frequency(
            self.db.posts, term, colleges, start, end)
