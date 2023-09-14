from typing import IO, List
from solar_api.classes.httpclient import HttpClient
from solar_api.services.dataset import DatasetService
from solar_api.services.datasetfile import DatasetFileService
from solar_api.classes.dataset import Dataset
from solar_api.classes.datasetfile import DatasetFile
from solar_api.classes.solarexception import DatasetNameAlreadyExists
from solar_api.util.upload_helper import upload
from urllib.parse import urlencode
import requests;

class SolarApi:
    '''Wrapper class for invoking Solar API

    Parameters
    ----------
    base_url : str
        The url to your Tonic instance. Do not include trailing backslashes
    api_key : str
        Your api token

    Examples
    --------
    >>> SolarApi("http://localhost:3000", "your_api_key")
    '''
    def __init__(self, base_url : str, api_key: str):
        self.client = HttpClient(base_url, api_key)
        self.dataset_service = DatasetService(self.client)
        self.datasetfile_service = DatasetFileService(self.client)

    def create_dataset(self, dataset_name:str):
        """Create a dataset, which is a collection of 1 or more files.

        Parameters
        -----
        dataset_name : str
            The name of the dataset.  Dataset names must be unique.


        Returns
        -------
        Dataset
            The newly created dataset
        """
        try:
            self.client.http_post("/api/dataset", data={"name": dataset_name})
        except requests.exceptions.HTTPError as e:
            if e.response.status_code==409:
                raise DatasetNameAlreadyExists(e)

        return self.get_dataset(dataset_name)

    def delete_dataset(self, dataset_name: str):
        params = { "datasetName": dataset_name}
        self.client.http_delete("/api/dataset/delete_dataset_by_name?" + urlencode(params))


    def upload_file(self, file_path: str, file_name: str) -> DatasetFile:
        """Upload file to Solar

        Parameters
        --------
        file_path : str
            Absolute path to file to be uploaded
        file_name : str
            Desired name of file once saved to Solar

        Returns
        -------
        DatasetFile
        A DatasetFile object represented the just uploaded file


        Examples
        --------
        >>> with open('<path to file>','r') as f:
                solar.upload_file(f, '<file name>')
        """

        return upload(file_path, file_name, self.client)



    def get_dataset(self, dataset_name : str) -> Dataset:
        '''Get instance of Workspace class with specified workspace_id.

        Parameters
        ----------
        dataset_name : str
            The name for your dataset

        Returns
        -------
        Dataset

        Examples
        --------
        >>> dataset = tonic.get_dataset("llama_2_chatbot_finetune_v5")
        '''
        return self.dataset_service.get_dataset(dataset_name)

    def get_files(self) -> List[DatasetFile]:
        """
        Gets all files

        Returns
        ------
        List[DatasetFile]
        A list of all files
        """
        return self.datasetfile_service.get_files()