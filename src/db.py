import sqlite3

DB_PATH = "video_stats.db"

def init_db():
    """Initializes the SQLite database and creates the video_stats table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS video_stats (
        video_id TEXT PRIMARY KEY,
        title TEXT,
        publish_date TEXT,
        views_24hr INTEGER DEFAULT NULL,
        views_48hr INTEGER DEFAULT NULL,
        views_7d INTEGER DEFAULT NULL,
        likes_24hr INTEGER DEFAULT NULL,
        likes_48hr INTEGER DEFAULT NULL,
        likes_7d INTEGER DEFAULT NULL,
        ctr_24hr REAL DEFAULT NULL,
        ctr_48hr REAL DEFAULT NULL,
        ctr_7d REAL DEFAULT NULL,
        average_view_duration_24hr REAL DEFAULT NULL,
        average_view_duration_48hr REAL DEFAULT NULL,
        average_view_duration_7d REAL DEFAULT NULL,
        average_percentage_viewed_24hr REAL DEFAULT NULL,
        average_percentage_viewed_48hr REAL DEFAULT NULL,
        average_percentage_viewed_7d REAL DEFAULT NULL,
        comments_24hr INTEGER DEFAULT NULL,
        comments_48hr INTEGER DEFAULT NULL,
        comments_7d INTEGER DEFAULT NULL,
        subs_gained_24hr INTEGER DEFAULT NULL,
        subs_gained_48hr INTEGER DEFAULT NULL,
        subs_gained_7d INTEGER DEFAULT NULL
      )
    """)
    conn.commit()
    conn.close()

def get_video_stats(video_id):
    """Returns stats for a specific video."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM video_stats WHERE video_id = ?", (video_id,))
    row = c.fetchone()
    conn.close()
    if row:
        keys = [
            "video_id", "title", "publish_date",
            "views_24hr", "views_48hr", "views_7d",
            "likes_24hr", "likes_48hr", "likes_7d",
            "ctr_24hr", "ctr_48hr", "ctr_7d",
            "average_view_duration_24hr", "average_view_duration_48hr", "average_view_duration_7d",
            "average_percentage_viewed_24hr", "average_percentage_viewed_48hr", "average_percentage_viewed_7d",
            "comments_24hr", "comments_48hr", "comments_7d",
            "subs_gained_24hr", "subs_gained_48hr", "subs_gained_7d"
        ]
        return dict(zip(keys, row))
    return None

def get_video_baseline(n=5):
    """Returns baseline metrics for the past n videos."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT
            views_24hr, views_48hr, views_7d,
            likes_24hr, likes_48hr, likes_7d,
            ctr_24hr, ctr_48hr, ctr_7d,
            average_view_duration_24hr, average_view_duration_48hr, average_view_duration_7d,
            average_percentage_viewed_24hr, average_percentage_viewed_48hr, average_percentage_viewed_7d,
            comments_24hr, comments_48hr, comments_7d,
            subs_gained_24hr, subs_gained_48hr, subs_gained_7d
        FROM video_stats
        ORDER BY publish_date DESC
        LIMIT ?
    """, (n,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return {k: 0 for k in [
            "views_24hr", "views_48hr", "views_7d",
            "likes_24hr", "likes_48hr", "likes_7d",
            "ctr_24hr", "ctr_48hr", "ctr_7d",
            "average_view_duration_24hr", "average_view_duration_48hr", "average_view_duration_7d",
            "average_percentage_viewed_24hr", "average_percentage_viewed_48hr", "average_percentage_viewed_7d",
            "comments_24hr", "comments_48hr", "comments_7d",
            "subs_gained_24hr", "subs_gained_48hr", "subs_gained_7d"
        ]}
    cols = list(zip(*rows))
    keys = [
        "views_24hr", "views_48hr", "views_7d",
        "likes_24hr", "likes_48hr", "likes_7d",
        "ctr_24hr", "ctr_48hr", "ctr_7d",
        "average_view_duration_24hr", "average_view_duration_48hr", "average_view_duration_7d",
        "average_percentage_viewed_24hr", "average_percentage_viewed_48hr", "average_percentage_viewed_7d",
        "comments_24hr", "comments_48hr", "comments_7d",
        "subs_gained_24hr", "subs_gained_48hr", "subs_gained_7d"
    ]
    def safe_avg(col):
        filtered = [v for v in col if v is not None]
        return float(sum(filtered) / len(filtered)) if filtered else 0
    return {k: safe_avg(col) for k, col in zip(keys, cols)}

def store_video_stats(video_id, publish_date, period, stats):
    if period not in ["24hr", "48hr", "7d"]:
        raise ValueError("Invalid period. Must be one of: 24hr, 48hr, 7d.")

    # Filter stats for the correct period
    filtered_stats = {k: v for k, v in stats.items() if k.endswith(f"_{period}")}
    filtered_stats["publish_date"] = publish_date

    print("Filtered Stats:", filtered_stats)

    if not filtered_stats:
        # Nothing to update/insert
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if video exists
    c.execute("SELECT video_id FROM video_stats WHERE video_id = ?", (video_id,))
    exists = c.fetchone()

    if exists:
        # Update only the provided stats
        set_clauses = []
        values = []
        for key, value in filtered_stats.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        values.append(video_id)
        query = f"UPDATE video_stats SET {', '.join(set_clauses)} WHERE video_id = ?"
        c.execute(query, values)
    else:
        # Insert new record with provided stats
        columns = ["video_id"] + list(filtered_stats.keys())
        placeholders = "?" + ", ?" * len(filtered_stats)
        values = [video_id] + list(filtered_stats.values())
        query = f"INSERT INTO video_stats ({', '.join(columns)}) VALUES ({placeholders})"
        c.execute(query, values)

    conn.commit()
    conn.close()

# Initialize the database when the module is imported
init_db()
