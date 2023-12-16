import argparse
import json
import logging
import os
import shlex
import subprocess
import sys
from importlib import import_module


def ssh_connect(host, args):
    """
    Assemble SSH command and run ssh using subprocess.

    Args:
        host: Host object to connect to.
        args: Arguments which are not known by ssht and should be passed along to ssh.
    """
    logging.debug("args = %s", args)

    # Connect to IPv6 if forced
    if hasattr(host, "ipv6") and host.ipv6 and "-6" in args:
        ssh_cmds = shlex.split(f"ssh {host.ipv6}")
        print(f'Connecting to "{host.hostname}" ({host.ipv6})')
    # Connect to IPv4 if specified
    elif hasattr(host, "ipv4") and host.ipv4:
        ssh_cmds = shlex.split(f"ssh {host.ipv4}")
        print(f'Connecting to "{host.hostname}" ({host.ipv4})')
    # Connect on host name
    else:
        ssh_cmds = shlex.split(f"ssh {host.hostname}")
        print(f'Connecting to "{host.hostname}"')
    logging.debug("ssh_cmds = %s", ssh_cmds)

    # Connect to host port
    if hasattr(host, "port") and host.port is not None and "-p" not in args:
        ssh_cmds += shlex.split(f"-p {host.port}")

    # Connect as user
    if hasattr(host, "user") and host.user is not None and "-l" not in args:
        ssh_cmds += shlex.split(f"-l {host.user}")

    logging.debug("ssh_cmds = %s %s", ssh_cmds, args)
    subprocess.call(ssh_cmds + args)


def select_host(hosts):
    """
    Print the list of hosts with a reference number from which the user can choose.

    Args:
        hosts: List of Host objects.

    Returns:
        Selected host.
    """
    for idx, host in enumerate(hosts):
        if hasattr(host, "user") and host.user is not None:
            print(f"{idx + 1}) {host.user}@{host.hostname}")
        else:
            print(f"{idx + 1}) {host.hostname}")
    option = get_answer("Connect to: ")
    try:
        return hosts[int(option) - 1]
    except ValueError:
        return None


def get_answer(text: str) -> str:
    """
    Get input from user.

    Args:
        text: The text to display before the input.

    Returns:
        The users input or an empty string.
    """
    try:
        return input(text)
    except SyntaxError:
        return ""


def get_log_level():
    """
    Get the loglevel depending on debugging being enabled or not.

    Returns:
        Log level
    """
    if os.getenv("SSHT_DEBUG", None):
        return logging.DEBUG
    return logging.WARNING


def main():  # pylint: disable=too-many-locals
    """Get and filter hosts based on arguments."""
    try:
        logging.basicConfig(level=get_log_level())

        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument("name", help="name of the host to connect to")
        args, unknown = arg_parser.parse_known_args()

        home_dir = os.path.expanduser("~")
        config_path = os.path.join(home_dir, ".ssht", "config.json")

        # Read generic config file.
        config = {}
        try:
            with open(config_path, encoding="utf8") as fh:
                config = json.loads(fh.read())
        except FileNotFoundError:
            logging.debug("Config file %s is missing", config_path)
        except ValueError as e:
            logging.debug("Config file %s invalid: %s", config_path, e)

        # Define default parsers for backwards compatibility.
        parsers = [
            "ssht.plugins.JsonParser",
            "ssht.plugins.MySQLParser",
            "ssht.plugins.APIParser",
        ]
        # Use configured parsers if defined.
        if "parsers" in config:
            logging.debug("Using configured parsers")
            parsers = config["parsers"]

        hosts = []
        for module_path in parsers:
            # Split module and class name.
            _module = ".".join(module_path.split(".")[:-1])
            _class = module_path.split(".")[-1:][0]

            # Dynamically import and execute the parsers.
            try:
                parser = getattr(import_module(_module), _class)
            except ImportError as e:
                logging.error("Error loading %s: %s", module_path, e)
                continue
            p = parser(os.path.join(home_dir, ".ssht"))
            hosts.extend(p.search(args.name))

        logging.info(hosts)

        host = None
        if len(hosts) == 1:
            host = hosts[0]
        elif len(hosts) > 1:
            host = select_host(hosts)

        if host is None:
            print("No host, exiting.")
            sys.exit(0)

        ssh_connect(host, unknown)
    except KeyboardInterrupt:
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
