import flask

class Post(object):

    def __init__(self, **fields):
        self.__dict__.update(fields)
        return
    
    @staticmethod
    def from_record(mongo_record):
    	"""
    	Get a new instance of a post object from a dictionary
    	
    	Args:
    	    mongo_record (dict): a dictionary

        Returns
            models.Post object
    	"""
        return Post(**mongo_record)

    @staticmethod
    def from_reddit_object(reddit):
        pass

    def to_json(self):
    	"""
    	Returns: 
            a json representation of the object	
    	"""
        self.comments = map(str, self.comments)
        self._id = str(self._id)
        return flask.jsonify(self.__dict__)


class Comment(object):

    def __init__(self, **fields):
        self.__dict__.update(fields)
        return

    @staticmethod
    def from_record(mongo_record):
    	"""
    	Get a post object from the dictionary

    	Args:
    	    mongo_record: a dictionary

        Returns:
            models.Comment instance
    	"""
        return Comment(**mongo_record)

    @staticmethod
    def from_reddit_object(reddit):
        pass

    def to_json(self):
    	"""
    	Returns a json representation of the dictionary.
    	"""
        self._id = str(self._id)
        return flask.jsonify(self.__dict__)
