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

import yaml

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


def get_provider_config(clusters: []):
    return {
        # Where the api auth can be loaded from
        'api_auth_file': './auth',
        # the k8 cluster(s) that we care about
        'clusters': clusters
    }


def launch(args: argparse.Namespace):
    """

    :return:
    """

    # First, get the user-given config map
    _cfg_map = get_config_map(args.config_file)

    _p = _cfg_map['cloud']['provider']
    log.info("Fetching the {} provider...".format(_p))
    provider = _get_provider(_p)

    log.info("Configuring provider...")
    provider.config = get_provider_config(_cfg_map['clusters'])

    log.info("Fetching IPs from provider...")
    _ips = provider.get_ips_by_cluster()

    # We now have a list of ip addresses by type for each node in the cluster(s) that we care about
    # Combine this w/ the specific user-driven tuples
    ##
    log.info("Combining IPs for {} cluster with the {} clusters from user".format(len(_ips), len(_cfg_map['clusters'])))
    for _cluster in _cfg_map['clusters']:
        _cfg_map['clusters'][_cluster].update(_ips[_cluster])

    log.info("Generating config files...")
    _static_file = build_traefik_config_files(_cfg_map['clusters'])
    _update_entrypoints_in_traefik_static_file(args.traefik_static_file, _static_file['entryPoints'])


def build_traefik_config_files(cfg: dict = {}):
    """
    Builds the data structures to be written out to the static and dynamic traefik config files
    :param cfg:
    :return:
    """
    _statics = {}

    for _cluster, _cluster_cfg in cfg.items():
        log.info("Generating the dynamic config for cluster://{}".format(_cluster))
        _dynamic = _build_traefik_dynamic_file(_cluster_cfg)

        # We can write out one 'dynamic' file per cluster
        _fname = "{}/{}.yaml".format(args.traefik_dynamic_dir, _cluster)
        with open(_fname, 'w') as f:
            yaml.dump(_dynamic, f)
        log.debug("wrote out: {}".format(_fname))

        # After the dynamic block(s) are created, we'll have to create the entrypoints for the static config
        # Unfortunately, Traefik does not support entrypoint loading from dynamic sources. This means that we must
        #   merge all the tcp/udp entrypoints
        ##
        log.info("Generating the static config for cluster://{}".format(_cluster))
        _static = _build_traefik_static_file(_cluster_cfg)

        # Now, merge the tcp/udp
        for _proto in _static:
            if 'entryPoints' not in _statics:
                _statics['entryPoints'] = []

            # The traefik static file does not care about proto as the root key as the proto is encoded in the listen
            #   address. We unwrap all the entrypoints that have so far been couched in tcp/udp and roll them all up
            #   under the entryPoints object
            _statics['entryPoints'].extend((_static[_proto]['entryPoints']))

    return _statics


def _build_traefik_dynamic_file(cluster_cfg: dict = {}):
    """
    Builds the dynamic configuration which declares the back end servers and the rules linking the entrypoints to them.
    The YAML representation of this function's output looks like:

        tcp:
          routers:
            tcp-to-skyhole:
              entryPoints:
                - "dot"
              rule: "HostSNI(`*`)"
              service: dot

          services:
            dot:
              loadBalancer:
                servers:
                - address: 64.227.101.3:30853
                - address: 64.227.106.125:30853

        udp:
          routers:
            udp-to-traccar:
              entryPoints:
                - "traccar"
              rule: "HostSNI(`*`)"
              service: traccar

          services:
            traccar:
              loadBalancer:
                servers:
                - address: 64.227.101.3:30007
                - address: 64.227.106.125:30007

    :return:
    """
    # _cluster_cfg will look like:
    # {
    #     'tcp': {
    #         'DoT': {'from': 853, 'to': 30853},
    #         'Test': {'from': 853, 'to': 30853}
    #     },
    #     'udp': {'traccar': {'from': 5172, 'to': 30007}},
    #     '4': ['64.227.101.3', '64.227.106.125'],
    #     '6': []
    # }

    _data = {}
    for _proto in ['tcp', 'udp']:
        _d = {}
        # Check for any services/backends that use this protocol
        if _proto in cluster_cfg:
            _data[_proto] = {}
            # We have a service defined for this protocol. Build the appropriate router/service sections
            ##
            # For each service that the user has defined...
            for _svc in cluster_cfg[_proto]:
                # ... there will be a from/to port
                _src_p = cluster_cfg[_proto][_svc]['from']
                _dst_p = cluster_cfg[_proto][_svc]['to']
                log.debug("service://{svc} listens on {src}/{proto} and forwards to {dst}/{proto}"
                          .format(svc=_svc, src= _src_p, dst=_dst_p, proto=_proto))

                # Combine the dst port w/ the cluster IPs and we've got everything we need :)
                _ip4 = cluster_cfg['4'] if '4' in cluster_cfg else None
                _ip6 = cluster_cfg['6'] if '6' in cluster_cfg else None
                # Join 4 and 6 for a list of app IPs
                _ips = _ip4 + _ip6

                for _obj in ['routers', 'services']:
                    if _obj == 'routers':
                        # It is *assumed* that the user is not going to define multiple services that listen on the same
                        #   port and protocol. The entrypoints are named exactly as the services are named
                        _d[_obj] = _make_router_block(_proto, _svc, [_svc])

                    if _obj == 'services':
                        # Same thing, but services
                        _d[_obj] = _make_services_block(_svc, _dst_p, _ips)

        _data[_proto].update(_d)
    return _data


def _build_traefik_static_file(cluster_cfg: dict = {}):
    """
    Generates the traefik static config file which drives thee port/protocol listeners / entrypoints
       entryPoints:
          ping:
            address: ":8081"
          traccar:
            address: ":5710/udp"
          DoT:
            address: ":853/tcp"
    :return:
    """
    _data = {}
    for _proto in ['tcp', 'udp']:
        _ep = {
            'entryPoints': []
        }
        # Check for any services/backends that use this protocol
        if _proto in cluster_cfg:
            _data[_proto] = {}
            for _svc in cluster_cfg[_proto]:
                # We have a service defined for this protocol. Pull out the 'from' port and turn that into the appropriate
                #   entrypoint blokc
                ##
                _src_p = cluster_cfg[_proto][_svc]['from']
                _d = {
                    _svc: {
                        'address': "{addr}:{port}/{proto}".format(addr='',port=_src_p, proto=_proto)
                    }
                }
                _ep['entryPoints'].append(_d)

        _data[_proto].update(_ep)
    return _data


def _make_router_block(proto: str, svc_name: str, entry_points: [str]):
    """
        tcp-to-skyhole:
            entryPoints:
                - "dot"
            rule: "HostSNI(`*`)"
            service: dot
    :return:
    """
    # Router name is proto + service
    _s = "{}-to-{}".format(proto, svc_name)
    return {
        _s: {
            'entryPoints': entry_points,
            'rule': "HostSNI(`*`)",
            'service': svc_name
        }
    }


def _make_services_block(svc_name: str, dest_port,  ip_addrs: [str]):
    """
        services:
            traccar:
                loadBalancer:
                    servers:
                        - address: 64.227.101.3:30007
                        - address: 64.227.106.125:30007
    :return:
    """
    # for each IP we need to combine w/ the dest port
    _a = []
    for ip in ip_addrs:
        _a.append({'address': "{backend_ip}:{backend_port}".format(backend_ip=ip, backend_port=dest_port)})

    return {
        svc_name: {
            'loadBalancer': {
                'servers': _a
            }
        }
    }


def _update_entrypoints_in_traefik_static_file(file: str, entrypoints: [{}]):
    """

    :param file:
    :param entrypoints:
    :return:
    """

    with open(file, 'r+') as f:
        # First, parse the existing entrypoints
        _static = yaml.safe_load(f)
        _existing = _static['entryPoints']
        log.debug("there are {} _existing entrypoint(s). Will add {} more...".format(len(_existing), len(entrypoints)))

        # Caller will provide entrypoints as a list of objects
        for ep in entrypoints:
            # Add our new entrypoints
            _existing.update(ep)

        # Copy the merged list of entrypoints back
        _static['entryPoints'] = _existing

        # Clear the file
        f.seek(0)
        f.truncate(0)

        # re-write
        yaml.dump(_static, f)
        log.info("Wrote {} entrypoints back to static config file".format(len(_existing)))


def get_config_map(map_file: str = ''):
    """
    Attempts to parse the configuration map
    :param map_file:
    :return:
    """
    with open(map_file, 'r') as f:
        return yaml.safe_load(f)


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
                        help='if set, the location logging  will be written to'
                        )

    parser.add_argument('--config-file',
                        default='./in.yaml',
                        type=str,
                        help='input config file'
                        )

    parser.add_argument('--traefik-dynamic-dir',
                        default='/etc/traefik/dynamic/',
                        type=str,
                        help='Where dooes traefik read dynamic configuration files from'
                        )
    parser.add_argument('--traefik-static-file',
                        default='/etc/traefik/traefik.yaml',
                        type=str,
                        help='traefik static config'
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
    log.info("GoodBye!")
    exit(0)
