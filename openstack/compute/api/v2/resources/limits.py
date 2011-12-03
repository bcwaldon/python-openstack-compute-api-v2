# Copyright 2011 OpenStack LLC.

from openstack.compute.api.v2.resources import base


class Limits(base.Resource):
    """Display the absolute and rate limits"""

    def __repr__(self):
        return "<Limits >"

    @property
    def absolute(self):
        for (name, value) in self._info['absolute'].items():
            yield AbsoluteLimit(name, value)

    @property
    def rate(self):
        for group in self._info['rate']:
            uri = group['uri']
            regex = group['regex']
            for rate in group['limit']:
                yield RateLimit(uri, regex, rate['verb'], rate['value'],
                                rate['remaining'], rate['unit'],
                                rate['next-available'])


class RateLimit(object):

    def __init__(self, uri, regex, value, verb, remaining,
                 unit, next_available):
        self.uri = uri
        self.regex = regex
        self.value = value
        self.verb = verb
        self.remaining = remaining
        self.unit = unit
        self.next_available = next_available

    def __eq__(self, other):
        return self.uri == other.uri \
            and self.regex == other.regex \
            and self.value == other.value \
            and self.verb == other.verb \
            and self.remaining == other.remaining \
            and self.unit == other.unit \
            and self.next_available == other.next_available

    def __repr__(self):
        return "<RateLimit: uri=%s>" % (self.uri)


class AbsoluteLimit(object):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __eq__(self, other):
        return self.value == other.value and self.name == other.name

    def __repr__(self):
        return "<AbsoluteLimit: name=%s value=%s>" % (self.name, self.value)


class LimitsManager(base.Manager):

    resource_class = Limits

    def get(self):
        """
        Get a specific extension.

        :rtype: :class:`Limits`
        """
        return self._get("/limits", "limits")
