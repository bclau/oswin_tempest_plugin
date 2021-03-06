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

from oslo_config import cfg
from tempest import config

CONF = config.CONF


hyperv_group = cfg.OptGroup(name='hyperv',
                            title='Hyper-V Driver Tempest Options')

HyperVGroup = [
    cfg.IntOpt('hypervisor_version',
               help="Compute nodes' hypervisor version, used to determine "
                    "which tests to run. It must have following value: "
                    "major_version * 1000 + minor_version"
                    "For example, Windows / Hyper-V Server 2012 R2 would have "
                    "the value 6003"),
    cfg.StrOpt('vhd_image_ref',
               help="Valid VHD image reference to be used in tests."),
    cfg.StrOpt('vhdx_image_ref',
               help="Valid VHDX image reference to be used in tests."),
    cfg.StrOpt('gen2_image_ref',
               help="Valid Generation 2 VM VHDX image reference to be used "
                    "in tests."),
]


_opts = [
    (hyperv_group, HyperVGroup),
]


def list_opts():
    return _opts
