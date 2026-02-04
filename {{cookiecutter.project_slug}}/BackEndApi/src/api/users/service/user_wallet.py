from typing import List

from django.db.models import Sum, Q, QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from api.users.models import User


class UserWalletService:
    def __init__(self):
        pass