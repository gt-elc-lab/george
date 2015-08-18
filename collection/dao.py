import models
import pymongo
from bson.objectid import ObjectId


class PostDao(object):
    def __init__(self, mongo_client=None):
        self.db = mongo_client or pymongo.MongoClient()['reddit']

    def get_post(self, post_id):
        post_record = self.db.posts.find({'_id': ObjectId(post_id)})
        return models.Post.fromRecord(post_record)

    def get_post_comments(self, post_id):
        pass

    def insert_post(self, post_record):
        return self.db.posts.find_one_and_replace(
            {'reddit_id': post_record['reddit_id']}, post_record, projection={'_id': True},
            return_document=pymongo.collection.ReturnDocument.AFTER, upsert=True)

    @property
    def collection(self):
        return self.db.posts


class CommentDao(object):
    def __init__(self, mongo_client=None):
        self.db = mongo_client or pymongo.MongoClient()['reddit']

    def get_comment(self, comment_id):
        comment_record = self.db.comments.find({'_id': ObjectId(comment_id)})
        return models.Comment.fromRecord(comment_record)

    def insert_comment(self, comment_record):
        return self.db.comments.find_one_and_replace(
            {'reddit_id': comment_record['reddit_id']}, comment_record, projection={'_id': True},
            return_document=pymongo.collection.ReturnDocument.AFTER, upsert=True)

    @property
    def collection(self):
        return self.db.comments
