#!/usr/bin/env python3
"""X Engagement for @generalizingai — lots of likes, selective follows, all replies."""

import subprocess, json, time, os, random, sys
from datetime import datetime

OS_ENV = os.environ.copy()
OS_ENV["PATH"] = f"{os.path.expanduser('~/.local/bin')}:/usr/local/bin:/usr/bin:/bin:{OS_ENV.get('PATH', '')}"
LOG = os.path.expanduser("~/.hermes/x-engagement.log")

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n"); print(msg)

def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=OS_ENV)
        if r.returncode != 0: return None
        return json.loads(r.stdout) if r.stdout.strip() else None
    except: return None

def like(pid):
    r = subprocess.run(["xurl", "like", pid], capture_output=True, text=True, timeout=10, env=OS_ENV)
    return r.returncode == 0

def follow(handle):
    r = subprocess.run(["xurl", "follow", handle], capture_output=True, text=True, timeout=10, env=OS_ENV)
    return r.returncode == 0

def reply_to(pid, text):
    r = subprocess.run(["xurl", "reply", pid, text], capture_output=True, text=True, timeout=20, env=OS_ENV)
    return r.returncode == 0

# ── Curated list of real AI builders (only productive people) ──
PRODUCTIVE_ACCOUNTS = [
    "levelsio",       # Building 12 startups in 12 months
    "shreyas",        # AI researcher/thinker
    "karpathy",       # AI education / research
    "nwitten",        # AI entrepreneur
    "mikawl_lim",     # AI content + building
    "nikitabier",     # Building indie products
    "tibo_maker",     # AI/tech builder
    "thesamparr",     # AI startup builder
    "marclou",        # AI/startup ecosystem
    "miramurati",     # AI leader
    "aidan_mclau",    # Anthropic co-founder
    "ilyasut",        # AI safety/research
    "goodside",       # AI prompt engineering
    "svpino",         # Software engineer building
    "kvogt",          # AI startup founder
    "jeremyphoward",  # ML educator
    "rasbt",          # ML/AI researcher
    "abacaj",         # AI engineering
    "nickfloats",     # AI/design engineer
    "metrics_rock",   # Metrics/AI builder
]

VALUABLE_REPLIES = [
    "Great thread. One thing that often gets overlooked is the unit economics. Even the best AI product fails if the cost per outcome doesnt justify the price.",
    "Really thoughtful breakdown. The point about context windowing saving 30% on token costs is something most people miss. I implemented this at logicbaseio and it made a real difference.",
    "This resonates with what I have been building. The shift from prompt engineer to agent orchestrator is real. The skill is no longer writing better prompts, it is designing systems of specialized agents.",
    "Great perspective. I would add that the biggest unlock for most teams is not the model choice but the data pipeline quality. Garbage in garbage out applies 10x to AI products.",
    "Solid analysis. One thing I would flag: most people skip caching in their first version and then get a nasty surprise when the API bill comes. Semantic caching is the highest ROI investment you can make.",
    "This is exactly right. The companies winning with AI are not the ones with the best models but the ones with the best understanding of their users workflows. Tech is the easy part, distribution is the moat.",
    "Agreed. The best AI products are invisible. Users shouldnt think about the model, they should think about getting their work done. If your tagline starts with AI-powered, you might be over-indexing on tech.",
    "Interesting take. In my experience building at logicbaseio, the most important metric for AI products is not accuracy or latency but retention. Do users come back? If not nothing else matters.",
    "The hidden variable in AI product success is not model quality but how well you handle edge cases. Models will get better. Your error handling is what separates a demo from a product.",
    "This is an underrated insight. Most AI startups fail not because the tech does not work but because the business model does not work. Unit economics matter even in the AI gold rush.",
    "One thing I learned the hard way: the best way to validate an AI feature is to run it manually for a week first. If the manual process works automate it. If it does not no amount of AI fixes it.",
    "The most successful AI products I have seen focus on a single workflow not a platform. Do one thing exceptionally well before expanding. Platform ambitions before product-market fit kill startups.",
    "The metric that matters most for AI products is not accuracy. It is reliability. Users forgive occasional mistakes if the system works consistently. Inconsistency is what destroys trust.",
]

def find_best_reply(text):
    tl = text.lower()
    for r in VALUABLE_REPLIES:
        rl = r.lower()
        # Score: +3 if reply shares keywords with post
        score = sum(3 for w in ["cost","api","token","model","agent","build","startup","product","user","data"] if w in tl and w in rl)
        if score >= 3: return r
    return random.choice(VALUABLE_REPLIES)

def run_engagement():
    log("=== ENGAGEMENT RUN ===")
    actions = 0
    MAX = 50  # total actions cap
    
    # ── 1. LIKE: 30+ posts from productive accounts ──
    log("PHASE 1: Liking posts from productive AI accounts")
    for handle in random.sample(PRODUCTIVE_ACCOUNTS, min(8, len(PRODUCTIVE_ACCOUNTS))):
        if actions >= MAX: break
        user_data = run(["xurl", "user", handle])
        uid = user_data["data"].get("id", "") if user_data and "data" in user_data else ""
        if not uid: continue
        data = run(["xurl", f"/2/users/{uid}/tweets?max_results=5&tweet.fields=public_metrics"])
        if data and "data" in data:
            for t in data["data"]:
                if actions >= MAX: break
                text, pid = t.get("text",""), t.get("id","")
                if text.startswith("@") or "generalizingai" in text or not pid: continue
                if like(pid):
                    log(f"LIKE: @{handle}")
                    actions += 1
                    time.sleep(random.uniform(1, 2))
    
    # ── 2. LIKE: Trending AI posts ──
    log("PHASE 2: Liking trending AI content")
    for query in ["AI agents", "AI startup", "AI founder", "AI automation", "building in public"]:
        if actions >= MAX: break
        data = run(["xurl", "search", query, "-n", "5"])
        if data and "data" in data:
            for t in data["data"]:
                if actions >= MAX: break
                text, pid = t.get("text",""), t.get("id","")
                metrics = t.get("public_metrics", {})
                likes = metrics.get("like_count", 0)
                if text.startswith("RT @") or "generalizingai" in text: continue
                if likes < 1: continue
                if len(text.replace("https://t.co/","").strip()) < 40: continue
                if like(pid):
                    log(f"LIKE: trending ({likes} likes)")
                    actions += 1
                    time.sleep(random.uniform(1, 2))
    
    # ── 3. REPLY: To mentions ──
    log("PHASE 3: Replying to mentions")
    data = run(["xurl", "mentions", "-n", "10"])
    if data and "data" in data:
        for t in data["data"]:
            if actions >= MAX: break
            text, pid = t.get("text",""), t.get("id","")
            if "generalizingai" not in text: continue
            if text.startswith("@generalizingai"): continue
            reply = find_best_reply(text)
            if reply_to(pid, reply):
                log(f"REPLY: mention {pid}")
                actions += 1
                time.sleep(random.uniform(5, 10))
    
    # ── 4. REPLY: In our threads ──
    log("PHASE 4: Replying in thread conversations")
    data = run(["xurl", "search", "generalizingai", "-n", "10"])
    if data and "data" in data:
        for t in data["data"]:
            if actions >= MAX: break
            text, pid = t.get("text",""), t.get("id","")
            if "@generalizingai" not in text: continue
            if text.startswith("@generalizingai"): continue
            reply = find_best_reply(text)
            if reply_to(pid, reply):
                log(f"REPLY: thread {pid}")
                actions += 1
                time.sleep(random.uniform(5, 10))
    
    # ── 5. FOLLOW: Max 5, only productive accounts ──
    log("PHASE 5: Following productive accounts (max 5)")
    # Check who we already follow
    already = set()
    data = run(["xurl", "following", "-n", "50"])
    if data and "data" in data:
        already = {t.get("username","") for t in data["data"] if t.get("username")}
    
    follows = 0
    for handle in PRODUCTIVE_ACCOUNTS:
        if follows >= 5 or actions >= MAX: break
        if handle in already: continue
        if follow(handle):
            log(f"FOLLOW: @{handle} (productive AI builder)")
            actions += 1
            follows += 1
            time.sleep(random.uniform(3, 5))
    
    log(f"DONE: {actions} total actions ({sum(1 for _ in open(LOG) if 'LIKE:' in _)} likes this session)")

if __name__ == "__main__":
    run_engagement()