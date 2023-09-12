import random

from .utils import ExecuteCommand, ExecuteCommandWithOutput

def CheckForwarding() -> None:
    cmd = "cat /proc/sys/net/ipv4/ip_forward"
    if ExecuteCommandWithOutput(cmd) != "1":
        ExecuteCommand("sudo sh -c 'echo \"net.ipv4.ip_forward=1\" >> /etc/sysctl.conf'")

    cmd = "cat /proc/sys/net/ipv4/conf/all/forwarding"
    if ExecuteCommandWithOutput(cmd) != "1":
        ExecuteCommand("sudo sh -c 'echo \"net.ipv4.conf.all.forwarding=1\" >> /etc/sysctl.conf'")

    cmd = "cat /proc/sys/net/ipv6/conf/all/forwarding"
    if ExecuteCommandWithOutput(cmd) != "1":
        ExecuteCommand("sudo sh -c 'echo \"net.ipv6.conf.all.forwarding=1\" >> /etc/sysctl.conf'")

    ExecuteCommand("sudo sysctl -p")


def GetMacAddress() -> str:
    mac = "52:54:00:%02x:%02x:%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))

    return mac

def AddLinuxBridge(name: str, ip4: str, ip6: str, plen4: int, plen6: int) -> None:
    mac_address = GetMacAddress()
    dummy_intf = "{}-nic".format(name)
    ExecuteCommand("sudo ip link add {} address {} type dummy".format(dummy_intf, mac_address))
    ExecuteCommand("sudo brctl addbr {}".format(name))
    ExecuteCommand("sudo brctl stp {} on".format(name))
    ExecuteCommand("sudo brctl addif {} {}".format(name, dummy_intf))
    ExecuteCommand("sudo ip address add {}/{} dev {}".format(ip4, plen4, name))
    if ip6 != "None":
        ExecuteCommand("sudo ip -6 address add {}/{} dev {}".format(ip6, plen6, name))
    ExecuteCommand("sudo ip link set dev {} up".format(dummy_intf))
    ExecuteCommand("sudo ip link set dev {} up".format(name))

def AddIptableRules(name: str, nw4: str) -> None:
    ExecuteCommand("sudo iptables -t mangle -A POSTROUTING "
                   "-o {} -p udp -m udp --dport 68 -j CHECKSUM --checksum-fill".format(name))
    ExecuteCommand("sudo iptables -t nat -A POSTROUTING "
                   "-s {} -d 224.0.0.0/24 -j RETURN".format(nw4))
    ExecuteCommand("sudo iptables -t nat -A POSTROUTING "
                   "-s {} -d 255.255.255.255/32 -j RETURN".format(nw4))
    ExecuteCommand("sudo iptables -t nat -A POSTROUTING "
                   "-s {} ! -d {} -p tcp -j MASQUERADE --to-ports 1024-65535".format(nw4, nw4))
    ExecuteCommand("sudo iptables -t nat -A POSTROUTING "
                   "-s {} ! -d {} -p udp -j MASQUERADE --to-ports 1024-65535".format(nw4, nw4))
    ExecuteCommand("sudo iptables -t nat -A POSTROUTING -s {} ! -d {} -j MASQUERADE".format(nw4, nw4))
    ExecuteCommand("sudo iptables -t filter -A INPUT "
                   "-i {} -p udp -m udp -m multiport --dports 53,67 -j ACCEPT".format(name))
    ExecuteCommand("sudo iptables -t filter -A INPUT -i "
                   "{} -p tcp -m tcp -m multiport --dports 53,67 -j ACCEPT".format(name))
    ExecuteCommand("sudo iptables -t filter -A FORWARD -d {} -o {} -j ACCEPT".format(nw4, name))
    ExecuteCommand("sudo iptables -t filter -A FORWARD -s {} -i {} -j ACCEPT".format(nw4, name))
    ExecuteCommand("sudo iptables -t filter -A FORWARD -i {} -j ACCEPT".format(name))
    ExecuteCommand("sudo iptables -t filter -A FORWARD -o {} -j ACCEPT".format(name))
    ExecuteCommand("sudo sh -c 'iptables-save > /etc/iptables/rules.v4'")

def DelLinuxBridge(name: str) -> None:
    dummy_intf = "{}-nic".format(name)
    ExecuteCommand("sudo ip link set dev {} down".format(dummy_intf))
    ExecuteCommand("sudo ip link set dev {} down".format(name))
    ExecuteCommand("sudo ip link del {}".format(dummy_intf))
    ExecuteCommand("sudo ip link del {}".format(name))

def DelIptableRules(name: str, nw4: str) -> None:
    ExecuteCommand("sudo iptables -t mangle -D POSTROUTING "
                   "-o {} -p udp -m udp --dport 68 -j CHECKSUM --checksum-fill".format(name))
    ExecuteCommand("sudo iptables -t nat -D POSTROUTING "
                   "-s {} -d 224.0.0.0/24 -j RETURN".format(nw4))
    ExecuteCommand("sudo iptables -t nat -D POSTROUTING "
                   "-s {} -d 255.255.255.255/32 -j RETURN".format(nw4))
    ExecuteCommand("sudo iptables -t nat -D POSTROUTING "
                   "-s {} ! -d {} -p tcp -j MASQUERADE --to-ports 1024-65535".format(nw4, nw4))
    ExecuteCommand("sudo iptables -t nat -D POSTROUTING "
                   "-s {} ! -d {} -p udp -j MASQUERADE --to-ports 1024-65535".format(nw4, nw4))
    ExecuteCommand("sudo iptables -t nat -D POSTROUTING -s {} ! -d {} -j MASQUERADE".format(nw4, nw4))
    ExecuteCommand("sudo iptables -t filter -D INPUT "
                   "-i {} -p udp -m udp -m multiport --dports 53,67 -j ACCEPT".format(name))
    ExecuteCommand("sudo iptables -t filter -D INPUT -i "
                   "{} -p tcp -m tcp -m multiport --dports 53,67 -j ACCEPT".format(name))
    ExecuteCommand("sudo iptables -t filter -D FORWARD -d {} -o {} -j ACCEPT".format(nw4, name))
    ExecuteCommand("sudo iptables -t filter -D FORWARD -s {} -i {} -j ACCEPT".format(nw4, name))
    ExecuteCommand("sudo iptables -t filter -D FORWARD -i {} -j ACCEPT".format(name))
    ExecuteCommand("sudo iptables -t filter -D FORWARD -o {} -j ACCEPT".format(name))
    ExecuteCommand("sudo sh -c 'iptables-save > /etc/iptables/rules.v4'")
    pass
