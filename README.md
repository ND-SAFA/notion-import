# Notion Import

A script for converting Notion pages into SAFA project files.

## Getting Started

This integration will convert all tables within a Notion database
to SAFA artifacts. The page title will be used as the artifact name,
and page content will be loaded as the body of the artifact.

### Installing

1. Create `.env` file containing the following.

```
# Required
NOTION_TOKEN=[TOKEN]
NOTION_TABLE_ID=[TABLE_ID]

# Optional
NOTION_FIELD_ID_TYPE=[FIELD_ID_TYPE]          # Assumes a select field
NOTION_FIELD_ID_PARENTS=[FIELD_ID_PARENTS]    # Assumes a relation field


NOTION_FIELD_ID_FILTER=[FIELD_ID_FILTER]      # Assumes a select field
NOTION_FIELD_VALUE_FILTER=[FILTER_VALUE_A,FILTER_VALUE_B]
```

2. Create virtual environment and download requirements.

```
$ python3 -m venv venv
$ source venv/bin/activate
```

3. Download requirements.

```
$ pip3 install -r requirements.txt
```

### Running

To create a JSON file from your Notion database, run the following commands. 
This could take a few minutes depending on the size of the database.

```
$ source venv/bin/activate
$ python3 src/runner.py
```
