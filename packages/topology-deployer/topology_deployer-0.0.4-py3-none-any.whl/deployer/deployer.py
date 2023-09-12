from .topology import Topology
from .utils import ProcessArguments

def topology_deployer():
    conf_file = ProcessArguments()
    topology = Topology()
    topology.Init(conf_file)
