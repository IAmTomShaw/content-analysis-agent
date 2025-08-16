from src.yt import get_all_video_stats, get_video_metadata
from src.notion import notion_get_video_properties, notion_send_report, notion_update_hypothesis_result
from src.db import store_video_stats, get_video_stats, get_video_baseline
from src.comparison import compare_to_baseline
from src.openai import run_evaluation_agent, run_report_agent, run_text_to_json_agent
import asyncio

async def main(notion_id: str, period: str):
  
  # get the video (manual for now)

  properties = notion_get_video_properties(notion_id)

  print('properties:', properties)

  video_id = properties.get("video_id")

  print('video_id:', video_id)

  video_metadata = get_video_metadata(video_id)

  print("Video Metadata:")
  for key, value in video_metadata.items():
    print(f"  {key}: {value}")

  video_stats = get_all_video_stats(video_id)

  print("\nVideo Stats:")
  for key, value in video_stats.items():
    print(f"  {key}: {value}")

  # Save metrics in database

  store_video_stats(video_id, video_metadata.get("publishedAt"), period, {
    f"views_{period}": video_stats.get("views"),
    f"likes_{period}": video_stats.get("likes"),
    f"comments_{period}": video_stats.get("comments"),
    f"average_view_duration_{period}": video_stats.get("averageViewDuration"),
    f"average_percentage_viewed_{period}": video_stats.get("averageViewPercentage"),
    f"subs_gained_{period}": video_stats.get("subscribersGained"),
  })

  video_stats_db = get_video_stats(video_id)

  print("\nVideo Stats from DB:")
  for key, value in video_stats_db.items():
    print(f"  {key}: {value}")

  baseline_metrics = get_video_baseline(5)

  print("\nBaseline Metrics:")
  for key, value in baseline_metrics.items():
    print(f"  {key}: {value}")

  baseline_comparison = compare_to_baseline(video_stats_db, baseline_metrics)

  print("\nBaseline Comparison:")
  for key, value in baseline_comparison.items():
    print(f"  {key}: {value}")

  print('Descriptors:')
  for descriptor in properties.get('descriptors', []):
    print(f"  - {descriptor}")

  eval_agent_res = await run_evaluation_agent(period, video_stats_db, baseline_metrics, properties.get('descriptors'), properties.get('script', ''), [])

  eval_res = eval_agent_res.evaluation

  hypothesis_result = eval_agent_res.hypothesis_result

  report_res = await run_report_agent(eval_res)

  # Text to json writer

  json_res = await run_text_to_json_agent(report_res)

  # Send the report to notion

  notion_send_report(notion_id, json_res) 

  # Update the Notion page with the hypothesis result

  notion_update_hypothesis_result(notion_id, hypothesis_result)