import ipaddress
import logging
import sys
from xml.dom import minidom
import xml.etree.cElementTree as ET

import deployer.globals as globals
from .globals import LIBVIRT_QEMU_NW, NAT_NW_BASE
from .nat_utils import AddIptableRules, AddLinuxBridge, CheckForwarding, DelIptableRules, DelLinuxBridge
from .utils import ExecuteCommand

class Network:
    topology_ = None
    type_ = ""
    name_ = ""
    ip4_ = None
    broadcast4_ = None
    dhcp_start4_ = None
    dhcp_end4_ = None
    network4_ = None
    network6_ = None
    ip6_ = None
    broadcast6_ = None
    dhcp_start6_ = None
    dhcp_end6_ = None

    def __init__(self, nw_type: str, conf: dict, topo):
        self.topology_ = topo
        self.type_ = nw_type
        self.name_ = conf["name"]
        if self.type_ in ["nat", "management"]:
            self.__create_v4_network(conf.get("subnet4", None))
            self.__create_v6_network(conf.get("subnet6", None))

    def __create_v4_network(self, subnet4: str) -> None:
        if subnet4 is not None:
            logging.debug("Creating IPv4 Network for {}".format(self.name_))
            self.network4_ = ipaddress.IPv4Network(subnet4)
            self.ip4_ = self.network4_[1]
            self.broadcast4_ = self.network4_.broadcast_address
            self.dhcp_start4_ = self.network4_[2]
            self.dhcp_end4_ = self.network4_[-2]
        else:
            logging.critical("No IPv4 subnet provided for {}".format(self.name_))
            sys.exit(1)

    def __create_v6_network(self, subnet6: str) -> None:
        if subnet6 is not None:
            logging.debug("Creating IPv6 Network for {}".format(self.name_))
            self.network6_ = ipaddress.IPv6Network(subnet6)
            self.ip6_ = self.network6_[1]
            self.broadcast6_ = self.network6_.broadcast_address
            self.dhcp_start6_ = self.network6_[2]
            self.dhcp_end6_ = self.network6_[-2]
        else:
            logging.warning("No IPv6 subnet provided for {}".format(self.name_))

    def __create_nat_network(self) -> None:
        logging.info("Creating NAT network : {}".format(self.name_))

        plen4 = 24
        plen6 = 120
        if self.network4_:
            plen4 = self.network4_.prefixlen
        if self.network6_:
            plen6 = self.network6_.prefixlen

        try:
            if not globals.DRY_RUN:
                if not globals.RECREATE_NW:
                    NAT_NW_BASE.joinpath(self.name_).mkdir(parents=True)
                else:
                    AddLinuxBridge(self.name_, str(self.ip4_), str(self.ip6_), plen4, plen6)
                    return
        except Exception as e:
            logging.warning("Nat network {} already exists.".format(self.name_))
            logging.error(str(e))
            return

        CheckForwarding()

        AddLinuxBridge(self.name_, str(self.ip4_), str(self.ip6_), plen4, plen6)
        AddIptableRules(self.name_, str(self.network4_))

    def __create_management_network(self) -> None:
        if globals.RECREATE_NW:
            return

        logging.info("Creating Management network : {}".format(self.name_))
        nw_cfg_file = LIBVIRT_QEMU_NW.joinpath("{}.xml".format(self.name_))

        if nw_cfg_file.is_file():
            logging.warning("Management network {} already exists".format(self.name_))
            return

        nw_ele = ET.Element("network")
        ET.SubElement(nw_ele, "name").text = self.name_
        ET.SubElement(nw_ele, "bridge", {"name": self.name_, "stp": "on", "delay": "0"})

        if self.network4_:
            ip_ele = ET.SubElement(nw_ele, "ip", {
                "address": str(self.ip4_),
                "netmask": str(self.network4_.netmask)
            })
            dhcp_ele = ET.SubElement(ip_ele, "dhcp")
            ET.SubElement(dhcp_ele, "range", {
                "start": str(self.dhcp_start4_),
                "end": str(self.dhcp_end4_)
            })

        xmlstr = minidom.parseString(ET.tostring(nw_ele)).toprettyxml(indent="   ")
        with open (nw_cfg_file, "w") as f:
            f.write(xmlstr)

        cmd = "sudo virsh net-define {}".format(nw_cfg_file)
        ExecuteCommand(cmd)
        cmd = "sudo virsh net-start {}".format(self.name_)
        ExecuteCommand(cmd)
        cmd = "sudo virsh net-autostart {}".format(self.name_)
        ExecuteCommand(cmd)


    def __create_isolated_network(self) -> None:
        if globals.RECREATE_NW:
            return

        logging.info("Creating Isolated network : {}".format(self.name_))
        nw_cfg_file = LIBVIRT_QEMU_NW.joinpath("{}.xml".format(self.name_))

        if nw_cfg_file.is_file():
            logging.warning("Isolated network {} already exists".format(self.name_))
            return

        nw_ele = ET.Element("network")
        ET.SubElement(nw_ele, "name").text = self.name_
        ET.SubElement(nw_ele, "bridge", {"name": self.name_, "stp": "on", "delay": "0"})

        xmlstr = minidom.parseString(ET.tostring(nw_ele)).toprettyxml(indent="   ")
        with open (nw_cfg_file, "w") as f:
            f.write(xmlstr)

        cmd = "sudo virsh net-define {}".format(nw_cfg_file)
        ExecuteCommand(cmd)
        cmd = "sudo virsh net-start {}".format(self.name_)
        ExecuteCommand(cmd)
        cmd = "sudo virsh net-autostart {}".format(self.name_)
        ExecuteCommand(cmd)

    def __delete_nat_network(self):
        DelIptableRules(self.name_, str(self.network4_))
        DelLinuxBridge(self.name_)
        NAT_NW_BASE.joinpath(self.name_).rmdir()

    def __delete_libvirt_network(self):
        cmd = "sudo virsh net-destroy {}".format(self.name_)
        ExecuteCommand(cmd)
        cmd = "sudo virsh net-undefine {}".format(self.name_)
        ExecuteCommand(cmd)

    def Delete(self):
        if self.type_ == "nat":
            self.__delete_nat_network()
        elif self.type_ in ["isolated","management"]:
            self.__delete_libvirt_network()
        else:
            logging.error("Unknown network type {}".format(self.type_))
            sys.exit(1)


    def Create(self):
        if self.type_ == "nat":
            self.__create_nat_network()
        elif self.type_ == "isolated":
            self.__create_isolated_network()
        elif self.type_ == "management":
            self.__create_management_network()
        else:
            logging.error("Unknown network type {}".format(self.type_))
            sys.exit(1)

    def ToString(self) -> str:
        nw_str = ""
        nw_str += "Type : {}\n".format(self.type_)
        nw_str += "Bridge : {}\n".format(self.name_)
        if self.type_ in ["nat", "management"]:
            if self.network4_ is not None:
                nw_str += "--- IPv4 Network ---\n"
                nw_str += "Network : {}\n".format(self.network4_)
                nw_str += "Address : {}\n".format(self.ip4_)
                nw_str += "DHCP Start : {}\n".format(self.dhcp_start4_)
                nw_str += "DHCP End : {}\n".format(self.dhcp_end4_)
                nw_str += "Broadcast : {}\n".format(self.broadcast4_)
            if self.network6_ is not None:
                nw_str += "--- IPv6 Network ---\n"
                nw_str += "Network : {}\n".format(self.network6_)
                nw_str += "Address : {}\n".format(self.ip6_)
                nw_str += "DHCP Start : {}\n".format(self.dhcp_start6_)
                nw_str += "DHCP End : {}\n".format(self.dhcp_end6_)
                nw_str += "Broadcast : {}\n".format(self.broadcast6_)
        nw_str += "===================================\n"
        return nw_str
