# XFactor — One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/hamzaashergill/xfactor/main/setup.sh | bash
```

Or via Hermes Skill Tap:
```bash
hermes skills tap add hamzaashergill/xfactor
hermes skills install xfactor
```

## What You Get

After install, this is your setup:

```
~/.hermes/skills/social-media/xfactor/        ← Skill files
~/.hermes/x-dashboard/                        ← Dashboard
~/.hermes/scripts/                            ← Script symlinks
```

## Then What?

```bash
# 1. Auth with X API
xurl auth apps add xfactor --client-id YOUR_ID --client-secret YOUR_SECRET
xurl auth oauth2 --app xfactor YOUR_HANDLE
xurl auth default xfactor
xurl whoami

# 2. Start dashboard
cd ~/.hermes/x-dashboard && python3 -m http.server 3000

# 3. Post your first thread
python3 ~/.hermes/scripts/x-daily-poster.py afternoon

# 4. Set up cron (in Hermes)
# 8 AM: x-daily-poster.py morning
# 10 AM: x-daily-poster.py afternoon
# 2 PM: x-engagement.py
# 6 PM: x-daily-poster.py evening
# Every 30m: x-dashboard-collector.py
```

Full docs: https://github.com/hamzaashergill/xfactor