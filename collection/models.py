from mongoengine import *
import config

connect('reddit', host=config.PROD_HOST, port=config.PROD_PORT)

class Submission(Document):
    r_id = StringField(primary_key=True)
    ups = IntField()
    downs = IntField()
    score = IntField()
    permalink = StringField()
    college = StringField()
    subreddit = StringField()
    created = DateTimeField()
    content = StringField()
    num_reports = IntField()
    pos = FloatField()
    neg = FloatField()
    neu = FloatField()
    keywords = ListField(StringField())

    meta = {'allow_inheritance': True,
            'collection': 'submissions',
            'indexes': ['$content']
            }

    def get_content(self):
        return self.content

class Comment(Submission):
    num_replies = IntField()

class Post(Submission):
    title = StringField()
    num_comments = IntField()
    comments = ListField(ReferenceField(Comment))