
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

    def to_record(self):
        """
        Returns:
            a dictionary representation of the object
        """
        return self.__dict__

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
        self.created_utc = str(self.created_utc)
        return self.__dict__