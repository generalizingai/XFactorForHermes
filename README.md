# XFactor - Autonomous X Growth Engine for Hermes Agent

<p align="center">
  <img src="dashboard/xfactor-logo.png" alt="XFactor Logo" width="400">
</p>

XFactor is a complete, autonomous X (Twitter) growth system built for [Hermes Agent](https://hermes-agent.nousresearch.com). It handles your entire X growth loop - research, content creation, engagement, and analytics - without manual effort.

## 🚀 One-Command Install

```bash
curl -fsSL https://raw.githubusercontent.com/hamzaashergill/xfactor/main/setup.sh | bash
```

Or via Hermes Skill Tap:

```bash
hermes skills tap add hamzaashergill/xfactor
hermes skills install xfactor
```

## What It Does

| Time | Action | Description |
|------|--------|-------------|
| **8:00 AM** | 🧵 Research + Thread | Searches X for trending AI topics, generates a 6-tweet educational thread |
| **10:00 AM** | 💬 Research + Post | Searches X, posts a single value-add insight |
| **2:00 PM** | ❤️ Engagement Run | Likes 20-30 posts, follows 5 productive accounts, replies to mentions |
| **6:00 PM** | 🌙 Research + Evening Post | Searches X, posts a hot take or reflection |
| **Every 30m** | 📊 Dashboard Refresh | Fetches latest follower count, post metrics, engagement data |

## Features

- **Research-first content**: Every post starts with X search to find what's trending in your niche
- **3 posts/day**: Thread + single + evening post with 2-hour gaps
- **Auto engagement**: 20-30 likes per run on curated productive accounts
- **Smart follows**: Max 5/day, only verified AI/tech builders
- **Mention reply automation**: Every mention gets a thoughtful, topic-matched reply
- **Live dashboard**: 5-view analytics at localhost:3000
- **Growth tracking**: Follower chart, posting heatmap, engagement timeline

## Requirements

- **Hermes Agent** (for cron scheduling)
- **X Developer Account** (free tier works)
- **macOS or Linux**
- **xurl CLI** (installed automatically)

## Setup

### 1. Install xurl & Authenticate with X API

```bash
curl -fsSL https://raw.githubusercontent.com/xdevplatform/xurl/main/install.sh | bash

# Register your X API app
xurl auth apps add xfactor --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET

# Authenticate (opens browser)
xurl auth oauth2 --app xfactor YOUR_HANDLE
xurl auth default xfactor

# Verify
xurl whoami
```

> **Need credentials?** Go to https://developer.x.com/en/portal/dashboard → Create an app → OAuth 2.0 → Get Client ID + Client Secret. Set callback URI to `http://localhost:8080/callback`.

### 2. Start the Dashboard

```bash
cd ~/.hermes/x-dashboard && python3 -m http.server 3000
open http://localhost:3000
```

### 3. Set Up Cron Jobs

In Hermes Agent, create these cron jobs:

| Job | Script | Schedule |
|-----|--------|----------|
| Morning Thread | `x-daily-poster.py morning` | `0 8 * * *` |
| Afternoon Post | `x-daily-poster.py afternoon` | `0 10 * * *` |
| Engagement | `x-engagement.py` | `0 14 * * *` |
| Evening Post | `x-daily-poster.py evening` | `0 18 * * *` |
| Dashboard Refresh | `x-dashboard-collector.py` | `*/30 * * * *` |

### 4. Test It

```bash
python3 ~/.hermes/scripts/x-daily-poster.py afternoon
```

## Dashboard

![XFactor Dashboard](https://via.placeholder.com/800x450?text=XFactor+Dashboard)

Open **http://localhost:3000** to see:

- **Dashboard**: KPIs, follower growth chart, top post, post table, activity feed, growth calendar
- **Analytics**: Total likes/RTs/engagement, posting heatmap, engagement breakdown
- **Content**: Tracked posts, lifetime stats, recent content list with View links
- **Schedule**: All cron jobs visualized on cards with descriptions
- **Engagement**: Engagement count, timeline of all likes/follows/replies

## Customizing for Your Niche

Edit these sections in `~/.hermes/skills/social-media/xfactor/scripts/`:

### Change search queries (what topics to research)

In `x-daily-poster.py`:
```python
SEARCH_QUERIES = ["your niche topic", "related topic", "another topic"]
```

### Change who to like/follow

In `x-engagement.py`:
```python
PRODUCTIVE_ACCOUNTS = ["influencer1", "builder2", "expert3"]
```

### Change content

In `x-daily-poster.py`, the content generation functions:
- `generate_morning_thread()` - 6-tweet threads
- `generate_single_post()` - afternoon singles
- `generate_evening_post()` - evening posts
- `VALUABLE_REPLIES` in `x-engagement.py` - reply templates

### Change posting times

Adjust cron job schedules in Hermes to match your audience's timezone.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      XFactor Engine                         │
├─────────────────┬───────────────────┬───────────────────────┤
│  Content (3x)   │  Engagement (1x)  │  Analytics (30min)   │
├─────────────────┼───────────────────┼───────────────────────┤
│ xurl search      │ xurl like        │ xurl whoami           │
│ xurl post        │ xurl follow      │ xurl user timeline    │
│ xurl reply       │ xurl reply       │ xurl mentions         │
└─────────────────┴───────────────────┴───────────────────────┘
         ↕                    ↕                    ↕
    ┌──────────────────────────────────────────────────────┐
    │              Hermes Agent (cron jobs)                │
    └──────────────────────────────────────────────────────┘
```

## File Structure

```
~/.hermes/
├── skills/social-media/xfactor/
│   ├── SKILL.md
│   └── scripts/
│       ├── x-daily-poster.py          # Research + post (3 modes)
│       ├── x-engagement.py            # Likes, follows, replies
│       └── x-dashboard-collector.py   # Data fetcher
├── x-dashboard/
│   └── index.html                     # Analytics dashboard
├── scripts/                           # Symlinked for cron
│   ├── x-daily-poster.py -> ..
│   ├── x-engagement.py -> ..
│   └── x-dashboard-collector.py -> ..
├── x-posts.log                        # Post history
├── x-engagement.log                   # Engagement history
└── x-research.log                     # Research findings
```

## X API Limitations

| ✅ Works | ❌ Blocked |
|----------|-----------|
| Post original content | Reply to strangers |
| Reply to mentions | Quote-post strangers |
| Reply in your threads | |
| Like any post | |
| Follow any account | |
| Search & research | |

## License

MIT - use freely, modify, share.

## Built With

- [xurl](https://github.com/xdevplatform/xurl) - Official X API CLI
- [Hermes Agent](https://hermes-agent.nousresearch.com) - AI Agent framework
- Python 3 - Scripting
- Vanilla HTML/CSS/JS - Dashboard