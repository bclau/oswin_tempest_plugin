# Copyright 2017 Cloudbase Solutions SRL
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

import time

from oslo_log import log as logging
import testtools

from oswin_tempest_plugin import config
from oswin_tempest_plugin import exceptions

CONF = config.CONF
LOG = logging.getLogger(__name__)


class _ResizeUtils(object):

    def _get_server_migration(self, server_id):
        final_states = ['error', 'confirmed']
        for i in range(10):
            migrations = (
                self.admin_migrations_client.list_migrations()['migrations'])
            server_migration = [m for m in migrations
                                if m['instance_uuid'] == server_id]
            if server_migration:
                migration_status = server_migration[0]['status']
                LOG.debug("Server's %s migration status: %s",
                          server_id, migration_status)
                if migration_status in final_states:
                    return server_migration[0]
            else:
                # NOTE(claudiub): the migration might not appear *immediately*
                # after the cold resize was requested.
                LOG.info("Server's %s migration was not found.", server_id)

            time.sleep(1)

        return server_migration[0] if server_migration else None

    def _resize_server(self, server_tuple, new_flavor):
        server = server_tuple.server
        self.servers_client.resize_server(server['id'],
                                          flavor_ref=new_flavor['id'])

        migration = self._get_server_migration(server['id'])
        if migration and migration['status'] == 'error':
            # the migration ended up in an error state. Raise an exception.
            raise exceptions.ResizeException(server_id=server['id'],
                                             flavor=new_flavor)

        self._wait_for_server_status(server, 'VERIFY_RESIZE')
        self.servers_client.confirm_resize_server(server['id'])


class _ResizeMixin(_ResizeUtils):
    """Cold resize mixin.

    This mixin will add cold resize tests. The tests will create a new
    instance, resize it to a new flavor, and check its network connectivity.

    The new flavor is based on the configured compute.flavor_ref, with some
    updates. For example, if the vNUMA configuration is to be tested, the new
    flavor would contain the flavor extra_spec 'hw:numa_nodes=1'.
    """

    # NOTE(claudiub): These flavor dicts are updates to the base flavor
    # tempest is configured with. For example, _BIGGER_FLAVOR can be:
    # _BIGGER_FLAVOR = {'disk': 1}
    # which means a flavor having +1 GB disk size will be created, and
    # a created instance will be resized to it.

    _SMALLER_FLAVOR = {}
    _BIGGER_FLAVOR = {}
    _BAD_FLAVOR = {}

    @testtools.skipUnless(CONF.compute_feature_enabled.resize,
                          'Resize is not available.')
    def test_resize(self):
        new_flavor = self._create_new_flavor(self._get_flavor_ref(),
                                             self._BIGGER_FLAVOR)
        server_tuple = self._create_server()
        self._resize_server(server_tuple, new_flavor)
        self._check_server_connectivity(server_tuple)

    @testtools.skipUnless(CONF.compute_feature_enabled.resize,
                          'Resize is not available.')
    def test_resize_negative(self):
        new_flavor = self._create_new_flavor(self._get_flavor_ref(),
                                             self._BAD_FLAVOR)
        server_tuple = self._create_server()

        self.assertRaises(exceptions.ResizeException, self._resize_server,
                          server_tuple, new_flavor)
        # assert that the server is still reachable, even if the resize
        # failed.
        self._check_server_connectivity(server_tuple)
