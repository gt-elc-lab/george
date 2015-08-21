import models
import pymongo
import os
import config
from bson.objectid import ObjectId


class MongoDao(object):
    def __init__(self, mongo_client=None):
        if mongo_client:
            self.db = mongo_client
        else:
            if os.environ.get('PROD'):
                self.db = pymongo.MongoClient()['reddit']
            else:
                self.db = pymongo.MongoClient(config.TEST_DB_URI)[config.TEST_DB_NAME]

    def get_post(self, post_id):
        """
    	Returns a post object for the given id
    	
    	Inputs:
    	    post_id: a string post id
    	
    	Returns a model.Post object
    	"""
        if type(post_id) == unicode:
            post_id = ObjectId(post_id)
        post_record = self.db.posts.find_one({'_id': post_id})
        return models.Post.from_record(post_record)

    def get_post_comments(self, post_id):
        post = self.get_post(post_id)
        return [self.get_comment(comment_id) for comment_id in post.comments]

    def get_colleges(self):
        """

        :return: List of colleges in the database
        """
        return self.db.posts.find({}).distinct('college')

    def insert_post(self, post_record):
        """
    	Inserts a post object into the database

    	Inputs:
    	    post_record: a dictionary
    	
    	Returns: an ObjectId for the post
    	"""
        return self.db.posts.find_one_and_replace(
            {'reddit_id': post_record['reddit_id']}, post_record, projection={'_id': True},
            return_document=pymongo.collection.ReturnDocument.AFTER, upsert=True)

    @property
    def post_collection(self):
        return self.db.posts

    def get_comment(self, comment_id):
        if type(comment_id) == unicode:
            comment_id = ObjectId(comment_id)
        comment_record = self.db.comments.find_one({'_id': comment_id})
        return models.Comment.from_record(comment_record)

    def insert_comment(self, comment_record):
        return self.db.comments.find_one_and_replace(
            {'reddit_id': comment_record['reddit_id']}, comment_record, projection={'_id': True},
            return_document=pymongo.collection.ReturnDocument.AFTER, upsert=True)

    @property
    def comment_collection(self):
        return self.db.comments
