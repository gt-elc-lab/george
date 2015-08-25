import pymongo
import os
import json

from collection import models
from collection import config
from bson.objectid import ObjectId


class MongoDao(object):
    """ Object to get data from MongoDB"""


    def __init__(self, mongo_client=None):
        if mongo_client:
            self.db = mongo_client
        else:
            if os.environ.get('PROD'):
                self.db = pymongo.MongoClient()['reddit']
            else:
                self.db = pymongo.MongoClient(config.TEST_DB_URI)[config.TEST_DB_NAME]

    @property
    def post_collection(self):
        """
        The collection where the posts are stored.
        """
        return self.db.posts

    @property
    def comment_collection(self):
        """
        The collection where the comments are stored.
        """
        return self.db.comments

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

    def get_post_comments(self, post_id):
        """
        Get comments for a given post.

        Args:
            post_id (str):

        Returns:
            a list of models.Comment object
        """
        post = self.get_post(post_id)
        return [self.get_comment(comment_id) for comment_id in post.comments]

    def get_colleges(self):
        """
        Returns: A list of all the colleges present in the database.
        """
        colleges = self.db.posts.find({}).distinct('college')
        colleges.sort()
        return colleges


    def insert_post(self, post_record):
        """
    	Inserts a post object into the database

    	Args:
    	    post_record (dict):

    	Returns:
            an ObjectId for the post
    	"""
        return self.db.posts.find_one_and_replace(
            {'reddit_id': post_record['reddit_id']}, post_record, projection={'_id': True},
            return_document=pymongo.collection.ReturnDocument.AFTER, upsert=True)

    def get_comment(self, comment_id):
        """
        Get a comment model.

        Args:
            comment_id (str):

        Returns:
            a models.Comment
        """
        if isinstance(comment_id, str):
            comment_id = ObjectId(comment_id)
        comment_record = self.db.comments.find_one({'_id': comment_id})
        return models.Comment.from_record(comment_record)

    def insert_comment(self, comment_record):
        """
        Insert the comment into the database.

        Args:
            comment_record (dict):

        Returns:
            ObjectId for the inserted post
        """
        return self.db.comments.find_one_and_replace(
            {'reddit_id': comment_record['reddit_id']}, comment_record, projection={'_id': True},
            return_document=pymongo.collection.ReturnDocument.AFTER, upsert=True)
