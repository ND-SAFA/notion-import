import json
import logging
import os
from typing import Dict, List, Union

from notion_client import APIResponseError, Client
from notion_client.helpers import collect_paginated_api

from paths import DATA_PATH


class NotionAPI:
    """
    A class to handle interacting with the Notion API.
    """

    def __init__(self):
        self.client = Client(
            auth=os.environ["NOTION_TOKEN"],
            log_level=logging.INFO,
        )

    def get_db(self, db_id: str) -> List[Dict]:
        """
        Gets a page from the database with the given id.
        :param db_id: The database to pull from.
        :return: The database data.
        """
        try:
            return collect_paginated_api(
                self.client.databases.query, database_id=db_id
            )
        except APIResponseError as error:
            logging.error(error)

    def get_block(self, block_id: str) -> Dict:
        """
        Gets a page from notion with the given id.
        :param block_id: The page to pull from.
        :return: The page data.
        """
        res = {}

        try:
            res = self.client.blocks.children.list(block_id=block_id)
        except Exception as error:
            logging.error(error)

        return res

    def save_local(self, db_data: Union[Dict, List], file_name: str) -> None:
        """
        Stores the given data in a local formatted JSON file.
        :param db_data: The database data to save the records of.
        :param file_name: The name of the file to store the data in.
        """
        with open(f"{DATA_PATH}/{file_name}.json", "w") as json_file:
            json.dump(db_data, json_file, indent=4)

    def load_local(self, file_identifier: str):
        """
        Loads the given data from a local formatted JSON file.
        :param file_identifier: The name of the file to load the data from.
        :return:
        """
        file_name = f"{file_identifier}.json"
        file_path = os.path.join(DATA_PATH, file_name)
        with open(file_path, "r") as json_file:
            return json.load(json_file)
