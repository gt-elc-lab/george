from mongoengine import *

connect('reddit')

class Submission(Document):
    r_id = StringField(primary_key=True)
    ups = IntField()
    downs = IntField()
    score = FloatField()
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
            'collection': 'posts',
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