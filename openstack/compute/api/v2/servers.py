# Copyright 2010 Jacob Kaplan-Moss

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Server interface.
"""

import urllib

from openstack.compute.api.v2 import base


REBOOT_SOFT, REBOOT_HARD = 'SOFT', 'HARD'


class Server(base.Resource):
    def __repr__(self):
        return "<Server: %s>" % self.name

    def delete(self):
        """
        Delete (i.e. shut down and delete the image) this server.
        """
        self.manager.delete(self)

    def update(self, name=None):
        """
        Update the name or the password for this server.

        :param name: Update the server's name.
        :param password: Update the root password.
        """
        self.manager.update(self, name=name)

    def pause(self):
        """
        Pause -- Pause the running server.
        """
        self.manager.pause(self)

    def unpause(self):
        """
        Unpause -- Unpause the paused server.
        """
        self.manager.unpause(self)

    def suspend(self):
        """
        Suspend -- Suspend the running server.
        """
        self.manager.suspend(self)

    def resume(self):
        """
        Resume -- Resume the suspended server.
        """
        self.manager.resume(self)

    def change_password(self, password):
        """
        Update the password for a server.
        """
        self.manager.change_password(self, password)

    def reboot(self, type=REBOOT_SOFT):
        """
        Reboot the server.

        :param type: either :data:`REBOOT_SOFT` for a software-level reboot,
                     or `REBOOT_HARD` for a virtual power cycle hard reboot.
        """
        self.manager.reboot(self, type)

    def rebuild(self, image, password=None):
        """
        Rebuild -- shut down and then re-image -- this server.

        :param image: the :class:`Image` (or its ID) to re-image with.
        :param password: string to set as password on the rebuilt server.
        """
        return self.manager.rebuild(self, image, password)

    def resize(self, flavor):
        """
        Resize the server's resources.

        :param flavor: the :class:`Flavor` (or its ID) to resize to.

        Until a resize event is confirmed with :meth:`confirm_resize`, the old
        server will be kept around and you'll be able to roll back to the old
        flavor quickly with :meth:`revert_resize`. All resizes are
        automatically confirmed after 24 hours.
        """
        self.manager.resize(self, flavor)

    def create_image(self, image_name, metadata):
        """
        Create an image based on this server.

        :param image_name: The name to assign the newly create image.
        :param metadata: Metadata to assign to the image.
        """
        self.manager.create_image(self, image_name, metadata)

    def confirm_resize(self):
        """
        Confirm that the resize worked, thus removing the original server.
        """
        self.manager.confirm_resize(self)

    def revert_resize(self):
        """
        Revert a previous resize, switching back to the old server.
        """
        self.manager.revert_resize(self)

    @property
    def networks(self):
        """
        Generate a simplified list of addresses
        """
        networks = {}
        try:
            for network_label, address_list in self.addresses.items():
                networks[network_label] = [a['addr'] for a in address_list]
            return networks
        except Exception:
            return {}


class ServerManager(base.BootingManagerWithFind):
    resource_class = Server

    def get(self, server):
        """
        Get a server.

        :param server: ID of the :class:`Server` to get.
        :rtype: :class:`Server`
        """
        return self._get("/servers/%s" % base.getid(server), "server")

    def list(self, detailed=True, search_opts=None):
        """
        Get a list of servers.
        Optional detailed returns details server info.
        Optional reservation_id only returns instances with that
        reservation_id.

        :rtype: list of :class:`Server`
        """
        if search_opts is None:
            search_opts = {}

        qparams = {}

        for opt, val in search_opts.iteritems():
            if val:
                qparams[opt] = val

        query_string = "?%s" % urllib.urlencode(qparams) if qparams else ""

        detail = ""
        if detailed:
            detail = "/detail"
        return self._list("/servers%s%s" % (detail, query_string), "servers")

    def pause(self, server):
        """
        Pause the server.
        """
        self.api.post('/servers/%s/pause' % base.getid(server))

    def unpause(self, server):
        """
        Unpause the server.
        """
        self.api.post('/servers/%s/unpause' % base.getid(server))

    def suspend(self, server):
        """
        Suspend the server.
        """
        self.api.post('/servers/%s/suspend' % base.getid(server))

    def resume(self, server):
        """
        Resume the server.
        """
        self.api.post('/servers/%s/resume' % base.getid(server))

    def create(self, name, image, flavor, meta=None, files=None):
        """
        Create (boot) a new server.

        :param name: Something to name the server.
        :param image: The :class:`Image` to boot with.
        :param flavor: The :class:`Flavor` to boot onto.
        :param meta: A dict of arbitrary key/value metadata to store for this
                     server. A maximum of five entries is allowed, and both
                     keys and values must be 255 characters or less.
        :param files: A dict of files to overrwrite on the server upon boot.
                      Keys are file names (i.e. ``/etc/passwd``) and values
                      are the file contents (either as a string or as a
                      file-like object). A maximum of five entries is allowed,
                      and each file must be 10k or less.
        :param zone_blob: a single (encrypted) string which is used internally
                      by Nova for routing between Zones. Users cannot populate
                      this field.
        :param userdata: user data to pass to be exposed by the metadata
                      server this can be a file type object as well or a
                      string.
        :param reservation_id: a UUID for the set of servers being requested.
        :param key_name: (optional extension) name of previously created
                      keypair to inject into the instance.
        :param availability_zone: The :class:`Zone`.
        :param block_device_mapping: (optional extension) A dict of block
                      device mappings for this server.
        :param nics:  (optional extension) an ordered list of nics to be
                      added to this server, with information about
                      connected networks, fixed ips, etc.
        """
        return self._boot("/servers", "server", name, image, flavor,
                          meta=meta, files=files)

    def update(self, server, name=None):
        """
        Update the name or the password for a server.

        :param server: The :class:`Server` (or its ID) to update.
        :param name: Update the server's name.
        """
        if name is None:
            return

        body = {
            "server": {
                "name": name,
            },
        }

        self._update("/servers/%s" % base.getid(server), body)

    def change_password(self, server, password):
        """
        Update the password for a server.
        """
        self._action("changePassword", server, {"adminPass": password})

    def delete(self, server):
        """
        Delete (i.e. shut down and delete the image) this server.
        """
        self._delete("/servers/%s" % base.getid(server))

    def reboot(self, server, type=REBOOT_SOFT):
        """
        Reboot a server.

        :param server: The :class:`Server` (or its ID) to share onto.
        :param type: either :data:`REBOOT_SOFT` for a software-level reboot,
                     or `REBOOT_HARD` for a virtual power cycle hard reboot.
        """
        self._action('reboot', server, {'type': type})

    def rebuild(self, server, image, password=None):
        """
        Rebuild -- shut down and then re-image -- a server.

        :param server: The :class:`Server` (or its ID) to share onto.
        :param image: the :class:`Image` (or its ID) to re-image with.
        :param password: string to set as password on the rebuilt server.
        """
        body = {'imageRef': base.getid(image)}
        if password is not None:
            body['adminPass'] = password
        resp, body = self._action('rebuild', server, body)
        return Server(self, body['server'])

    def resize(self, server, flavor):
        """
        Resize a server's resources.

        :param server: The :class:`Server` (or its ID) to share onto.
        :param flavor: the :class:`Flavor` (or its ID) to resize to.

        Until a resize event is confirmed with :meth:`confirm_resize`, the old
        server will be kept around and you'll be able to roll back to the old
        flavor quickly with :meth:`revert_resize`. All resizes are
        automatically confirmed after 24 hours.
        """
        self._action('resize', server, {'flavorRef': base.getid(flavor)})

    def confirm_resize(self, server):
        """
        Confirm that the resize worked, thus removing the original server.

        :param server: The :class:`Server` (or its ID) to share onto.
        """
        self._action('confirmResize', server)

    def revert_resize(self, server):
        """
        Revert a previous resize, switching back to the old server.

        :param server: The :class:`Server` (or its ID) to share onto.
        """
        self._action('revertResize', server)

    def create_image(self, server, image_name, metadata=None):
        """
        Snapshot a server.

        :param server: The :class:`Server` (or its ID) to share onto.
        :param image_name: Name to give the snapshot image
        :param meta: Metadata to give newly-created image entity
        """
        self._action('createImage', server,
                     {'name': image_name, 'metadata': metadata or {}})

    def set_meta(self, server, metadata):
        """
        Set a servers metadata
        :param server: The :class:`Server` to add metadata to
        :param metadata: A dict of metadata to add to the server
        """
        body = {'metadata': metadata}
        return self._create("/servers/%s/metadata" % base.getid(server),
                             body, "metadata")

    def delete_meta(self, server, keys):
        """
        Delete metadata from an server
        :param server: The :class:`Server` to add metadata to
        :param keys: A list of metadata keys to delete from the server
        """
        for k in keys:
            self._delete("/servers/%s/metadata/%s" % (base.getid(server), k))

    def _action(self, action, server, info=None):
        """
        Perform a server "action" -- reboot/rebuild/resize/etc.
        """
        url = '/servers/%s/action' % base.getid(server)
        return self.api.post(url, body={action: info})
