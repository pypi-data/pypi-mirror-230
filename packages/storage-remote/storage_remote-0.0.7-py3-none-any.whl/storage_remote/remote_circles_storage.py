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
        self.url: str = UrlCirclez.endpoint_url(
            BRAND_NAME, ENVIRONMENT_NAME, ComponentName.GROUP_PROFILE.value,
            EntityName.GROUP_PROFILE.value, 1, "graphql")

    def put(self, file_name: str, local_path: str, created_user_id: str, entity_type_id: str, profile_id: str) -> str:
        """Uploads a file to the remote storage and returns the file's remote path"""
        put_query = f"""
        mutation {{
          put(
            fileName: "{file_name}",
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

    def download(self, file_name: str, entity_type_id: str, profile_id: str, local_path: str) -> str:
        """Downloads a file from the remote storage and returns the file's contents"""
        download_query = f"""
        mutation {{
          download(
            fileName: "{file_name}",
            entity_type_id: "{entity_type_id}",
            profile_id: "{profile_id}",
            localPath: "{local_path}"
          )
        }}
        """
        response = requests.post(self.url, json={"query": download_query})

        response_data = response.json().get("data", {})
        if "errors" in response_data:
            raise Exception(response_data["errors"][0]["message"])

        return response_data["download"]
