import sys
import logging
import yaml
import ipaddress

import deployer.globals as G
from .network import Network
from .globals import BASE_OS, LIBVIRT_IMAGES
from .utils import ExecuteCommand

class VirtualMachine:
    name_ = ""
    flavor_ = ""
    vnc_port_ = -1
    user_data_cfg_ = ""
    network_data_cfg_ = ""
    root_disk_ = ""
    cloud_init_iso_ = ""
    networks_ = {}
    vcpus_ = 8
    ram_ = 16384
    root_disk_sz_ = "40G"

    def __init__(self, conf: dict, topo):
        self.topology_ = topo
        self.name_ = conf["name"]
        self.flavor_ = conf["flavor"]
        self.vnc_port_ = int(conf["vnc_port"])
        self.libvirt_vm_base = LIBVIRT_IMAGES.joinpath(self.name_)
        self.user_data_cfg_ = self.libvirt_vm_base.joinpath("user-data.cfg")
        self.network_data_cfg_ = self.libvirt_vm_base.joinpath("nw-data.cfg")
        self.root_disk_ = self.libvirt_vm_base.joinpath("root_disk.qcow2")
        self.cloud_init_iso_ = self.libvirt_vm_base.joinpath("cloud-init.iso")

        self.libvirt_vm_base.mkdir(parents=True, exist_ok=True)
        self.networks_ = conf["networks"]

        if self.flavor_ == "ce":
            self.vcpus_ = 8
            self.ram_ = 8192
            self.root_disk_sz_ = "40G"
        elif self.flavor_ == "pe":
            self.vcpus_ = 8
            self.ram_ = 16384
            self.root_disk_sz_ = "80G"
        elif self.flavor_ == "dev":
            self.vcpus_ = 32
            self.ram_ = 65536
            self.root_disk_sz_ = "320G"

        if conf.get("vcpus", None) is not None:
            self.vcpus_ = int(conf["vcpus"])

        if conf.get("ram", None) is not None:
            self.vcpus_ = int(conf["ram"])

        if conf.get("disk", None) is not None:
            self.root_disk_sz_ = int(conf["disk"])

    def Topology(self):
        return self.topology_

    def __generate_cloud_init_config(self) -> None:
        cloud_init = {
            "system_info": {
                "default_user": {
                    "name": G.BASE_OS,
                    "home": "/home/{}".format(G.BASE_OS)
                },
            },
            "password": G.BASE_OS,
            "chpasswd": {
                "expire": False
            },
            "hostname": "{}-node".format(self.name_),
            "ssh_pwauth": True
        }

        with open(self.user_data_cfg_, "w") as cloud_init_f:
            cloud_init_f.write("#cloud-config\n")
            yaml.dump(cloud_init, cloud_init_f, sort_keys=False)
            cloud_init_f.write("")

    def __get_ubuntu_params(self) -> list:
        network_config = {
            "network": {
                "version": 2,
                "ethernets": {}
            }
        }
        interface_config = network_config["network"]["ethernets"]
        index = 1
        intf_fmt = "enp{}s0"
        return [network_config, interface_config, intf_fmt, index]

    def __get_rocky_params(self) -> list:
        network_config = {
            "version": 2,
            "ethernets": {}
        }
        interface_config = network_config["ethernets"]
        index = 0
        intf_fmt = "eth{}"
        return [network_config, interface_config, intf_fmt, index]

    def __get_os_based_params(self) -> list:
        if G.BASE_OS == "rocky":
            return self.__get_rocky_params()
        elif G.BASE_OS == "ubuntu":
            return self.__get_ubuntu_params()

        return [None, None, None, None]

    def __generate_netplan_config(self) -> None:
        network_config, interface_config, intf_fmt, index = self.__get_os_based_params()

        if ((network_config is None) or
            (interface_config is None) or
            (intf_fmt is None) or
            (index is None)):
            logging.critical("Error fetching os based network params")
            sys.exit(1)

        for nw in self.networks_:
            intf_name = intf_fmt.format(index)
            network = self.Topology().GetNetwork(nw)
            nw_type = self.Topology().GetNetworkType(nw)
            ip4 = self.networks_[nw].get("v4", None)
            ip6 = self.networks_[nw].get("v6", None)

            if nw_type == "management":
                interface_config[intf_name] = self.__generate_mgmt_config(ip4, network)
            elif nw_type == "nat":
                interface_config[intf_name] = self.__generate_nat_config(ip4, ip6, network)
            elif nw_type == "isolated":
                interface_config[intf_name] = self.__generate_iso_config(ip4, ip6)
            index = index + 1

        with open(self.network_data_cfg_, "w") as nw_config_f:
            nw_config_f.write("#network-config\n")
            yaml.dump(network_config, nw_config_f, sort_keys=False)


    def __generate_mgmt_config(self, ip4: str, nw: Network) -> dict:
        addr = ""
        if nw.network4_ is not None:
            addr = "{}/{}".format(ip4, nw.network4_.prefixlen)
        mgmt_nw_config = {
            "addresses": [addr],
            "routes": [{
                "to": str(nw.network4_),
                "via": str(nw.ip4_)
            }]
        }
        return mgmt_nw_config

    def __generate_nat_config(self, ip4: str, ip6: str, nw: Network) -> dict:
        addresses = []

        if nw.network4_ is not None:
            addresses.append("{}/{}".format(ip4, nw.network4_.prefixlen)) if ip4 is not None else None

        if nw.network6_ is not None:
            addresses.append("{}/{}".format(ip6, nw.network6_.prefixlen)) if ip6 is not None else None

        nat_nw_config = {
            "addresses": addresses,
            "nameservers": {
                "addresses": ['66.129.233.81', '10.84.5.101', '172.21.200.60'],
                "search": ['jnpr.net', 'juniper.net', 'englab.juniper.net']
            },
            "gateway4": str(nw.ip4_),
        }

        if nw.network6_ is not None:
            nat_nw_config["gateway6"] = str(nw.ip6_)

        return nat_nw_config

    def __generate_iso_config(self, ip4: str, ip6: str) -> dict:
        addresses = []
        routes = []

        if ip4 is not None:
            addresses.append("{}/{}".format(ip4, 24))
            nw = ipaddress.IPv4Network("{}/24".format(ip4), strict=False)
            routes.append({
                "to": str(nw),
                "scope": "link"
            })

        if ip6 is not None:
            addresses.append("{}/{}".format(ip6, 120))
            nw = ipaddress.IPv6Network("{}/120".format(ip6), strict=False)
            routes.append({
                "to": str(nw),
                "scope": "link"
            })

        iso_nw_config = {
            "addresses": addresses,
            "routes": routes
        }
        return iso_nw_config

    def __create_root_disk(self) -> None:
        cmd = "sudo qemu-img convert -f qcow2 -O qcow2 {} {}".format(
                G.OS_IMAGE_TEMPLATE, self.root_disk_)
        ExecuteCommand(cmd)

        cmd = "sudo qemu-img resize {} {}".format(self.root_disk_, self.root_disk_sz_)
        ExecuteCommand(cmd)

    def __generate_cloud_init_iso(self) -> None:
        cmd = "sudo cloud-localds -N {} {} {}".format(
                self.network_data_cfg_,
                self.cloud_init_iso_,
                self.user_data_cfg_)
        ExecuteCommand(cmd)


    def __execute_virt_install_cmd(self):
        name_arg = "--name {}".format(self.name_)
        graphic_arg = "--graphics vnc,listen=0.0.0.0,port={}".format(self.vnc_port_)
        root_disK_arg = "--disk path={},bus=virtio,format=qcow2".format(self.root_disk_)
        cloud_init_arg = "--disk {},device=cdrom".format(self.cloud_init_iso_)
        cpu_ram_arg = "--vcpus {} --ram {}".format(self.vcpus_, self.ram_)

        network_args = ""
        for nw in self.networks_:
            tmp_nw_cfg = "--network bridge={},model=virtio ".format(nw)
            network_args += tmp_nw_cfg

        os_var = ""
        if G.BASE_OS == "ubuntu":
            os_var = "ubuntu20.04"
        elif G.BASE_OS == "rocky":
            os_var = "rhel8.0"

        cmd = ("sudo virt-install --virt-type kvm --os-variant {} "
                          "{} {} {} {} {} {} --noautoconsole --import".format(
                              os_var, name_arg, cpu_ram_arg, graphic_arg, root_disK_arg,
                              cloud_init_arg, network_args))

        ExecuteCommand(cmd)


    def Create(self):
        logging.warning("Creating Virtual Machine : {}".format(self.name_))

        self.__generate_cloud_init_config()
        self.__generate_netplan_config()
        self.__create_root_disk()
        self.__generate_cloud_init_iso()

        self.__execute_virt_install_cmd()

    def Delete(self):
        logging.warning("Deleting Virtual Machine : {}".format(self.name_))

        cmd = "sudo virsh destroy {}".format(self.name_)
        ExecuteCommand(cmd)

        cmd = "sudo virsh undefine --remove-all-storage {}".format(self.name_)
        ExecuteCommand(cmd)

    def ToString(self) -> str:
        vm_str = ""
        vm_str += "Flavor : {}\n".format(self.flavor_)
        vm_str += "VNC : {}\n".format(self.vnc_port_)
        vm_str += "Networks : \n"
        for nw, ips in self.networks_.items():
            vm_str += "\t{} :\n\t\tv4 : {}\n\t\tv6 : {}\n".format(nw, ips.get("v4", None), ips.get("v6", None)) 
        vm_str += "===================================\n"
        return vm_str
