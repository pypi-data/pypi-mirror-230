import argparse
import logging
import shlex
import subprocess
import sys

# from .config import DRY_RUN, NO_NETWORK, NO_VM, PRINT_NETWORK, PRINT_VM
import deployer.globals as G
from .globals import OP_CREATE, OP_DELETE, ROCKY_TEMPLATE, UBUNTU_TEMPLATE


def ProcessArguments() -> str:
    parser = argparse.ArgumentParser(description="Parse topology config")

    parser.add_argument("-c", "--config", required=True,
                        help="JSON Config file that defines the topology")

    parser.add_argument("-o", "--operation", type=str, required=True,
                        choices=["create", "delete", "CREATE", "DELETE"], default="create",
                        help="Operation to create or delete topology from the JSON Config")

    parser.add_argument("-i", "--image", type=str,
                        choices=["ubuntu", "rocky"], default="ubuntu",
                        help="Choose the base OS image for the VMS")

    parser.add_argument("-l", "--log", type=str,
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the log level")
    parser.add_argument("--dry-run", action="store_true",
                        help="Instead of executing, print the commands")

    parser.add_argument("--recreate-nw", action="store_true",
                        help="[PREVIEW] Recreate the nat network")

    parser.add_argument("--print-nw", action="store_true", help="Print out created network details")
    parser.add_argument("--print-vm", action="store_true", help="Print out created VM details")

    skip_operation = parser.add_mutually_exclusive_group()
    skip_operation.add_argument("--no-network", action="store_true",
                                help="Skip creating networks. Cannot be used with --no-vm")
    skip_operation.add_argument("--no-vm", action="store_true",
                                help="Skip creating vms. Cannot be used with --no-network")

    args = parser.parse_args()

    if args.log:
        log_level = getattr(logging, args.log.upper(), None)
        if not isinstance(log_level, int):
            raise ValueError("Invalid log level: {}".format(args.log))
        logging.basicConfig(level=log_level)

    if args.dry_run:
        G.DRY_RUN = args.dry_run

    if args.operation.upper() == "CREATE":
        G.OP = OP_CREATE
    else:
        G.OP = OP_DELETE

    if args.no_network:
        G.NO_NETWORK = args.no_network

    if args.no_vm:
        G.NO_VM = args.no_vm

    if args.recreate_nw:
        G.RECREATE_NW = args.recreate_nw
        G.NO_VM = True

    if args.print_nw:
        G.PRINT_NETWORK = args.print_nw

    if args.print_vm:
        G.PRINT_VM = args.print_vm

    if args.image.lower() == "ubuntu":
        G.BASE_OS = "ubuntu"
        G.OS_IMAGE_TEMPLATE = UBUNTU_TEMPLATE
    elif args.image.lower() == "rocky":
        G.BASE_OS = "rocky"
        G.OS_IMAGE_TEMPLATE = ROCKY_TEMPLATE
    else:
        logging.critical("Invalid image argument")
        sys.exit(1)

    return args.config

def ExecuteCommand(cmd: str) -> None:
    if not G.DRY_RUN:
        logging.info("Executing command : {}".format(cmd))
        ret = subprocess.call(shlex.split(cmd))
        if ret != 0:
            logging.error("Command {} failed wih return code : {}".format(cmd, ret))
            sys.exit(ret)
    else:
        logging.debug("Dry Run enabled. Command : {}".format(cmd))

def ExecuteCommandWithOutput(cmd: str) -> str:
    logging.info("Executing command : {}".format(cmd))
    res = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        logging.error("Command {} failed wih return code : {}".format(cmd, res.returncode))
        logging.error("Error message : {}".format(res.stderr))
        sys.exit(res.returncode)
    return res.stdout.decode('utf-8').strip()
