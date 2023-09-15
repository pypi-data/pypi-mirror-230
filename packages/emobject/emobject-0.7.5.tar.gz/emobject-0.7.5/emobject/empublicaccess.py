import os
import requests
import xml.etree.ElementTree as ET
from typing import Optional, Union
from botocore import UNSIGNED
from botocore.config import Config
from botocore.session import Session
import botocore


class EMPublicDataConnector:
    """
    Connector class for accessing the public data bucket.
    """

    def __init__(self, bucket_name: Optional[str] = "enable-medicine-public-data"):
        """
        Args:
            bucket_name (str): name of the S3 bucket
        """
        self.bucket_name = bucket_name
        self.emobjects = self.__get_all_available_emobjects()
        self.datasets = list(self.emobjects.keys())

        self.session = Session()
        self.client = self.session.create_client(
            "s3", config=Config(signature_version=UNSIGNED), region_name="us-west-2"
        )

    def download_emobjects(
        self, emobjects: Union[str, list] = None, out_dir: Optional[str] = None
    ) -> None:
        """
        Download emObjects from the public data bucket

        Args:
            emobjects (str or list): name of the emObject(s) to download
            outdir (str): path to the output directory

        Returns:
            None
        """

        if isinstance(emobjects, str):
            emobjects = [emobjects]

        if out_dir is None:
            out_dir = os.getcwd()

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for emobject in emobjects:
            print(f"Downloading {emobject}")
            study = self.__get_study_from_object_name(emobject)
            self._download_all_files_for_emobject(
                study=study, object_name=emobject, out_dir=out_dir
            )

    def _download_all_files_for_emobject(
        self, study: str = None, object_name: str = None, out_dir: str = None
    ) -> None:
        """
        Download all files for a given emObject

        Args:
            study (str): name of the study
            object_name (str): name of the emObject
            out_dir (str): path to the output directory

        Returns:
            None

        """

        response = self.client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=f"emObjects/{study}/{object_name}"
        )

        objects = []
        if "Contents" in response:
            for obj in response["Contents"]:
                objects.append(obj["Key"])

        for obj in objects:
            try:
                file_name = obj.replace(f"emObjects/{study}/", "")  # for saving.
                local_file_path = os.path.join(out_dir, file_name)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                try:
                    response = self.client.get_object(Bucket=self.bucket_name, Key=obj)
                except botocore.exceptions.ClientError as e:
                    print(f"Error downloading {obj}: {e}")
                    raise
                with open(local_file_path, "wb") as f:
                    f.write(response["Body"].read())
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    print(f"The object does not exist: {obj}")
                else:
                    raise

    def __get_available_datasets(self) -> list:
        """
        Get a list of available datasets from the S3 bucket

        Args:
            None

        Returns:
            datasets (list): list of dataset names
        """

        datasets = []
        url = f"https://{self.bucket_name}.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=emObjects/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                namespace = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}

                prefixes = root.findall(".//s3:CommonPrefixes/s3:Prefix", namespace)
                for prefix in prefixes:
                    subdir = prefix.text.replace("emObjects/", "")
                    datasets.append(subdir.split("/")[0])
            else:
                print(f"Error accessing bucket. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error accessing bucket: {e}")

        return datasets

    def __get_available_dataset_emobjects(self, dataset_name: str = None) -> list:
        """
        Get a list of available emObjects for a given dataset from the S3 bucket

        Args:
            dataset_name (str): name of the dataset

        Returns:
            emobjects (list): list of emObject names
        """

        emobjects = []
        url = f"https://{self.bucket_name}.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=emObjects/{dataset_name}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                namespace = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}

                prefixes = root.findall(".//s3:CommonPrefixes/s3:Prefix", namespace)
                for prefix in prefixes:
                    subdir = prefix.text.replace(f"emObjects/{dataset_name}", "")
                    subdir = subdir.replace("/", "")
                    if subdir.endswith(".zarr"):
                        emobjects.append(subdir)
            else:
                print(f"Error accessing bucket. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error accessing bucket: {e}")

        return emobjects

    def __get_all_available_emobjects(self) -> dict:
        """
        Gets a list of all available emObjects from the S3 bucket, separated by dataset

        Args:
            None

        Returns:
            emobjects (dict): dictionary of emObjects, separated by dataset
        """

        emobjects = {}
        datasets = self.__get_available_datasets()
        for dataset in datasets:
            emobjects[dataset] = self.__get_available_dataset_emobjects(dataset)

        return emobjects

    def __get_study_from_object_name(self, object_name: str) -> str:
        """
        Gets the study name from an emObject name

        Args:
            object_name (str): name of the emObject

        Returns:
            study (str): name of the study
        """

        # object name is a value in the dict, so we need to find the key

        for study, objects in self.emobjects.items():
            if object_name in objects:
                return study
