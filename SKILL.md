---
name: xfactor
description: "Use when the user wants to grow their X account with AI-powered content, engagement, and analytics. Full X growth engine: research-first posting, automated likes/follows, and live dashboard."
version: 2.0.0
author: Hamzaa Shergill
license: MIT
platforms: [macos, linux]
prerequisites:
  commands: [xurl]
metadata:
  hermes:
    tags: [x, twitter, growth, automation, social-media, analytics]
    related_skills: [xurl]
    config:
      - key: xfactor.handle
        description: Your X handle (without @)
        default: ""
        prompt: Enter your X handle (e.g., generalizingai)
      - key: xfactor.posts_per_day
        description: Number of posts per day
        default: "3"
        prompt: How many posts per day? (2-4)
      - key: xfactor.timezone
        description: Your timezone for posting schedule
        default: "Asia/Karachi"
        prompt: Your timezone (e.g., Asia/Karachi, America/New_York, Europe/London)
      - key: xfactor.dashboard_port
        description: Local port for the dashboard
        default: "3000"
        prompt: Dashboard port number
required_environment_variables:
  - name: X_CLIENT_ID
    prompt: X API OAuth 2.0 Client ID
    help: Get from https://developer.x.com/en/portal/dashboard
    required_for: X API authentication
  - name: X_CLIENT_SECRET
    prompt: X API OAuth 2.0 Client Secret
    help: Get from https://developer.x.com/en/portal/dashboard
    required_for: X API authentication
  - name: X_HANDLE
    prompt: Your X handle (username only, no @)
    help: e.g., generalizingai
    required_for: Account identification
required_credential_files:
  - path: ~/.xurl
    description: X API OAuth token file (created by xurl auth oauth2)
---

# XFactor - X Growth Engine

<p align="center">
  <img src="dashboard/xfactor-logo.png" alt="XFactor Logo" width="400">
</p>

XFactor is a complete autonomous X (Twitter) growth engine. It posts research-driven content, engages with your niche, and provides a live analytics dashboard - all automated through Hermes Agent.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      XFactor Engine                         │
├─────────────────┬───────────────────┬───────────────────────┤
│  Content (3x)   │  Engagement (1x)  │  Analytics (every 30m)│
├─────────────────┼───────────────────┼───────────────────────┤
│ 8AM Research X  │ Like 20-30 posts  │ Fetch followers       │
│   → Write thread│ Reply to mentions │ Track post metrics    │
│ 10AM Research X │ Reply in threads  │ Log engagement        │
│   → Write post  │ Follow 5 max/day  │ Update dashboard      │
│ 6PM Research X  │ (productive only) │                       │
│   → Write post  │                   │                       │
└─────────────────┴───────────────────┴───────────────────────┘
```

## Installation

### One-Command Install
```bash
curl -fsSL https://raw.githubusercontent.com/hamzaashergill/xfactor/main/setup.sh | bash
```

### Via Hermes Skill Tap
```bash
hermes skills tap add hamzaashergill/xfactor
hermes skills install xfactor
```

### Manual Setup

1. **Install xurl:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/xdevplatform/xurl/main/install.sh | bash
   ```

2. **Set up X API auth:**
   ```bash
   xurl auth apps add xfactor --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
   xurl auth oauth2 --app xfactor YOUR_HANDLE
   xurl auth default xfactor
   ```

3. **Install skill files into:**
   ```
   ~/.hermes/skills/social-media/xfactor/
   ├── SKILL.md
   └── scripts/
       ├── x-daily-poster.py
       ├── x-engagement.py
       └── x-dashboard-collector.py
   ```

4. **Dashboard:**
   ```
   ~/.hermes/x-dashboard/index.html
   ```

## Configuration

### X API Authentication

XFactor uses the official X API via the `xurl` CLI. You need:

1. **X Developer Account**: https://developer.x.com/en/portal/dashboard
2. **OAuth 2.0 credentials**: Client ID + Client Secret
3. **App setup**: Callback URI = `http://localhost:8080/callback`, app type = "Web App, Automated App or Bot"

Complete auth:
```bash
xurl auth apps add xfactor --client-id YOUR_ID --client-secret YOUR_SECRET
xurl auth oauth2 --app xfactor YOUR_HANDLE
xurl auth default xfactor
xurl whoami  # Verify
```

### Content Customization

Edit `~/.hermes/skills/social-media/xfactor/scripts/x-daily-poster.py`:

| Section | What to Change |
|---------|---------------|
| `SEARCH_QUERIES` | Topics to research before posting (line ~70) |
| Thread content | The 6 blocks in `generate_morning_thread()` |
| Single posts | The lists in `generate_single_post()` and `generate_evening_post()` |
| Reply templates | The `REPLIES` list in engagement script |
| Target accounts | The `PRODUCTIVE_ACCOUNTS` list for likes/follows |

### Cron Job Setup

Create these cron jobs in Hermes:

```yaml
# Morning thread (8 AM your time)
schedule: "0 8 * * *"
script: x-daily-poster.py morning

# Afternoon post (10 AM - 2h gap)
schedule: "0 10 * * *"
script: x-daily-poster.py afternoon

# Engagement run (2 PM)
schedule: "0 14 * * *"
script: x-engagement.py

# Evening post (6 PM)
schedule: "0 18 * * *"
script: x-daily-poster.py evening

# Dashboard refresh (every 30 min)
schedule: "*/30 * * * *"
script: x-dashboard-collector.py
```

## Usage

### Starting the Dashboard
```bash
cd ~/.hermes/x-dashboard && python3 -m http.server 3000
```
Then open **http://localhost:3000**

### Manual Posting
```bash
# Post a research-driven thread
python3 ~/.hermes/scripts/x-daily-poster.py morning

# Post a single value-add post
python3 ~/.hermes/scripts/x-daily-poster.py afternoon

# Post an evening hot take
python3 ~/.hermes/scripts/x-daily-poster.py evening
```

### Manual Engagement Run
```bash
python3 ~/.hermes/scripts/x-engagement.py
```

### Check Dashboard Data
```bash
python3 ~/.hermes/scripts/x-dashboard-collector.py
```

## What XFactor Does Well

| Feature | Status | Detail |
|---------|--------|--------|
| Research-driven posting | ✅ | Searches X for trending topics before writing |
| 3 posts/day | ✅ | Thread (8AM) + Single (10AM) + Evening (6PM) |
| Auto likes (20-30/run) | ✅ | Likes from curated productive accounts |
| Selective follows (max 5) | ✅ | Only real AI/tech builders |
| Reply to mentions | ✅ | Every mention gets a thoughtful response |
| Reply in threads | ✅ | Every thread reply gets a response |
| Live analytics dashboard | ✅ | 5 views: Dashboard, Analytics, Content, Schedule, Engagement |
| Post history tracking | ✅ | View Post links on every post |
| Follower growth chart | ✅ | Live-updating chart |
| Posting heatmap | ✅ | 28-day activity heatmap |
| Scheduling overview | ✅ | Shows all cron jobs and timings |

## Limitations (X API Restrictions)

| Feature | Status | Why |
|---------|--------|-----|
| Reply to strangers | ❌ | X API blocks replying to accounts that haven't engaged with you |
| Quote-post strangers | ❌ | Same X API restriction |
| Auto-DM new followers | ❌ | X API requires opt-in for DMs |

## Architecture

```
xurl CLI (X API) ←→ Hermes Agent ←→ Scripts ←→ Dashboard
                      ↕
                 Cron Jobs (schedule)
```

- **xurl**: Official X CLI for API calls (post, reply, like, follow, search)
- **Hermes Agent**: Runs scripts, manages cron, loads skill
- **Scripts**: Python that orchestrates research → generate → post cycle
- **Dashboard**: Static HTML/JS served locally, fetches JSON data files

## Customization for Your Niche

XFactor is niche-agnostic. To adapt for a different niche:

1. **Change search queries** in `x-daily-poster.py`:
   ```python
   SEARCH_QUERIES = ["your niche topic 1", "topic 2", "topic 3"]
   ```

2. **Change target accounts** in `x-engagement.py`:
   ```python
   PRODUCTIVE_ACCOUNTS = ["handle1", "handle2", "handle3"]
   ```

3. **Rewrite thread content** in `generate_morning_thread()` for your niche's pain points

4. **Adjust posting times** via cron jobs to match your audience's active hours

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `xurl: command not found` | Add `~/.local/bin` to PATH or reinstall xurl |
| OAuth errors | Re-run `xurl auth oauth2 --app xfactor YOUR_HANDLE` |
| Dashboard shows "No data" | Run `python3 ~/.hermes/scripts/x-dashboard-collector.py` |
| Scripts fail in cron | Scripts auto-set PATH to include `~/.local/bin` |
| Rate limited | X API free tier has limits; wait 15 min between runs |
| Posts not appearing | Check `~/.hermes/x-posts.log` for errors |

## Files Reference

| File | Purpose |
|------|---------|
| `~/.hermes/skills/social-media/xfactor/SKILL.md` | This skill definition |
| `~/.hermes/skills/social-media/xfactor/scripts/x-daily-poster.py` | Research + post (morning/afternoon/evening) |
| `~/.hermes/skills/social-media/xfactor/scripts/x-engagement.py` | Likes, follows, mention replies |
| `~/.hermes/skills/social-media/xfactor/scripts/x-dashboard-collector.py` | Data fetcher for dashboard |
| `~/.hermes/x-dashboard/index.html` | XFactor analytics dashboard |
| `~/.hermes/x-posts.log` | Log of all posts |
| `~/.hermes/x-engagement.log` | Log of all engagement actions |
| `~/.hermes/x-research.log` | Log of research findings |
| `~/.hermes/x-dashboard/*.json` | Dashboard data files |
| `~/.xurl` | X API credentials (DO NOT SHARE) |

## Updates

To update XFactor:
```bash
curl -fsSL https://raw.githubusercontent.com/hamzaashergill/xfactor/main/setup.sh | bash
```
Or via Hermes tap:
```bash
hermes skills tap sync hamzaashergill/xfactor
hermes skills install xfactor --force
