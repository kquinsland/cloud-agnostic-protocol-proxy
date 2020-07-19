from abc import ABCMeta, abstractmethod

import logging


class AbstractProvider(metaclass=ABCMeta):
    """
    Abstract / Interface for cloud providers
    """
    def __init__(self):
        # A logging object
        self.log = logging.getLogger(__name__)

        # The object used to configure the actual API
        self._api_config = None

        # The actual API object
        self._api = None

    @property
    @abstractmethod
    def config(self):
        pass

    @config.setter
    @abstractmethod
    def config(self, value):
        pass

    @property
    @abstractmethod
    def api(self):
        pass

    @abstractmethod
    def get_cluster_ips(self):
        pass
