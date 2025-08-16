from src.yt import get_all_video_stats, get_video_metadata
import argparse

from src.db import store_video_stats

def refresh_video_stats(video_id: str):

  video_metadata = get_video_metadata(video_id)

  twenty_four_hour_stats = get_all_video_stats(video_id, video_metadata.get("publishedAt"), "24hr")
  forty_eight_hour_stats = get_all_video_stats(video_id, video_metadata.get("publishedAt"), "48hr")
  seven_day_stats = get_all_video_stats(video_id, video_metadata.get("publishedAt"), "7d")


  # Save metrics in database
  store_video_stats(video_id, video_metadata.get("publishedAt"), "24hr", {
    f"views_24hr": twenty_four_hour_stats.get("views"),
    f"likes_24hr": twenty_four_hour_stats.get("likes"),
    f"comments_24hr": twenty_four_hour_stats.get("comments"),
    f"average_view_duration_24hr": twenty_four_hour_stats.get("averageViewDuration"),
    f"average_percentage_viewed_24hr": twenty_four_hour_stats.get("averageViewPercentage"),
    f"subs_gained_24hr": twenty_four_hour_stats.get("subscribersGained"),
  })

  store_video_stats(video_id, video_metadata.get("publishedAt"), "48hr", {
    f"views_48hr": forty_eight_hour_stats.get("views"),
    f"likes_48hr": forty_eight_hour_stats.get("likes"),
    f"comments_48hr": forty_eight_hour_stats.get("comments"),
    f"average_view_duration_48hr": forty_eight_hour_stats.get("averageViewDuration"),
    f"average_percentage_viewed_48hr": forty_eight_hour_stats.get("averageViewPercentage"),
    f"subs_gained_48hr": forty_eight_hour_stats.get("subscribersGained"),
  })

  store_video_stats(video_id, video_metadata.get("publishedAt"), "7d", {
    f"views_7d": seven_day_stats.get("views"),
    f"likes_7d": seven_day_stats.get("likes"),
    f"comments_7d": seven_day_stats.get("comments"),
    f"average_view_duration_7d": seven_day_stats.get("averageViewDuration"),
    f"average_percentage_viewed_7d": seven_day_stats.get("averageViewPercentage"),
    f"subs_gained_7d": seven_day_stats.get("subscribersGained"),
  })

  print("Stats refreshed: ")

def main():
  parser = argparse.ArgumentParser(description="Refresh YouTube video stats.")
  parser.add_argument("--video-id", type=str, required=True, help="YouTube video ID")
  args = parser.parse_args()

  refresh_video_stats(args.video_id)

if __name__ == "__main__":
  main()