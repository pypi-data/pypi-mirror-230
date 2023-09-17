#
from enum import Enum, auto


#


#


#
class ExceptionMessageGroup(Enum):
    API = auto()
    DEALERS_API = auto()
    BLOCKCHAIN = auto()
    FRONT = auto()


class ExceptionMessageContainer:
    def __init__(self, group, message=None, e=None, data=None):
        if isinstance(group, ExceptionMessageGroup):
            self.group = group
        else:
            raise ValueError(
                "Invalid 'group' value {0} provided; should be an instance of ExceptionMessageGroup class".format(
                    group
                ))
        self.message = message
        self.e = e
        self.data = data
        # if message and e:
        #     raise ValueError("Only one field exclusively should be specified: either 'message' or 'e', not both")

    @property
    def specific(self):
        return bool(self.message)
