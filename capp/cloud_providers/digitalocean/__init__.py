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
        self.log.info("value:{}".format(value))
        # Store
        self._api_config = value

    @property
    def api(self):
        return self._api

    def get_cluster_ips(self):
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

    def _get_api_auth(self):
        if 'api_auth_file' not in self._api_config:
            self.log.error("auth file not set")
            raise Exception()

        _file = self._api_config['api_auth_file']
        if not isfile(_file):
            self.log.error("auth file not accessible")
            raise Exception()

        # otherwise, load the file :)
        with open(_file, 'r') as f:
            # Read the content of the file and strip any leading/trailing whitespaces
            return f.read().strip()

    def _init_api(self):
        # First thing we need to do is get the API auth
        self.log.debug("fetching api auth token...")
        _token = self._get_api_auth()
        self._api = digitalocean.Manager(token=_token)



