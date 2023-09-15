from django.conf import settings
from dragonfirerequests import Dragon

from frauddetector.exceptions import CardStatusIsUnknown, CardIsBlocked

url = getattr(settings, 'FRAUD_DETECTOR_URL', 'http://192.168.202.81/api/v1/jsonrpc')
headers = getattr(settings, 'FRAUD_DETECTOR_HEADERS', {})

dragon = Dragon(url, headers=headers)


def check_is_not_blocked(number: str, raise_exception: bool = True):
    """

    :param number: Card number which should contain 16 numbers
    :param raise_exception: Whether to raise exception when card is blocked
    :return: True if card is not blocked otherwise False if raise exception parameter is given as False
             and raises a proper exception when it is True or not given (default)
    """
    data = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'card.check',
        'params': {
            'number': number
        }
    }
    response = dragon.fire_post(json=data)
    if 'result' not in response.data or 'error' in response.data or not response.data['status'] or 'is_blocked' not in \
            response.data['result']:
        if raise_exception:
            raise CardStatusIsUnknown(f"Card status of {number} is unknown")
        return False

    if response.data['result']['is_blocked']:
        if raise_exception:
            # TODO:
            #   Implement temporarily blocked exceptions
            raise CardIsBlocked(f"Card {number} is blocked")
        else:
            return False
    return True
