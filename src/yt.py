import os
from datetime import date, timedelta
from dateutil import tz
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

from dotenv import load_dotenv

load_dotenv()

# get_refresh_token.py
import json, os, webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from datetime import datetime, timedelta

GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]

def auth():
    # Put your client id/secret here or read from env
    client_id = os.getenv("GOOGLE_CLIENT_ID") or input("Client ID: ").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET") or input("Client Secret: ").strip()

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(open_browser=True, port=0)  # opens browser, handles redirect to localhost
    # Force a refresh to guarantee a refresh_token is present
    creds.refresh(Request())

    print("\n✅ Success!")
    print("Access Token:", creds.token)
    print("Refresh Token:", creds.refresh_token)
    print("\nSave these as environment variables:")
    print("GOOGLE_CLIENT_ID=", client_id)
    print("GOOGLE_CLIENT_SECRET=", client_secret)
    print("GOOGLE_REFRESH_TOKEN=", creds.refresh_token)


def make_credentials():
    """
    Returns a Credentials object using environment variables.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    token_uri = "https://oauth2.googleapis.com/token"

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds

def get_video_metadata(video_id: str):
    """
    Returns metadata for a video: title, length, description, publish date, etc.
    """
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,contentDetails",
        "id": video_id,
        "key": GOOGLE_CLOUD_API_KEY
    }
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    item = (data.get("items") or [None])[0]
    if not item:
        return {}

    snippet = item.get("snippet", {})
    content_details = item.get("contentDetails", {})
    return {
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "publishedAt": snippet.get("publishedAt"),
        "duration": content_details.get("duration"),  # ISO 8601 format, e.g. 'PT5M33S'
        "channelTitle": snippet.get("channelTitle"),
        "thumbnails": snippet.get("thumbnails"),
    }

def get_all_video_stats(video_id: str, published_date: str = None, period: str = None):
    start_date = "2006-01-01"
    end_date = date.today().isoformat()

    if published_date and period:
        # Ensure published_date is in YYYY-MM-DD format
        dt = datetime.fromisoformat(published_date)
        start_date = dt.date().isoformat()
        if period == "24hr":
            end_dt = dt + timedelta(hours=24)
        elif period == "48hr":
            end_dt = dt + timedelta(hours=48)
        elif period == "7d":
            end_dt = dt + timedelta(days=7)
        else:
            end_dt = date.today()
        end_date = end_dt.date().isoformat()

        # If the video is not old enough for the entire period to have elapsed, then do not return stats

        if end_date > date.today().isoformat():
            return {}

    """
    Returns all available stats for a video from its publish date to today.
    """
    ya = build("youtubeAnalytics", "v2", credentials=make_credentials(), cache_discovery=False)
    metrics = ",".join([
        "views",
        "averageViewDuration",
        "averageViewPercentage",
        "estimatedMinutesWatched",
        "likes",
        "comments",
        "subscribersGained",
        "subscribersLost"
    ])
    try:
        resp = ya.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics=metrics,
            dimensions="video",
            filters=f"video=={video_id}",
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"YouTube Analytics API error ({e.resp.status}): {e}") from e

    rows = resp.get("rows", [])
    headers = [h["name"] for h in resp.get("columnHeaders", [])]
    stats = dict(zip(headers, rows[0])) if rows else {}

    return stats