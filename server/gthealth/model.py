from mongoengine import *
from passlib.apps import custom_app_context as pwd_context
import passlib.utils
import datetime

from gthealth import config

connect(host=config.TEST_DB_URI)

class Post(Document):
    r_id = StringField(primary_key=True)
    title = StringField()
    content = StringField()
    resolved = BooleanField(default=False)
    discarded = BooleanField(default=False)
    created = DateTimeField()


class User(Document):
    email = StringField()
    password = StringField()
    activation_token = StringField()
    activated = BooleanField(default=False)

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def create_activation_token(self):
        self.activation_token = passlib.utils.generate_password(size=20)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def verify_activation_token(self, token):
        return pwd_context.verify(token, self.activation_token)

class Responses(Document):
    post = ReferenceField(Post)
    user = ReferenceField(User)
    date = DateTimeField(default=datetime.datetime.now)

class Sample(Document):
    r_id = StringField(primary_key=True)
    title = StringField()
    content = StringField()
    label = BooleanField()
    date = DateTimeField()
    subreddit = StringField()