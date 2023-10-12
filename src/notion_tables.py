import os
from enum import Enum
from typing import Dict, List, Any, Union, Tuple

from notion_api import NotionAPI
from notion2md.exporter.block import StringExporter

notion = NotionAPI()

table_id = os.environ["NOTION_TABLE_ID"]
field_id_type = os.environ["NOTION_FIELD_ID_TYPE"]
field_id_parents = os.environ["NOTION_FIELD_ID_PARENTS"]
field_id_filter = os.environ["NOTION_FIELD_ID_FILTER"]
field_value_filter = os.environ["NOTION_FIELD_VALUE_FILTER"].split(",")


class NotionFieldType(Enum):
    NAME = "Name"
    BODY = "Body"
    TYPE = "Type"
    PARENTS = "Parents"
    FILTER = "Filter"


def get_notion_field(
        notion_page: Dict[str, Any],
        field_type: NotionFieldType,
) -> Union[str, List[str]]:
    """
    Gets the value of a field from a Notion page.

    :param notion_page: The Notion database row page.
    :param field_type: The field type.
    :return: The field value.
    """
    try:
        if field_type == NotionFieldType.NAME:
            return notion_page["properties"]["Name"]["title"][0]["text"]["content"]
        elif field_type == NotionFieldType.BODY:
            return StringExporter(block_id=notion_page["id"]).export()
        elif field_type == NotionFieldType.TYPE:
            return notion_page["properties"][field_id_type]["select"]["name"]
        elif field_type == NotionFieldType.PARENTS:
            return [parent["id"] for parent in notion_page["properties"][field_id_parents]["relation"]]
        elif field_type == NotionFieldType.FILTER:
            return notion_page["properties"][field_id_filter]["select"]["name"]
    except IndexError:
        return ""
    except KeyError:
        return ""


def notion_table_row_to_parent_artifacts(
        notion_page: Dict[str, Any],
        artifact_id_to_name: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Converts a Notion database row into its parent artifacts.

    :param notion_page: The Notion database row page.
    :param artifact_id_to_name: A dictionary of artifact ids to artifact names.
    :return: The trace links from this requirement to its parents.
    """
    source_name = get_notion_field(notion_page, NotionFieldType.NAME)
    parent_ids = get_notion_field(notion_page, NotionFieldType.PARENTS)
    existing_ids = [parent_id for parent_id in parent_ids if parent_id in artifact_id_to_name.keys()]

    return [
            {
                "id": None,
                "traceLinkId": None,
                "traceType": "MANUAL",
                "approvalStatus": "APPROVED",
                "score": 1,
                "sourceId": None,
                "sourceName": source_name,
                "targetId": None,
                "targetName": artifact_id_to_name[parent_id],
            } for parent_id in existing_ids
        ]


def notion_table_row_to_artifact(
        notion_page: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Converts a Notion database row into an artifact.

    :param notion_page: The Notion database row page.
    :return: The artifact created from the requirement.
    """
    return {
            "id": None,
            "name": get_notion_field(notion_page, NotionFieldType.NAME),
            "body": get_notion_field(notion_page, NotionFieldType.BODY),
            "type": get_notion_field(notion_page, NotionFieldType.TYPE) or "Notion Requirement",
            "summary": "",
            "logicType": None,
            "safetyCaseType": None,
            "documentType": "ARTIFACT_TREE",
            "attributes": {},
            "documentIds": []
        }


def notion_table_to_artifacts(db_data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Converts a Notion database into a list of artifacts.

    :param db_data: The requirement database data.
    :return: The artifacts created from requirements.
    """
    artifacts = []
    traces = []
    artifact_id_to_name = {}

    for notion_page in db_data:
        page_filter = get_notion_field(notion_page, NotionFieldType.FILTER)

        if len(field_value_filter) > 0 and page_filter not in field_value_filter:
            continue

        # Convert the notion page to a SAFA artifact, and store the artifact id to name mapping.
        artifact = notion_table_row_to_artifact(notion_page)

        artifacts.append(artifact)
        artifact_id_to_name[notion_page["id"]] = artifact["name"]

        print(f"Added artifact: {artifact['name']}")

    if field_id_parents != "":
        for notion_page in db_data:
            page_name = get_notion_field(notion_page, NotionFieldType.NAME)
            traces = notion_table_row_to_parent_artifacts(notion_page, artifact_id_to_name)

            # Convert the notion page to a SAFA trace link.
            traces.extend(traces)

            print(f"Added {len(traces)} traces: {page_name}")

    return artifacts, traces


def notion_store_table() -> None:
    """
    Stores the given data in a local formatted JSON file.
    """
    print("Downloading Notion Requirement Data...")

    rows = notion.get_db(table_id)
    artifacts, traces = notion_table_to_artifacts(rows)

    print("Storing Notion Requirement Data...")
    print(f"- Artifacts: {len(artifacts)}")
    print(f"- Traces: {len(traces)}")

    notion.save_local({"artifacts": artifacts}, f"Notion Requirement")
    notion.save_local({"traces": traces}, f"Notion Requirement2Notion Requirement")
