import json
from dotenv import load_dotenv
try:
    # Works when running the tests from this package
    from constants import *
except Exception as e:
    # Works when importing this module from another package
    from profile_reaction_local.src.constants import *


load_dotenv()
from logger_local.Logger import Logger  # noqa: E402

logger = Logger.create_logger(object=OBJECT_TO_INSERT_CODE)


class ProfileReactionDto:

    def __init__(self, **kwargs):
        INIT_METHOD_NAME = '__init__'
        logger.start(INIT_METHOD_NAME, object={'kwargs': kwargs})
        self.kwargs = kwargs
        logger.end(INIT_METHOD_NAME, object={'kwargs': kwargs})

    def get(self, attr_name, default=None):
        arguments = getattr(self, 'kwargs', default)
        value = arguments.get(attr_name, default)
        return value

    def get_arguments(self):
        return getattr(self, 'kwargs', None)

    def to_json(self):
        return json.dumps(self.__dict__)

    def __eq__(self, other):
        if not isinstance(other, ProfileReactionDto):
            return False
        return self.__dict__ == other.__dict__
