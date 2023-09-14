import configparser
import os

from digitaltwins import Auth
from digitaltwins import IRODS
from digitaltwins import MetadataQuerier
from digitaltwins.utils.config_loader import ConfigLoader

from irods.session import iRODSSession


class Downloader(object):
    def __init__(self, config_file):
        self._configs = configparser.ConfigParser()
        self._configs.read(config_file)

        self._save_dir = "./tmp"

        self._irods = IRODS(self._configs)

    def execute(self, dataset_name=None, save_dir=None):
        if dataset_name is None:
            raise ValueError("Dataset not specified")
        if save_dir is None:
            save_dir = self._save_dir

        self._irods.download(dataset_name, save_dir)

    def _download_collection(self, session, collection_path, save_dir):
        dataset = session.collections.get(collection_path)
        save_dir = save_dir.joinpath(dataset.name)
        os.makedirs(save_dir, exist_ok=True)

        for obj in (dataset.data_objects):
            session.data_objects.get(obj.path, os.path.join(save_dir, obj.name))

        if dataset.subcollections:
            for subcollection in dataset.subcollections:
                self._download_collection(session, subcollection.path, save_dir)
        else:
            return

    # def __init__(self, data_storage_config, gen3_config=None, data_storage_type="pacs"):
    #     """
    #     Constructor
    #
    #     :param data_storage_config: Path to the data storage (PACS or iRods) configuration file (json)
    #     :type data_storage_config: string
    #     :param gen3_config: (Optional)
    #     :type gen3_config: Path to the Gen3 configuration file (json)
    #     """
    #     self._data_storage_configs = ConfigLoader.load_from_json(data_storage_config)
    #
    #     self._data_storage = self._data_storage_configs.get("storage")
    #     if data_storage_type:
    #         self._data_storage = data_storage_type
    #     else:
    #         self._data_storage = self._data_storage_configs.get("storage")
    #
    #     if gen3_config:
    #         self._gen3_config = ConfigLoader.load_from_json(gen3_config)
    #         self._gen3_endpoint = self._gen3_config.get("gen3_endpoint")
    #         self._gen3_cred_file = self._gen3_config.get("gen3_cred_file")
    #         self._gen3_auth = Auth(self._gen3_endpoint, self._gen3_cred_file)
    #         self._gen3_queryer = MetadataQuerier(self._gen3_auth)
    #
    #     if self._data_storage == "pacs":
    #         self._pacs_ip = self._data_storage_configs.get("pacs_ip")
    #         self._pacs_port = self._data_storage_configs.get("pacs_port")
    #         self._pacs_aec = self._data_storage_configs.get("pacs_aec")
    #         self._pacs_aet = self._data_storage_configs.get("pacs_aet")
    #
    #     elif self._data_storage == "irods":
    #         self._irods = IRODS(data_storage_config)
    #
    # def download_dataset(self, dataset_id, dest):
    #     """
    #     Downloading dataset (including data from PACS/iRods & metadata from Gen3) in SDS format
    #
    #     :param dataset_id: Dataset id/name on Gen3
    #     :type dataset_id: str
    #     :param dest: Path to the save folder
    #     :type dest: string
    #     """
    #     if self._data_storage == "pacs":
    #         # self._download(dataset_id)
    #         raise NotImplementedError("PACS: Storage location not implemented!")
    #     elif self._data_storage == "irods":
    #         self._irods.download_data(data=dataset_id, save_dir=dest)

    # def _download(self, dataset_id):
    #     gen3_query_string = """
    #     {
    #         experiment(submitter_id: "%s"){
    #             cases{
    #                 id
    #                 submitter_id,
    #                 subject_id,
    #             }
    #         }
    #     }
    #     """ % dataset_id
    #
    #     results = self._queryer.graphql_query(gen3_query_string)
    #     datasets = results.get("experiment")
    #
    #     study_uuids = list()
    #     for dataset in datasets:
    #         studies = dataset.get("cases")
    #         for study in studies:
    #             study_id = study.get("subject_id")
    #             study_uuid = study_id.replace("sub-", '')
    #             study_uuids.append(study_uuid)
    #
    #     for study_uuid in study_uuids:
    #         pacs_query_settings = {
    #             "StudyInstanceUID": study_uuid
    #         }
    #         pypacs.move_files(server_ip=self._pacs_ip,
    #                           server_port=self._pacs_port,
    #                           aec=self._pacs_aec,
    #                           aet=self._pacs_aet,
    #                           query_settings=pacs_query_settings)
