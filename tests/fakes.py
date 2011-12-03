import httplib2

from openstack.compute.api.v2 import client
from tests import utils


class FakeClient(client.Client):

    def __init__(self):
        self.callstack = []

        super(FakeClient, self).__init__('http://localhost', 'fake_tenant',
                                         'justanothertoken')

    def _cs_request(self, url, method, **kwargs):
        # Check that certain things are called correctly
        if method in ['GET', 'DELETE']:
            assert 'body' not in kwargs
        elif method == 'PUT':
            assert 'body' in kwargs

        # Call the method
        munged_url = url.strip('/').replace('/', '_').replace('.', '_')
        munged_url = munged_url.replace('-', '_')
        callback = "%s_%s" % (method.lower(), munged_url)

        if not hasattr(self, callback):
            raise AssertionError('Called unknown API method: %s %s, '
                                 'expected utils method name: %s' %
                                 (method, url, callback))

        # Note the call
        self.callstack.append((method, url, kwargs.get('body', None)))

        status, body = getattr(self, callback)(**kwargs)
        return httplib2.Response({"status": status}), body

    def assert_called(self, method, url, body=None, pos=-1):
        """
        Assert than an API method was just called.
        """
        expected = (method, url)
        called = self.callstack[pos][0:2]

        assert self.callstack, \
                       "Expected %s %s but no calls were made." % expected

        assert expected == called, 'Expected %s %s; got %s %s' % \
                                               (expected + called)

        if body is not None:
            assert self.callstack[pos][2] == body

    def assert_called_anytime(self, method, url, body=None):
        """
        Assert than an API method was called anytime in the test.
        """
        expected = (method, url)

        assert self.callstack, \
                       "Expected %s %s but no calls were made." % expected

        found = False
        for entry in self.callstack:
            called = entry[0:2]
            if expected == called:
                found = True
                break

        assert found, 'Expected %s %s; got %s' % \
                              (expected, self.callstack)
        if body is not None:
            try:
                assert entry[2] == body
            except AssertionError:
                print entry[2]
                print "!="
                print body
                raise

        self.callstack = []

    def clear_callstack(self):
        self.callstack = []

    #
    # Servers
    #

    def get_servers(self, **kw):
        return (200, {"servers": [
            {'id': 1234, 'name': 'sample-server'},
            {'id': 5678, 'name': 'sample-server2'}
        ]})

    def get_servers_detail(self, **kw):
        return (200, {"servers": [
            {
                "id": 1234,
                "name": "sample-server",
                "image": {
                    "id": 2,
                    "name": "sample image",
                },
                "flavor": {
                    "id": 1,
                    "name": "256 MB Server",
                },
                "hostId": "e4d909c290d0fb1ca068ffaddf22cbd0",
                "status": "BUILD",
                "progress": 60,
                "addresses": {
                    "public": [{
                        "version": 4,
                        "addr": "1.2.3.4",
                    },
                    {
                        "version": 4,
                        "addr": "5.6.7.8",
                    }],
                    "private": [{
                        "version": 4,
                        "addr": "10.11.12.13",
                    }],
                },
                "metadata": {
                    "Server Label": "Web Head 1",
                    "Image Version": "2.1"
                }
            },
            {
                "id": 5678,
                "name": "sample-server2",
                "image": {
                    "id": 2,
                    "name": "sample image",
                },
                "flavor": {
                    "id": 1,
                    "name": "256 MB Server",
                },
                "hostId": "9e107d9d372bb6826bd81d3542a419d6",
                "status": "ACTIVE",
                "addresses": {
                    "public": [{
                        "version": 4,
                        "addr": "4.5.6.7",
                    },
                    {
                        "version": 4,
                        "addr": "5.6.9.8",
                    }],
                    "private": [{
                        "version": 4,
                        "addr": "10.13.12.13",
                    }],
                },
                "metadata": {
                    "Server Label": "DB 1"
                }
            }
        ]})

    def post_servers(self, body, **kw):
        assert body.keys() == ['server']
        utils.assert_has_keys(body['server'],
                        required=['name', 'imageRef', 'flavorRef'],
                        optional=['metadata', 'personality'])
        if 'personality' in body['server']:
            for pfile in body['server']['personality']:
                utils.assert_has_keys(pfile, required=['path', 'contents'])
        return (202, self.get_servers_1234()[1])

    def post_servers_1234_migrate(self, *args, **kwargs):
        return (202, None)

    def get_servers_1234(self, **kw):
        r = {'server': self.get_servers_detail()[1]['servers'][0]}
        return (200, r)

    def get_servers_5678(self, **kw):
        r = {'server': self.get_servers_detail()[1]['servers'][1]}
        return (200, r)

    def put_servers_1234(self, body, **kw):
        assert body.keys() == ['server']
        utils.assert_has_keys(body['server'], optional=['name', 'adminPass'])
        return (204, None)

    def delete_servers_1234(self, **kw):
        return (202, None)

    def delete_servers_1234_metadata_test_key(self, **kw):
        return (204, None)

    def delete_servers_1234_metadata_key1(self, **kw):
        return (204, None)

    def delete_servers_1234_metadata_key2(self, **kw):
        return (204, None)

    def post_servers_1234_metadata(self, **kw):
        return (204, {'metadata': { 'test_key': 'test_value'}})

    #
    # Server Addresses
    #

    def get_servers_1234_ips(self, **kw):
        return (200, {'addresses':
                      self.get_servers_1234()[1]['server']['addresses']})

    def get_servers_1234_ips_public(self, **kw):
        return (200, {'public':
                      self.get_servers_1234_ips()[1]['addresses']['public']})

    def get_servers_1234_ips_private(self, **kw):
        return (200, {'private':
                      self.get_servers_1234_ips()[1]['addresses']['private']})

    def delete_servers_1234_ips_public_1_2_3_4(self, **kw):
        return (202, None)

    #
    # Server actions
    #

    def post_servers_1234_action(self, body, **kw):
        _body = None
        assert len(body.keys()) == 1
        action = body.keys()[0]
        if action == 'reboot':
            assert body[action].keys() == ['type']
            assert body[action]['type'] in ['HARD', 'SOFT']
        elif action == 'rebuild':
            keys = body[action].keys()
            if 'adminPass' in keys:
                keys.remove('adminPass')
            assert keys == ['imageRef']
            _body = self.get_servers_1234()[1]
        elif action == 'resize':
            assert body[action].keys() == ['flavorRef']
        elif action == 'confirmResize':
            assert body[action] is None
            # This one method returns a different response code
            return (204, None)
        elif action == 'revertResize':
            assert body[action] is None
        elif action == 'migrate':
            assert body[action] is None
        elif action == 'rescue':
            assert body[action] is None
        elif action == 'unrescue':
            assert body[action] is None
        elif action == 'addFixedIp':
            assert body[action].keys() == ['networkId']
        elif action == 'removeFixedIp':
            assert body[action].keys() == ['address']
        elif action == 'addFloatingIp':
            assert body[action].keys() == ['address']
        elif action == 'removeFloatingIp':
            assert body[action].keys() == ['address']
        elif action == 'createImage':
            assert set(body[action].keys()) == set(['name', 'metadata'])
        elif action == 'changePassword':
            assert body[action].keys() == ['adminPass']
        else:
            raise AssertionError("Unexpected server action: %s" % action)
        return (202, _body)

    #
    # Flavors
    #

    def get_flavors(self, **kw):
        return (200, {'flavors': [
            {'id': 1, 'name': '256 MB Server'},
            {'id': 2, 'name': '512 MB Server'}
        ]})

    def get_flavors_detail(self, **kw):
        return (200, {'flavors': [
            {'id': 1, 'name': '256 MB Server', 'ram': 256, 'disk': 10},
            {'id': 2, 'name': '512 MB Server', 'ram': 512, 'disk': 20}
        ]})

    def get_flavors_1(self, **kw):
        return (200, {'flavor': self.get_flavors_detail()[1]['flavors'][0]})

    def get_flavors_2(self, **kw):
        return (200, {'flavor': self.get_flavors_detail()[1]['flavors'][1]})

    #
    # Images
    #
    def get_images(self, **kw):
        return (200, {'images': [
            {'id': 1, 'name': 'CentOS 5.2'},
            {'id': 2, 'name': 'My Server Backup'}
        ]})

    def get_images_detail(self, **kw):
        return (200, {'images': [
            {
                'id': 1,
                'name': 'CentOS 5.2',
                "updated": "2010-10-10T12:00:00Z",
                "created": "2010-08-10T12:00:00Z",
                "status": "ACTIVE",
                "metadata": {
                    "test_key": "test_value",
                },
                "links": {},
            },
            {
                "id": 743,
                "name": "My Server Backup",
                "serverId": 1234,
                "updated": "2010-10-10T12:00:00Z",
                "created": "2010-08-10T12:00:00Z",
                "status": "SAVING",
                "progress": 80,
                "links": {},
            }
        ]})

    def get_images_1(self, **kw):
        return (200, {'image': self.get_images_detail()[1]['images'][0]})

    def get_images_2(self, **kw):
        return (200, {'image': self.get_images_detail()[1]['images'][1]})

    def post_images(self, body, **kw):
        assert body.keys() == ['image']
        utils.assert_has_keys(body['image'], required=['serverId', 'name'])
        return (202, self.get_images_1()[1])

    def post_images_1_metadata(self, body, **kw):
        assert body.keys() == ['metadata']
        utils.assert_has_keys(body['metadata'],
                              required=['test_key'])
        return (200,
            {'metadata': self.get_images_1()[1]['image']['metadata']})

    def delete_images_1(self, **kw):
        return (204, None)

    def delete_images_1_metadata_test_key(self, **kw):
        return (204, None)

    #
    # Extensions
    #

    def get_extensions(self, **kw):
        return (200, {'extensions': [
            {
                'name': 'Blargh Extension',
                'alias': 'os-blargh',
                'description': 'What is a blargh?',
            },
            {
                'name': 'Another Extension',
                'alias': 'os-another',
                'description': 'Just another extension!',
            },
        ]})

    def get_extensions_os_blargh(self, **kw):
        obj = self.get_extensions()[1]['extensions'][0]
        return (200, {'extension': obj})

    def get_extensions_os_another(self, **kw):
        obj = self.get_extensions()[1]['extensions'][1]
        return (200, {'extension': obj})

    #
    # Limits
    #

    def get_limits(self, **kw):
        return (200, {"limits": {
            "rate": [
                {
                    "uri": "*",
                    "regex": ".*",
                    "limit": [
                        {
                            "value": 10,
                            "verb": "POST",
                            "remaining": 2,
                            "unit": "MINUTE",
                            "next-available": "2011-12-15T22:42:45Z"
                        },
                        {
                            "value": 10,
                            "verb": "PUT",
                            "remaining": 2,
                            "unit": "MINUTE",
                            "next-available": "2011-12-15T22:42:45Z"
                        },
                        {
                            "value": 100,
                            "verb": "DELETE",
                            "remaining": 100,
                            "unit": "MINUTE",
                            "next-available": "2011-12-15T22:42:45Z"
                        }
                    ]
                },
                {
                    "uri": "*/servers",
                    "regex": "^/servers",
                    "limit": [
                        {
                            "verb": "POST",
                            "value": 25,
                            "remaining": 24,
                            "unit": "DAY",
                            "next-available": "2011-12-15T22:42:45Z"
                        }
                    ]
                }
            ],
            "absolute": {
                "maxTotalRAMSize": 51200,
                "maxServerMeta": 5,
                "maxImageMeta": 5,
                "maxPersonality": 5,
                "maxPersonalitySize": 10240
            }}})
