import random
import string


def random_token(length=6):
    return ''.join(random.choices(string.digits, k=length))
