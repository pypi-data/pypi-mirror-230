#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 RENCI NRIG
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author Komal Thareja (kthare10@renci.org)
import logging
import traceback
from ipaddress import IPv4Network
from typing import List

from fabrictestbed.slice_editor import ServiceType
from fabrictestbed_extensions.fablib.fablib import FablibManager
from fabrictestbed_extensions.fablib.node import Node
from fabrictestbed_extensions.fablib.resources import Resources
from fabrictestbed_extensions.fablib.slice import Slice

from mobius.controller.api.api_client import ApiClient
from mobius.controller.util.config import Config


def get_external_ip(self):
    site = self.get_site()
    interface = self.get_interface(network_name=f"{site}-EXT")
    return interface.get_ip_addr()


class FabricClient(ApiClient):
    n = Node
    n.get_external_ip = get_external_ip

    def __init__(self, *, logger: logging.Logger, fabric_config: dict, runtime_config: dict):
        """ Constructor """
        self.logger = logger
        self.fabric_config = fabric_config
        self.runtime_config = runtime_config
        self.node_counter = 0
        self.slices = {}
        self.fablib = FablibManager(credmgr_host=self.fabric_config.get(Config.FABRIC_CM_HOST),
                                    orchestrator_host=self.fabric_config.get(Config.FABRIC_OC_HOST),
                                    fabric_token=self.fabric_config.get(Config.FABRIC_TOKEN_LOCATION),
                                    project_id=self.fabric_config.get(Config.FABRIC_PROJECT_ID),
                                    bastion_username=self.fabric_config.get(Config.FABRIC_BASTION_USER_NAME),
                                    bastion_key_filename=self.fabric_config.get(Config.FABRIC_BASTION_KEY_LOCATION))

    def get_resources(self, slice_id: str = None, slice_name: str = None) -> List[Slice] or None:
        if slice_id is None and slice_name is None and len(self.slices) == 0:
            return None
        try:
            result = []
            self.logger.info("get slice_id")
            if slice_id is not None:
                self.logger.info("slice_id: " + str(slice_id))
                result.append(self.fablib.get_slice(slice_id=slice_id))
            elif slice_name is not None:
                self.logger.info("slice id is none. slice name: " + slice_name)
                result.append(self.fablib.get_slice(name=slice_name))
            else:
                result = self.slices.values()
            return result
        except Exception as e:
            self.logger.info(f"Exception: {e}")

    def get_available_resources(self) -> Resources:
        try:
            available_resources = self.fablib.get_available_resources()
            self.logger.info(f"Available Resources: {available_resources}")
            return available_resources
        except Exception as e:
            self.logger.info(f"Error: {e}")

    def add_resources(self, *, resource: dict, slice_name: str) -> Slice or None:
        if resource.get(Config.RES_COUNT) < 1:
            return None
        # Create Slice

        if slice_name in self.slices:
            self.logger.info(f"Slice {slice_name} already exists!")
            return None
        self.logger.debug(f"Adding {resource} to {slice_name}")
        slice_object = self.fablib.new_slice(slice_name)

        node_count = resource.get(Config.RES_COUNT)
        node_name_prefix = resource.get(Config.RES_NAME_PREFIX)
        image = resource.get(Config.RES_IMAGE)
        nic_model = resource.get(Config.RES_NIC_MODEL)
        network_type = resource.get(Config.RES_NETWORK)[Config.RES_TYPE]
        local_subnet = resource.get(Config.RES_NETWORK)[Config.RES_LOCAL_NW_SUBNET]
        if local_subnet is None:
            local_subnet = "192.168.1.0/24"
        site = resource.get(Config.RES_SITE)
        cores = resource.get(Config.RES_FLAVOR)[Config.RES_FLAVOR_CORES]
        ram = resource.get(Config.RES_FLAVOR)[Config.RES_FLAVOR_RAM]
        disk = resource.get(Config.RES_FLAVOR)[Config.RES_FLAVOR_DISK]

        if site == Config.FABRIC_RANDOM:
            site = self.fablib.get_random_site()

        # Layer3 Network (provides data plane internet access)
        net1 = slice_object.add_l3network(name=f"{site}-EXT", type=f"{network_type}Ext")

        # Layer2 Network
        net2 = slice_object.add_l2network(name=f"{site}-LOCAL", subnet=IPv4Network(local_subnet))

        # Add node
        for i in range(node_count):
            node_name = f"{node_name_prefix}{self.node_counter}"
            self.node_counter += 1
            node = slice_object.add_node(name=node_name, image=image, site=site, cores=cores, ram=ram, disk=disk)

            iface1 = node.add_component(model=nic_model, name=f"{node_name}-ext").get_interfaces()[0]
            net1.add_interface(iface1)

            iface2 = node.add_component(model=nic_model, name=f"{node_name}-local").get_interfaces()[0]
            iface2.set_mode('auto')
            net2.add_interface(iface2)

        self.slices[slice_name] = slice_object
        return slice_object

    def request_external_access(self, *, slice_object: Slice):
        try:
            if slice_object is None:
                raise Exception("Add Resources to the Slice, before requesting external access")
            self.logger.info("Requesting external access")

            slice_object = self.fablib.get_slice(name=slice_object.slice_name)

            num_nodes = len(slice_object.get_nodes())
            site = slice_object.get_nodes()[0].get_site()
            ext_network = slice_object.get_network(name=f"{site}-EXT")
            available_ips = ext_network.get_available_ips(count=num_nodes)
            available_ips_str = []
            for x in available_ips:
                available_ips_str.append(str(x))

            self.logger.info(f"Requesting public access on IPs: {available_ips_str} for {ext_network.get_type()}")
            if ext_network.get_type() == ServiceType.FABNetv4Ext:
                ext_network.make_ip_publicly_routable(ipv4=available_ips_str)
            elif ext_network.get_type() == ServiceType.FABNetv6Ext:
                ext_network.make_ip_publicly_routable(ipv6=available_ips_str)

            self.logger.info("Submitted external access request")
            slice_object.submit()
            slice_object = self.fablib.get_slice(slice_id=slice_object.slice_id)

            ext_network = slice_object.get_network(name=f"{site}-EXT")
            public_ips = ext_network.get_public_ips()
            count = 0
            for n in slice_object.get_nodes():
                node_iface = n.get_interface(network_name=ext_network.get_name())
                node_iface.ip_addr_add(addr=public_ips[count], subnet=ext_network.get_subnet())
                if ext_network.get_type() == ServiceType.FABNetv4Ext:
                    n.execute(f'sudo ip route add 0.0.0.0/1 via {ext_network.get_gateway()} dev {node_iface.get_device_name()}')
                elif ext_network.get_type() == ServiceType.FABNetv6Ext:
                    n.execute(
                        f'sudo ip route add 2605:d9c0:2:10::2:210/64 via {ext_network.get_gateway()} dev {node_iface.get_device_name()}')
                self.logger.info(f"IP Address {public_ips[count]} and routes configured on  {n.get_name()}/{n.get_management_ip()}!")
                count += 1
        except Exception as e:
            self.logger.error(f"Exception occurred: {e}")
            self.logger.error(traceback.format_exc())

    def submit_and_wait(self, *, slice_object: Slice) -> str or None:
        try:
            if slice_object is None:
                raise Exception("Add Resources to the Slice, before calling create")

            # Check if slice already exists; return existing slice
            existing_slices = self.get_resources(slice_name=slice_object.get_name())
            if existing_slices is not None and len(existing_slices) > 0:
                self.slices[slice_object.get_name()] = existing_slices[0]
                return existing_slices[0].get_slice_id()

            # Check if the slice has more than one site then add a layer2 network
            # Submit Slice Request
            self.logger.info("Submit slice request")
            slice_id = slice_object.submit()
            self.logger.info("Slice provisioning successful")
            return slice_id
        except Exception as e:
            self.logger.error(f"Exception occurred: {e}")
            self.logger.error(traceback.format_exc())
        return None

    def delete_resources(self, *, slice_id: str = None, slice_name: str = None):
        if slice_id is None and slice_name is None and len(self.slices) == 0:
            return None
        try:
            if slice_id is not None:
                slice_object = self.fablib.get_slice(slice_id=slice_id)
                slice_object.delete()
            elif slice_name is not None:
                slice_object = self.fablib.get_slice(slice_name)
                slice_object.delete()
            else:
                for s in self.slices.values():
                    s.delete()
        except Exception as e:
            self.logger.info(f"Fail: {e}")
