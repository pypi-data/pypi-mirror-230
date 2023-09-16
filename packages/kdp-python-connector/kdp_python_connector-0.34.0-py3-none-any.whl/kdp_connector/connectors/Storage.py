import kdp_api
from kdp_api.api import storage_api
from kdp_api.model.job import Job

class StorageApi(object):

    def clear_dataset(self, config, dataset_id: str) -> Job:
        """This method will be used to clear dataset.

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset where the data will queried

            :returns: clear dataset job

            :rtype: Job
        """
        with kdp_api.ApiClient(config) as api_client:
            api_instance = storage_api.StorageApi(api_client)
            return api_instance.post_clear_dataset(dataset_id=dataset_id)
