import requests
import os
from dotenv import load_dotenv
from url_local.url_circlez import UrlCirclez
from url_local.component_name_enum import ComponentName
from url_local.entity_name_enum import EntityName

load_dotenv()
BRAND_NAME: str = os.getenv('BRAND_NAME')
ENVIRONMENT_NAME: str = os.getenv('ENVIRONMENT_NAME')


class RemoteCirclesStorage:
    def __init__(self) -> None:
        # TODO Please replace all strings and Magic Numbers such as "graphql" to const enum
        version = 1
        action = "graphql"
        self.url: str = UrlCirclez.endpoint_url(
            BRAND_NAME, ENVIRONMENT_NAME, ComponentName.GROUP_PROFILE.value,
            EntityName.GROUP_PROFILE.value, version, action)

    def put(self, filename: str, local_path: str, created_user_id: int, entity_type_id: int, profile_id: int) -> str:
        """
        Uploads a file to the remote storage and returns the file's remote path.

        :param filename: The name of the file.
        :param local_path: The local path to the file on your system.
        :param created_user_id: The ID of the user who created the file.
        :param entity_type_id: The ID of the entity type associated with the file.
        :param profile_id: The ID of the profile associated with the file.
        :return: The remote path of the uploaded file.
        """
        put_query = f"""
        mutation {{
          put(
            filename: "{filename}",
            local_path: "{local_path}",
            created_user_id: "{created_user_id}",
            entity_type_id: "{entity_type_id}",
            profile_id: "{profile_id}"
          )
        }}"""
        response = requests.post(self.url, json={"query": put_query})

        response_data = response.json().get("data", {})
        if "errors" in response_data:
            raise Exception(response_data["errors"][0]["message"])

        return response_data["put"]

    def download(self, filename: str, local_path: str, entity_type_id: int, profile_id: int) -> str:
        """
        Downloads a file from the remote storage and returns the file's contents.

        :param filename: The name of the file to download.
        :param entity_type_id: The ID of the entity type associated with the file.
        :param profile_id: The ID of the profile associated with the file.
        :param local_path: The local path where the downloaded file should be saved.
        :return: The contents of the downloaded file.
        """
        download_query = f"""
        mutation {{
          download(
            filename: "{filename}",
            entity_type_id: "{entity_type_id}",
            profile_id: "{profile_id}",
            local_path: "{local_path}"
          )
        }}
        """
        response = requests.post(self.url, json={"query": download_query})

        response_data = response.json().get("data", {})
        if "errors" in response_data:
            raise Exception(response_data["errors"][0]["message"])

        return response_data["download"]
