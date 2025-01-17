#!/usr/bin/env python3

"""
This is the entry point for roll-op system, responsible for parsing command line arguments and
invoking the appropriate commands.
"""

import argparse

import deps
import libroll as lib
from setup import setup


####################################################################################################

parser = argparse.ArgumentParser(
    description="Helps you spin up an op-stack rollup.")

subparsers = parser.add_subparsers(
    title="commands",
    dest="command",
    metavar="<command>")

subparsers.add_parser(
    "setup",
    help="installs prerequisites and builds the optimism repository")

subparsers.add_parser(
    "l1",
    help="spins up a local L1 node with the rollup contracts deployed on it")

subparsers.add_parser(
    "l2-execution",
    help="spins up a local op-geth node")

subparsers.add_parser(
    "devnet",
    help="spins up a local devnet, comprising an L1 node and all L2 components")

subparsers.add_parser(
    "clean",
    help="cleans up build outputs")

parser.add_argument(
    "--no-ansi-esc",
    help="disable ANSI escape codes for terminal manipulation",
    default=True,
    dest="use_ansi_esc",
    action="store_false")

parser.add_argument(
    "--stack-trace",
    help="display exception stack trace in case of failure",
    default=False,
    dest="show_stack_trace",
    action="store_true")

####################################################################################################

if __name__ == "__main__":
    lib.args = parser.parse_args()
    try:
        if lib.args.command is None:
            parser.print_help()
            exit()

        deps.basic_setup()
        deps.check_basic_prerequisites()

        if lib.args.command == "setup":
            setup()

        if lib.args.command == "l1":
            deps.check_or_install_foundry()
            deps.check_or_install_geth()
            import l1
            import paths
            l1.deploy_devnet_l1(paths.OPPaths("optimism"))
            from processes import PROCESS_MGR
            PROCESS_MGR.wait_all()

        if lib.args.command == "l2-execution":
            deps.check_or_install_op_geth()
            import l2_execution
            import paths
            l2_execution.deploy_l2(paths.OPPaths("optimism"))
            from processes import PROCESS_MGR
            PROCESS_MGR.wait_all()

        if lib.args.command == "devnet":
            # TODO refactor
            deps.check_or_install_foundry()
            deps.check_or_install_geth()
            from paths import OPPaths
            paths = OPPaths("optimism")

            import l1
            l1.deploy_devnet_l1(paths)

            deps.check_or_install_op_geth()
            import l2_execution
            l2_execution.deploy_l2(paths)

            from processes import PROCESS_MGR
            PROCESS_MGR.wait_all()

        if lib.args.command == "clean":
            import l1
            import l2_execution
            import paths
            l1.clean(paths.OPPaths("optimism"))
            l2_execution.clean(paths.OPPaths("optimism"))

        print("Done.")
    except KeyboardInterrupt:
        # Usually not triggered because we will exit via the exit hook handler.
        print("Interrupted by user.")
    except Exception as e:
        if lib.args.show_stack_trace:
            raise e
        else:
            print(f"Aborted with error: {e}")

####################################################################################################
