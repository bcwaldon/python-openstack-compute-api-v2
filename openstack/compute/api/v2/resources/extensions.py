# Copyright 2011 OpenStack LLC.

from openstack.compute.api.v2.resources import base

class Extension(base.Resource):
    """An extension communicates what extra functionality is available"""

    id_field = 'alias'

    def __repr__(self):
        return "<Extension: %s>" % self.alias


class ExtensionManager(base.Manager):

    resource_class = Extension

    def list(self):
        """
        Get a list of all extensions.

        :rtype: list of :class:`Extension`.
        """
        return self._list("/extensions", "extensions")

    def get(self, alias):
        """
        Get a specific extension.

        :param alias: The alias of the :class:`extension` to get.
        :rtype: :class:`Extension`
        """
        return self._get("/extensions/%s" % alias, "extension")
