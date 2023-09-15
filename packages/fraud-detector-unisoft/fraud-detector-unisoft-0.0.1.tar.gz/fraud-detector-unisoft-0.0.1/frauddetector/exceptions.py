
class CardIsBlocked(Exception):
    pass


class CardIsTemporarilyBlocked(CardIsBlocked):
    pass


class CardStatusIsUnknown(Exception):
    pass
