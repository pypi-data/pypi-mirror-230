import configparser
from digitaltwins.irods.irods import IRODS


class Deleter(object):
    def __init__(self, config_file):
        self._configs = configparser.ConfigParser()
        self._configs.read(config_file)

        self._program = self._configs["gen3"].get("program")
        self._project = self._configs["gen3"].get("project")

    def execute(self, dataset_name):
        self._delete_metadata(dataset_name)
        self._delete_dataset(dataset_name)
        pass

    def _delete_metadata(self, dataset_name):
        pass

    def _delete_dataset(self, dataset_name):
        pass
