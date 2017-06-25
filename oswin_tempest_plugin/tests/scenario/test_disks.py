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

from oswin_tempest_plugin import config
from oswin_tempest_plugin.tests import test_base
from oswin_tempest_plugin.tests._mixins import migrate

CONF = config.CONF


class _BaseDiskTestMixin(test_base.TestBase,
                         migrate._BaseMigrateMixin):

    _CONF_OPTION_NAME = ''

    @classmethod
    def skip_checks(cls):
        super(_BaseDiskTestMixin, cls).skip_checks()
        # check if the needed image ref has been configured.
        if not cls._IMAGE_REF:
            msg = ('The config option "%s" has not been set. Skipping.' %
                   cls._CONF_OPTION_NAME)
            raise cls.skipException(msg)

    def test_check_disk(self):
        server_tuple = self._create_server()
        self._check_server_connectivity(server_tuple)


class VhdDiskTest(_BaseDiskTestMixin):

    _IMAGE_REF = CONF.hyperv.vhd_image_ref
    _CONF_OPTION_NAME = 'hyperv.vhd_image_ref'

    # TODO(claudiub): validate that the images really are VHD / VHDX.


class VhdxDiskTest(_BaseDiskTestMixin):

    _IMAGE_REF = CONF.hyperv.vhdx_image_ref
    _CONF_OPTION_NAME = 'hyperv.vhdx_image_ref'


class Generation2DiskTest(_BaseDiskTestMixin):

    # Generation 2 VMs have been introduced in Windows / Hyper-V Server 2012 R2
    _MIN_HYPERV_VERSION = 6003

    _IMAGE_REF = CONF.hyperv.gen2_image_ref
    _CONF_OPTION_NAME = 'hyperv.gen2_image_ref'

    # TODO(claudiub): Add validation that the given gen2_image_ref really has
    # the 'hw_machine_type=hyperv-gen2' property.
