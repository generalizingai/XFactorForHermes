#!/usr/bin/env python3
"""X Analytics Dashboard Data Collector for @generalizingai.
Fetches follower count, post metrics, engagement data and saves as JSON for the dashboard."""

import subprocess, json, os, time
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(os.path.expanduser("~/.hermes/x-dashboard"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = DATA_DIR / "history.json"
SNAPSHOT_FILE = DATA_DIR / "snapshot.json"
POSTS_FILE = DATA_DIR / "posts.json"
ENGAGEMENT_FILE = DATA_DIR / "engagement.json"
CONTENT_FILE = DATA_DIR / "content.json"
ERROR_LOG = DATA_DIR / "errors.log"

USER_ID = "1925525910067073024"
USERNAME = "generalizingai"

def log_error(msg):
    with open(ERROR_LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def run(cmd):
    try:
        # xurl is at ~/.local/bin/xurl, ensure PATH includes it
        env = os.environ.copy()
        env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:/usr/local/bin:/usr/bin:/bin:{env.get('PATH', '')}"
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
        if r.returncode != 0:
            log_error(f"CMD FAILED: {' '.join(cmd)} -> {r.stderr[:200]}")
            return None
        return json.loads(r.stdout) if r.stdout.strip() else None
    except Exception as e:
        log_error(f"EXCEPTION: {' '.join(cmd)} -> {e}")
        return None

def fetch_profile():
    """Fetch follower count and profile metrics."""
    data = run(["xurl", "whoami"])
    if data and "data" in data:
        m = data["data"]["public_metrics"]
        return {
            "followers": m["followers_count"],
            "following": m["following_count"],
            "posts": m["tweet_count"],
            "likes": m["like_count"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    return None

def fetch_recent_posts(limit=20):
    """Fetch recent original posts with engagement metrics (excludes replies)."""
    data = run(["xurl", f"/2/users/{USER_ID}/tweets?max_results={limit}&tweet.fields=public_metrics,created_at,attachments&exclude=replies"])
    if data and "data" in data:
        posts = []
        for t in data["data"]:
            text = t.get("text", "")
            # Skip replies (dont show on dashboard, already on profile)
            if text.startswith("@"):
                continue
            m = t.get("public_metrics", {})
            posts.append({
                "id": t["id"],
                "text": t.get("text", "")[:280],
                "created_at": t.get("created_at", ""),
                "likes": m.get("like_count", 0),
                "retweets": m.get("retweet_count", 0),
                "replies": m.get("reply_count", 0),
                "quotes": m.get("quote_count", 0),
                "bookmarks": m.get("bookmark_count", 0),
                "impressions": m.get("impression_count", 0),
                "engagement_score": m.get("like_count", 0) + m.get("retweet_count", 0) * 3 +
                                    m.get("reply_count", 0) * 2 + m.get("bookmark_count", 0) * 4,
            })
        return posts
    return []

def fetch_mentions(limit=20):
    """Fetch recent mentions and replies."""
    data = run(["xurl", f"/2/users/{USER_ID}/mentions?max_results={limit}&tweet.fields=public_metrics,created_at"])
    if data and "data" in data:
        mentions = []
        for t in data["data"]:
            m = t.get("public_metrics", {})
            mentions.append({
                "id": t["id"],
                "text": t.get("text", "")[:280],
                "created_at": t.get("created_at", ""),
                "likes": m.get("like_count", 0),
                "replies": m.get("reply_count", 0),
            })
        return mentions
    return []

def fetch_engagement_log():
    """Read the engagement log."""
    log_file = os.path.expanduser("~/.hermes/x-engagement.log")
    entries = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            for line in f.readlines()[-50:]:
                line = line.strip()
                if line and ("REPLIED" in line or "LIKED" in line):
                    entries.append(line)
    return entries

def fetch_posts_log():
    """Read the posts log for daily posting history."""
    log_file = os.path.expanduser("~/.hermes/x-posts.log")
    entries = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            for line in f.readlines()[-100:]:
                line = line.strip()
                if line:
                    entries.append(line)
    return entries

def update_history(profile):
    """Append current metrics to history for charting."""
    history = []
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text())
        except:
            history = []
    
    history.append({
        "timestamp": profile["timestamp"],
        "followers": profile["followers"],
        "following": profile["following"],
        "posts": profile["posts"],
    })
    
    # Keep last 90 days
    if len(history) > 90:
        history = history[-90:]
    
    HISTORY_FILE.write_text(json.dumps(history, indent=2))
    return history

def collect_all():
    """Collect all dashboard data."""
    print("Collecting X analytics data...")
    
    # 1. Profile snapshot
    profile = fetch_profile()
    if profile:
        print(f"  Profile: {profile['followers']} followers, {profile['posts']} posts")
    
    # 2. History for charting
    history = update_history(profile) if profile else []
    
    # 3. Recent posts with metrics
    posts = fetch_recent_posts(20)
    print(f"  Posts: {len(posts)} recent posts")
    
    # 4. Mentions
    mentions = fetch_mentions(10)
    print(f"  Mentions: {len(mentions)} recent mentions")
    
    # 5. Engagement log
    engagements = fetch_engagement_log()
    print(f"  Engagements: {len(engagements)} log entries")
    
    # 6. Post log
    post_log = fetch_posts_log()
    
    # 7. Compute totals
    total_likes = sum(p["likes"] for p in posts)
    total_retweets = sum(p["retweets"] for p in posts)
    total_replies = sum(p["replies"] for p in posts)
    total_bookmarks = sum(p["bookmarks"] for p in posts)
    
    # Posting streak (consecutive days with at least one post)
    streak = 0
    if post_log:
        dates = set()
        for entry in post_log:
            if "RUNNING DAILY POST" in entry or "THREAD STARTED" in entry or "THREAD COMPLETE" in entry or "MORNING DONE" in entry:
                date_part = entry[1:11] if entry.startswith("[") else ""
                if date_part:
                    dates.add(date_part)
        # Count consecutive days
        sorted_dates = sorted(dates)
        if sorted_dates:
            streak = 1
            from datetime import date, timedelta
            for i in range(1, len(sorted_dates)):
                d1 = datetime.strptime(sorted_dates[i-1], "%Y-%m-%d").date()
                d2 = datetime.strptime(sorted_dates[i], "%Y-%m-%d").date()
                if (d2 - d1).days == 1:
                    streak += 1
                else:
                    streak = 1
    
    # 8. Save snapshot (preserve previous data on failure)
    # Load previous snapshot as fallback
    prev_snapshot = {}
    if SNAPSHOT_FILE.exists():
        try:
            prev_snapshot = json.loads(SNAPSHOT_FILE.read_text())
        except:
            pass
    
    if not profile and prev_snapshot.get("profile", {}).get("followers", 0) > 0:
        profile = prev_snapshot["profile"]
        print(f"  Using cached profile: {profile['followers']} followers")
    
    if not posts and prev_snapshot.get("totals", {}).get("total_posts_tracked", 0) > 0:
        # Load previous posts
        if POSTS_FILE.exists():
            try:
                posts = json.loads(POSTS_FILE.read_text())
                print(f"  Using cached posts: {len(posts)} posts")
            except:
                pass
    
    snapshot = {
        "profile": profile or {"followers": 0, "following": 0, "posts": 0, "likes": 0},
        "totals": {
            "total_likes": total_likes,
            "total_retweets": total_retweets,
            "total_replies": total_replies,
            "total_bookmarks": total_bookmarks,
            "total_posts_tracked": len(posts),
        },
        "posting_streak": streak,
        "top_post": max(posts, key=lambda p: p["engagement_score"]) if posts else None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2))
    POSTS_FILE.write_text(json.dumps(posts, indent=2))
    ENGAGEMENT_FILE.write_text(json.dumps({
        "mentions": mentions,
        "engagement_log": engagements[-30:] if len(engagements) > 30 else engagements,
        "post_log": post_log[-50:] if len(post_log) > 50 else post_log,
    }, indent=2))
    
    print(f"Dashboard data saved to {DATA_DIR}")
    print(f"  Snapshot: {snapshot['profile']['followers']} followers")
    print(f"  Top post: {snapshot['top_post']['engagement_score'] if snapshot['top_post'] else 0} score")
    print(f"  Streak: {streak} days")

if __name__ == "__main__":
    collect_all()