
class Post(object):

    def __init__(self, **fields):
        self.__dict__.update(fields)
        pass


    @staticmethod
    def from_record(mongo_record):
        return Post(**mongo_record)

    def to_json(self):
        pass

class Comment(object):

    def __init__(self, fields):
        self.__dict__.update(**fields)
        pass

    @staticmethod
    def from_record(mongo_record):
        return Comment(**mongo_record)

    def to_json(self):
        pass
