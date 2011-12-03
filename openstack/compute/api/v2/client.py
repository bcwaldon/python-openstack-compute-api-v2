# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 OpenStack LLC.
# Copyright 2011 Piston Cloud Computing, Inc.

# All Rights Reserved.
"""
OpenStack Client interface. Handles the REST calls and responses.
"""

import logging
import os
import urlparse

import httplib2

try:
    import json
except ImportError:
    import simplejson as json

# Python 2.5 compat fix
if not hasattr(urlparse, 'parse_qsl'):
    import cgi
    urlparse.parse_qsl = cgi.parse_qsl

from openstack.compute.api.v2 import exceptions
from openstack.compute.api.v2.resources import extensions
from openstack.compute.api.v2.resources import flavors
from openstack.compute.api.v2.resources import images
from openstack.compute.api.v2.resources import servers


_logger = logging.getLogger(__name__)


class Client(httplib2.Http):

    USER_AGENT = 'python-openstack-compute-api-v2'

    def __init__(self, base_url, tenant_id, auth_token, insecure=False,
                 timeout=None):
        super(Client, self).__init__(timeout=timeout)
        self.base_url = base_url
        self.tenant_id = tenant_id
        self.auth_token = auth_token
        #TODO(bcwaldon): this should be v2
        self.management_url = '%s/v1.1/%s' % (base_url, tenant_id)

        # httplib2 overrides
        self.force_exception_to_status_code = True
        self.disable_ssl_certificate_validation = insecure

        # initialize resource-specific managers
        self.extensions = extensions.ExtensionManager(self)
        self.flavors = flavors.FlavorManager(self)
        self.images = images.ImageManager(self)
        self.servers = servers.ServerManager(self)

    def http_log(self, args, kwargs, resp, body):
        if 'NOVACLIENT_DEBUG' in os.environ and os.environ['NOVACLIENT_DEBUG']:
            ch = logging.StreamHandler()
            _logger.setLevel(logging.DEBUG)
            _logger.addHandler(ch)
        elif not _logger.isEnabledFor(logging.DEBUG):
            return

        string_parts = ['curl -i']
        for element in args:
            if element in ('GET', 'POST'):
                string_parts.append(' -X %s' % element)
            else:
                string_parts.append(' %s' % element)

        for element in kwargs['headers']:
            header = ' -H "%s: %s"' % (element, kwargs['headers'][element])
            string_parts.append(header)

        _logger.debug("REQ: %s\n" % "".join(string_parts))
        if 'body' in kwargs:
            _logger.debug("REQ BODY: %s\n" % (kwargs['body']))
        _logger.debug("RESP:%s %s\n", resp, body)


    def _cs_request(self, url, method, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers']['X-Auth-Token'] = self.auth_token
        kwargs['headers']['X-Auth-Project-Id'] = self.tenant_id
        kwargs['headers']['User-Agent'] = self.USER_AGENT

        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['body'] = json.dumps(kwargs['body'])

        _url = '%s/%s' % (self.management_url, url)

        resp, body = super(Client, self).request(_url, method, **kwargs)
        self.http_log((url, method), kwargs, resp, body)

        if body:
            try:
                body = json.loads(body)
            except ValueError:
                pass
        else:
            body = None

        if resp.status in (400, 401, 403, 404, 408, 413, 500, 501):
            raise exceptions.from_response(resp, body)

        return resp, body

    def get(self, url, **kwargs):
        return self._cs_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)
