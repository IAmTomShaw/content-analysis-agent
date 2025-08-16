import requests
from typing import Optional, Union
from agents import AgentOutputSchema
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Literal
import json

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")

class NotionBlock(BaseModel):
  type: Literal["paragraph", "heading1", "heading_2", "numbered_list_item"]
  text: str

def notion_get_video_properties(notion_id: str):

  api_url = f"https://api.notion.com/v1/pages/{notion_id}"

  request = requests.get(api_url, headers={
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-02-22"
  })

  if request.status_code != 200:
    print("Failed to retrieve video properties.")
    return {}

  data = request.json()

  print("Notion API Response:", json.dumps(data, indent=2))

  props = data.get("properties", {})

  print("Props:", json.dumps(props, indent=2))

  def get_rich_text(prop):
    val = props.get(prop, {}).get("rich_text", [])
    return val[0]["plain_text"] if val else ""

  def get_title(prop):
    val = props.get(prop, {}).get("title", [])
    return val[0]["plain_text"] if val else ""

  def get_multi_select(prop):
    val = props.get(prop, {}).get("multi_select", [])
    return [item["name"] for item in val]

  def get_number(prop):
    return props.get(prop, {}).get("number", None)

  return {
    "title": get_title("Video Title"),
    "description": get_rich_text("Description"),
    "descriptors": get_multi_select("Descriptors"),
    "hypothesis": get_rich_text("Hypothesis"),
    "video_id": get_rich_text("YouTube ID"),
    "score": get_number("Score"),
    "script": get_rich_text("Script"),
  }


def convert_json_to_notion_blocks(content_blocks: list[NotionBlock]) -> list[dict]:

  notion_blocks = []

  for item in content_blocks.blocks:

    if item.type == "paragraph":
      notion_blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [{"type": "text", "text": {"content": item.text}}]
        }
      })
    elif item.type == "heading_1":
      notion_blocks.append({
        "object": "block",
        "type": "heading_1",
        "heading_1": {
          "rich_text": [{"type": "text", "text": {"content": item.text}}]
        }
      })
    elif item.type == "heading_2":
      notion_blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
          "rich_text": [{"type": "text", "text": {"content": item.text}}]
        }
      })
    elif item.type == "heading_3":
      notion_blocks.append({
        "object": "block",
        "type": "heading_3",
        "heading_3": {
          "rich_text": [{"type": "text", "text": {"content": item.text}}]
        }
      })

  return notion_blocks

def notion_send_report(parent_id: str, content_blocks: dict):

  notion_blocks = convert_json_to_notion_blocks(content_blocks)

  headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
  }

  # Get existing blocks from the page
  page_url = f"https://api.notion.com/v1/blocks/{parent_id}/children"
  
  # Append new blocks to the existing page
  data = {
    "children": notion_blocks
  }

  response = requests.patch(page_url, headers=headers, json=data)

  if response.status_code == 200:
    print("Report added to Notion successfully.")
    return True
  else:
    print("Failed to add report to Notion.")
    print("Response:", response.json())
    return False
  
def notion_update_hypothesis_result(notion_id: str, hypothesis_result: str):
  api_url = f"https://api.notion.com/v1/pages/{notion_id}"

  headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
  }

  data = {
    "properties": {
      "Hypothesis Result": {
        "select": {
          "name": hypothesis_result
        }
      }
    }
  }

  response = requests.patch(api_url, headers=headers, json=data)

  if response.status_code == 200:
    print("Hypothesis result updated successfully.")
    return True
  else:
    print("Failed to update hypothesis result.")
    print("Response:", response.json())
    return False