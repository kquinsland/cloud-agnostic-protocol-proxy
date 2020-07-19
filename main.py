# Basci CLI interface
import argparse

# Debugging
from prettyprinter import pprint as pp
import logging

# Dynamically load the cloud provider class
import importlib

# Load the git hash
from capp.version import __version__

# Wrapper to make the logging class a bit ... easier to use
from utils.log import  LogCfg

# Get a simple logger for the few functions in this file
log = logging.getLogger(__name__)


def _get_provider(provider: str):
    """
    Returns a concrete cloud_provider class
    :param provider:
    :return:
    """

    # Add the provider name to build the path
    _pkg = 'capp.cloud_providers.{}'.format(provider)
    log.debug("_pkg: {}".format(_pkg))

    # Load the module by path
    _provider_mod = importlib.import_module(_pkg)

    # Get the class name that the module wants us to use
    _class = getattr(_provider_mod, '_class')
    log.debug("_class: {}".format(_class))

    # Get a class _from_ the module
    _provider_class = getattr(_provider_mod, _class)

    # Make instance of class
    return _provider_class()


def get_provider_config():
    return {
        'api_auth_file': './auth'
    }


def launch(args: argparse.Namespace):
    """

    :return:
    """
    _p = 'digitalocean'
    log.info("Fetching the {} provider...".format(_p))
    provider = _get_provider(_p)

    # TODO: Parse the API config out of a YAML file.
    # For now, we have a hard_coded one
    ##
    log.info("configuring provider...")
    provider.config = get_provider_config()

    log.info("Fetching IPs from provider...")
    provider.get_cluster_ips()


    #
    # for drop in droplets:
    #     # Check tags for k8 cluster membership information
    #     _tags = drop.tags
    #     if len(_tags) is 1:
    #         continue
    #
    #     # Pull a few useful things out
    #     _id = drop.id
    #     _name = drop.name
    #     _ip_4_pub = drop.ip_address
    #
    #     # Check if we have k8 tags
    #     if 'k8s' in _tags:
    #         # Get the cluster out of those tags
    #         _cluster = get_k8_cluster(_tags)
    #
    #         # Check if it's a cluster we care about
    #         if _cluster in CLUSTER_TO_IP_MAP:
    #             # It's a cluster we care about.
    #             _s = "node://{} ({}) has ip://{} and is part of the {} cluster".format(
    #                 _id, _name, _ip_4_pub, _cluster)
    #             logging.error(_s)

                # Now, what proxy



        # pp(drop.name)
        # pp(drop.ip_address)
        # pp(drop.ip_v6_addres)

        # print(dir(drop))
        # exit()


def get_k8_cluster(tags: [str]):
    for t in tags:
        if t.startswith("k8s:"):
            _tokens = t.split(":")
            if _tokens[1] == "worker":
                continue

            return _tokens[1]


def get_config_map(map_file: str = ''):
    """
    Attempts to parse the configuration map
    :param map_file:
    :return:
    """
    # TODO: this should actually be parsed from Yaml / validated!
    ##
    # for now we have a hard-coded map for DNS over TLS and Traccar
    return {
        "606aeaef-2872-4e60-aa11-852241536571": {
            "tcp": {
                # Take ingress on TCP/853
                "from": 853,
                "to": 30853
            },
            "udp": {
                # UDP 5170 -> Cluster:30007
                "from": 5170,
                "to": 30007
            }
        }
    }


def set_logging(args: argparse.Namespace):

    # LogInfo expects a Dict, we pull what we need out of args
    log_opts = {
        'log_level': args.log_level,
        'log_file': args.log_file
    }

    # Pass in the user config to LogInfo. Creation of which will configure the root logger
    LogCfg(log_opts)


def parse_args():
    """
    This script does very little, so there's not much to configure. Additionally, what can be configured
        is likely not going to change often so it's best to just leave things in a config file.
    :return:
    """

    # Root argparse
    parser = argparse.ArgumentParser(
        description='Collection of tools to automate the upkeep of ToDoist',
        epilog='Push that blue button...',
        allow_abbrev=False)

    parser.add_argument('--version', action='version', version=__version__)

    ###
    # LOGGING
    ###
    _log_default = 'INFO'
    parser.add_argument('--log-level',
                        default=_log_default,
                        choices=logging._nameToLevel.keys(),
                        help='Set log level. Defaults to {}'.format(_log_default)
                        )

    parser.add_argument('--log-file',
                        default=None,
                        type=str,
                        help='if set, the path to log to. If not set, stdout is used'
                        )

    parser.add_argument('--provider',
                        default='digitalocean',
                        type=str,
                        help='the default cloud provider'
                        )

    return parser.parse_args()


if __name__ == '__main__':
    # Begin by parsing any arguments from the client
    args = parse_args()

    set_logging(args)

    # Assuming that nothing has blown up, we launch the tool
    launch(args)

    # And assuming that nothing there blew up, we exit
    exit(0)

