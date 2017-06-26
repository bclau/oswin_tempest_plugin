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

import collections

from oslo_log import log as logging
from tempest.common import waiters
from tempest.scenario import manager

from oswin_tempest_plugin import config

CONF = config.CONF
LOG = logging.getLogger(__name__)


Server_tuple = collections.namedtuple(
    'Server_tuple',
    ['server', 'floating_ip', 'keypair', 'security_groups'])


class TestBase(manager.ScenarioTest):

    credentials = ['primary', 'admin']

    # Inheriting TestCases should change this version if needed.
    _MIN_HYPERV_VERSION = 6002

    # Inheriting TestCases should change this image ref if needed.
    _IMAGE_REF = CONF.compute.image_ref

    @classmethod
    def skip_checks(cls):
        super(TestBase, cls).skip_checks()
        # check if the configured hypervisor_version is higher than
        # the test's required minimum Hyper-V version.

        # TODO(claudiub): instead of expecting a config option specifying
        # the hypervisor version, we could check nova's compute nodes for
        # their hypervisor versions.
        config_vers = CONF.hyperv.hypervisor_version
        if config_vers < cls._MIN_HYPERV_VERSION:
            msg = ('Configured hypervisor_version (%(config_vers)s) is not '
                   'supported. It must be higher than %(req_vers)s.' % {
                       'config_vers': config_vers,
                       'req_vers': cls._MIN_HYPERV_VERSION})
            raise cls.skipException(msg)

    @classmethod
    def setup_clients(cls):
        super(TestBase, cls).setup_clients()

        cls.admin_servers_client = cls.os_admin.servers_client
        cls.admin_flavors_client = cls.os_admin.flavors_client
        cls.admin_migrations_client = cls.os_admin.migrations_client
        cls.admin_hypervisor_client = cls.os_admin.hypervisor_client

    def _get_image_ref(self):
        return self._IMAGE_REF

    def _get_flavor_ref(self):
        return CONF.compute.flavor_ref

    def _create_server(self):
        image = self._get_image_ref()
        flavor = self._get_flavor_ref()
        keypair = self.create_keypair()
        security_group = self._create_security_group()

        # we need to pass the security group's name to the instance.
        sg_group_names = [{'name': security_group['name']}]

        server = self.create_server(
            image_id=image, flavor=flavor, security_groups=sg_group_names,
            key_name=keypair['name'])
        self._wait_for_server_status(server)

        floating_ip = self.create_floating_ip(server)

        server_tuple = Server_tuple(
            server=server,
            keypair=keypair,
            floating_ip=floating_ip,
            security_groups=[security_group])

        return server_tuple

    def _wait_for_server_status(self, server, status='ACTIVE'):
        waiters.wait_for_server_status(self.servers_client, server['id'],
                                       status)

    def _get_server_client(self, server_tuple):
        server = server_tuple.server
        floating_ip = server_tuple.floating_ip
        keypair = server_tuple.keypair

        # ssh into the VM.
        return self.get_remote_client(
            floating_ip['ip'],
            private_key=keypair['private_key'],
            server=server)

    def _check_server_connectivity(self, server_tuple):
        # if server connectivity works, an SSH client can be opened.
        self._get_server_client(server_tuple)
