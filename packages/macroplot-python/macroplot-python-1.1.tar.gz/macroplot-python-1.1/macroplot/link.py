import json
from collections import OrderedDict
from datetime import datetime

import requests

from .utils import cached_property


class Auth:
    """Authentication credentials."""

    def __init__(self, email, token):

        self.email = email
        self.token = token

    def data(self):

        return {
            'email': self.email,
            'token': self.token,
        }


class Client:
    """Link API client."""

    BASE_URL = 'https://link.macroplot.com'

    class Error(Exception):

        @classmethod
        def raise_for_status(cls, status, data=None):

            message = None

            if isinstance(data, str):
                message = data

            if not message:

                if status == 401:
                    message = 'unauthorized'

                if status == 400:
                    message = 'invalid'

                if status != 200:
                    message = 'error {}'.format(status)

            if message:
                raise cls(message)

    def __init__(self, auth):
        self.auth = auth

    def fetch(self, link, fields=None):

        response = requests.post(
            self.BASE_URL,
            json=[{
                'klass': 'Fetch',
                'body': json.dumps({
                    'auth': self.auth.data(),
                    'link': link,
                    'fields': fields,
                }),
            }],
        )

        self.Error.raise_for_status(response.status_code)

        [item] = response.json()

        status = item['status']
        data = json.loads(item['body'])

        self.Error.raise_for_status(status, data)
        series = Series(data)

        if series.error:
            raise self.Error(series.error)

        return series


class Model(object):
    """Base class for data objects."""

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, str(self))


class Series(Model):
    """Time series data."""

    error = property(lambda self: self.data.get('error'))
    result = cached_property(lambda self: Result(self.data['result']))

    title = property(lambda self: self.data.get('title'))
    connector = property(lambda self: self.data['connector'])
    meta = property(lambda self: self.data.get('meta'))
    expr = property(lambda self: self.data.get('expr'))

    @cached_property
    def points(self):

        points = self.data.get('points')

        if points is None:
            return None

        items = []

        for _date, value in points:
            _date = datetime.strptime(_date, '%Y-%m-%d').date()
            items.append((_date, value))

        return items

    def __str__(self):
        return '{} {} [{}] {}'.format(
            self.connector,
            '?' if self.title is None else repr(self.title),
            '?' if self.points is None else len(self.points),
            repr(self.result),
        )

    ########
    # UTIL #
    ########

    @cached_property
    def pandas(self):
        import pandas as pd
        index, values = zip(*self.points)
        return pd.Series(values, index)


class Result(Model):
    """Connector result."""

    class Field(Model):

        key = property(lambda self: self.data['key'])
        label = property(lambda self: self.data['label'])
        kind = property(lambda self: self.data['type'])
        initial = property(lambda self: self.data.get('initial'))

        @cached_property
        def choices(self):

            items = self.data.get('choices')

            if items is None:
                return None

            return OrderedDict(items)

        def __str__(self):
            return '{} {} [{}]'.format(
                self.key,
                repr(self.label),
                '?' if self.choices is None else len(self.choices),
            )

    status = property(lambda self: self.data['status'])

    @cached_property
    def fields(self):

        items = self.data.get('fields')

        if items is None:
            return None

        fields = OrderedDict()

        for item in items:
            field = self.Field(item)
            fields[field.key] = field

        return fields

    def __str__(self):
        return '{} [{}]'.format(
            self.status,
            '?' if self.fields is None else len(self.fields),
        )
