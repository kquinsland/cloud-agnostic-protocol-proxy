import digitalocean

from capp.cloud_providers.abstract import AbstractProvider


# Points to the class to load
_class = 'DigitalOcean'

# Debugging
from prettyprinter import pprint as pp

from os.path import isfile


class DigitalOcean(AbstractProvider):
    def __init__(self):
        super().__init__()

    @property
    def config(self):
        return self._api_config

    @config.setter
    def config(self, value):
        # Store
        self._api_config = value

    @property
    def api(self):
        return self._api

    def get_ips_by_cluster(self):
        """
        Coordinates the work of retrieving the IP addresses

        :return:
        """
        # First, check if we have an API or not, already
        if self._api is None:
            self.log.debug("self._api not yet spun up! Fixing that now...")
            self._init_api()

        # API should be inited, now we get all the nodes tagged with `k8s`
        droplets = self._api.get_all_droplets(tag_name="k8s")
        self.log.debug("got {} droplets".format(len(droplets)))

        _ips = {}
        for _d in droplets:
            _tags = _d.tags
            _ip4 = []
            _ip6 = []
            if len(_tags) is 1:
                continue

            # Get the cluster each node belongs to
            _cluster = self._get_k8_cluster(_tags)
            if _cluster not in _ips:
                _ips[_cluster] = {
                    '4': [],
                    '6': []
                }

            # Check if the node is part of any cluster we care about
            if _cluster in self._api_config['clusters']:
                _s = "node://{} ({}) has ip://{} and is part of the {} cluster"\
                    .format(_d.id, _d.name, _d.ip_address, _cluster)
                self.log.debug(_s)

                # Add the ipv4 address
                _ips[_cluster]['4'].append(_d.ip_address)
                # And the 6(s) if any
                if _d.ip_v6_address is not None:
                    _ips[_cluster]['6'].append(_d.ip_v6_address)

        return _ips

    def _get_api_auth(self):
        if 'api_auth_file' not in self._api_config:
            _e = "api auth file not set. Can't authenticate!. _api_config:{}".format(self._api_config)
            self.log.error(_e)
            raise Exception(_e)

        _file = self._api_config['api_auth_file']
        if not isfile(_file):
            _e = "api auth file could not be read.  Can't authenticate!. _api_config:{}".format(self._api_config)
            self.log.error(_e)
            raise Exception(_e)

        # otherwise, load the file :)
        with open(_file, 'r') as f:
            # Read the content of the file and strip any leading/trailing whitespaces
            return f.read().strip()

    def _init_api(self):
        # First thing we need to do is get the API auth
        self.log.debug("fetching api auth token...")
        _token = self._get_api_auth()
        self._api = digitalocean.Manager(token=_token)

    def _get_k8_cluster(self, tags: [str]):
        for t in tags:
            if t.startswith("k8s:"):
                _tokens = t.split(":")
                if _tokens[1] == "worker":
                    continue

                return _tokens[1]