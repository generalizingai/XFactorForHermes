#!/usr/bin/env python3
"""Daily X content for @generalizingai - researches X first, then writes viral-optimized content.
Usage: python3 x-daily-poster.py morning|afternoon|evening"""

import subprocess, json, sys, time, os, random
from datetime import datetime

OS_ENV = os.environ.copy()
OS_ENV["PATH"] = f"{os.path.expanduser('~/.local/bin')}:/usr/local/bin:/usr/bin:/bin:{OS_ENV.get('PATH', '')}"

LOG = os.path.expanduser("~/.hermes/x-posts.log")
RESEARCH_LOG = os.path.expanduser("~/.hermes/x-research.log")

def log(file, msg):
    with open(file, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    print(msg)

def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=OS_ENV)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout) if r.stdout.strip() else None
    except:
        return None

def post(text):
    r = subprocess.run(["xurl", "post", text], capture_output=True, text=True, timeout=30, env=OS_ENV)
    if r.returncode != 0:
        log(LOG, f"POST FAILED: {r.stderr[:200]}")
        return None
    try:
        return json.loads(r.stdout)["data"]["id"]
    except:
        return None

def reply(pid, text):
    r = subprocess.run(["xurl", "reply", pid, text], capture_output=True, text=True, timeout=30, env=OS_ENV)
    if r.returncode == 0:
        try:
            return json.loads(r.stdout)["data"]["id"]
        except:
            return None
    return None

# ── RESEARCH PHASE ──

TRENDING_ACCOUNTS = ["levelsio", "shreyas", "karpathy", "nwitten", "mikawl_lim"]
TOPIC_QUERIES = [
    "AI agents business",
    "AI startup building",
    "AI automation workflow",
    "AI founder lessons",
    "AI SaaS product",
    "building in public AI",
    "AI tools productivity",
    "machine learning business",
]

def research_x():
    """Research what's trending in AI/business niche on X right now."""
    log(RESEARCH_LOG, "=== RESEARCH RUN ===")
    findings = {
        "trending_topics": [],
        "top_formats": [],
        "high_engagement_hooks": [],
        "timestamp": datetime.now().isoformat(),
    }
    
    # 1. Search trending topics
    for query in random.sample(TOPIC_QUERIES, min(4, len(TOPIC_QUERIES))):
        data = run(["xurl", "search", query, "-n", "5"])
        if data and "data" in data:
            for t in data["data"]:
                text = t.get("text", "")
                m = t.get("public_metrics", {})
                likes = m.get("like_count", 0)
                rts = m.get("retweet_count", 0)
                bookmarks = m.get("bookmark_count", 0)
                score = likes + rts * 2 + bookmarks * 3
                
                if score > 5 and not text.startswith("RT @") and len(text) > 40:
                    findings["high_engagement_hooks"].append({
                        "text": text[:200],
                        "score": score,
                        "query": query,
                        "likes": likes,
                        "retweets": rts,
                        "bookmarks": bookmarks,
                    })
                    log(RESEARCH_LOG, f"  TRENDING: ({score}) [{query}] {text[:80]}...")
    
    # 2. Check trending accounts' recent posts for format patterns
    for handle in TRENDING_ACCOUNTS[:3]:
        user_data = run(["xurl", "user", handle])
        uid = user_data["data"].get("id", "") if user_data and "data" in user_data else ""
        if not uid:
            continue
        
        data = run(["xurl", f"/2/users/{uid}/tweets?max_results=5&tweet.fields=public_metrics"])
        if data and "data" in data:
            for t in data["data"]:
                text = t.get("text", "")
                m = t.get("public_metrics", {})
                likes = m.get("like_count", 0)
                if likes > 10:
                    findings["top_formats"].append({
                        "author": handle,
                        "text": text[:200],
                        "likes": likes,
                    })
                    log(RESEARCH_LOG, f"  FORMAT: @{handle} ({likes} likes) {text[:80]}...")
    
    # 3. Sort by engagement
    findings["high_engagement_hooks"].sort(key=lambda x: x["score"], reverse=True)
    findings["top_formats"].sort(key=lambda x: x["likes"], reverse=True)
    
    log(RESEARCH_LOG, f"  Found {len(findings['high_engagement_hooks'])} trending hooks, {len(findings['top_formats'])} top formats")
    return findings

def extract_trending_topics(findings):
    """Extract the hottest topics from research to write about."""
    topics = set()
    for h in findings["high_engagement_hooks"][:10]:
        text = h["text"].lower()
        # Extract topic phrases
        phrases = [
            "AI agent", "LLM", "GPT", "Claude", "fine.tune", "RAG",
            "API cost", "token", "pricing", "startup", "founder",
            "build", "ship", "deploy", "automation", "workflow",
            "prompt", "model", "open source", "vector",
            "cost", "scale", "production", "enterprise",
        ]
        for p in phrases:
            if p in text or p.replace(" ", "") in text:
                topics.add(p)
    
    # If no topics found, use defaults
    if not topics:
        topics = {"AI agents", "automation", "cost optimization", "prompt engineering"}
    
    log(RESEARCH_LOG, f"  Topics extracted: {', '.join(topics)}")
    return list(topics)

# ── CONTENT GENERATION ──

def generate_morning_thread(trending_topics, top_formats):
    """Generate a thread based on what's trending. Returns list of tweet texts."""
    
    # Analyze what format is working
    thread_format = "numbered list"  # default
    for f in top_formats[:3]:
        text = f["text"].lower()
        if "thread" in text or "1." in text or "1/" in text:
            thread_format = "numbered list thread"
            break
    
    topic = trending_topics[0] if trending_topics else "AI agents"
    
    threads = {
        "AI agent": [
            "AI agents are everywhere right now. But most people are building them wrong. Here is what actually works after building production agents at @logicbaseio.",
            "The biggest mistake: giving the agent too much freedom. Start with narrow scope and strict guardrails. An agent that can do anything will cost you everything.",
            "Second mistake: no observability. You cannot improve what you cannot see. Track every decision, every API call, every failure mode from day one.",
            "Third mistake: skipping the human loop. Let your agent suggest, the human approve. Over time the human trusts more and you fade the loop out.",
            "Fourth mistake: no caching. If two users ask the same question you pay twice. Semantic caching cuts costs 40-60% immediately.",
            "The formula is simple: narrow scope + observability + human loop + caching. Build that and you have a production agent. Ignore any piece and you have a demo.",
        ],
        "cost optimization": [
            "Everyone is talking about AI API costs. Here is how to cut yours by 70% without sacrificing quality.",
            "Leak 1: you are using the same model for everything. A simple classification does not need GPT-5. Route simple tasks to cheap models. Save 30-50%.",
            "Leak 2: no caching. If user A asks 'what is your pricing' and user B asks 'how much do you cost' you pay for both. Semantic cache solves this.",
            "Leak 3: context bloat. Every API call includes the full conversation history. Keep last 5 messages plus a summary. Save 30% on tokens.",
            "Leak 4: no rate limits. One user can drain your monthly budget in a day. Set per-user limits and alerts at 80% of budget.",
            "Stack these four fixes and your API bill goes from scary to manageable. Same output quality. Way less burn.",
        ],
        "automation": [
            "The businesses winning with AI automation share one thing in common. They automated the boring stuff first. Not the hard stuff. Not the strategic stuff. The soul-crushing repetitive work.",
            "Customer support triage. Invoice data entry. Lead qualification. Email sorting. Report generation. These are not glamorous. But they have the highest ROI because the process is already well understood.",
            "The companies that fail start by trying to automate complex creative work. That is where AI still struggles. Start with predictable workflows where the inputs and outputs are clearly defined.",
            "Rule of thumb: if a human can do it in under 5 minutes with clear instructions, automate it. If it takes a human 30 minutes of thinking to get right, augment it, do not automate it.",
            "At @logicbaseio we automated cold outreach lead qualification first. Simple decision tree + AI personalization. Cut 40 hours per month. Then we expanded to more complex workflows.",
            "Start boring. Scale to interesting. That is the winning automation playbook.",
        ],
        "prompt engineering": [
            "Prompt engineering is evolving fast. Here is what changed in 2026 and what still works.",
            "Long system prompts are dead. Models now handle brief structured instructions better than 2000-word manifestos. Shorter prompts with clear structure outperform verbose ones.",
            "Structured output is the real game changer. Define your output format as a schema (JSON with types) instead of describing it in prose. Models respect structure more than natural language.",
            "Few-shot examples still matter but placement matters more. Put examples AFTER the instructions, not before. The models attention is strongest at the end of the prompt.",
            "Temperature is the most underrated parameter. Data extraction at 0.0. Code generation at 0.3. Creative at 0.7. Never above 0.8 in production. Pick based on your tolerance for hallucination.",
            "The bottom line: prompts are becoming code. Treat them like code. Version control. Test coverage. Review cycles. The days of typing whatever and hoping are over.",
        ],
        "default": [
            "Here is what I learned building AI products for the last 2 years. Most of the advice out there is wrong. Here is what actually works.",
            "Start with a single workflow. Not a platform. Not an API. One workflow that is painful enough people will pay to fix it. Do that one thing perfectly before expanding.",
            "Ship the 80% solution. Perfect is the enemy of shipped. Your first version does not need fine-tuning, multi-model routing, or streaming. It needs to work well enough for one happy user.",
            "Costs will surprise you. Your first month will be cheap. By month three your bill will be 10x what you expected. Budget for that. Cache from day one. Set limits from day one.",
            "Users do not care about your model choice. They care about reliability. An OK answer every time beats a brilliant answer some of the time. Consistency is the real competitive advantage.",
            "Build in public. It is uncomfortable. It is worth it. Every thread you write attracts users. Every lesson you share builds trust. Every failure you admit makes you relatable.",
        ],
    }
    
    # Pick the best matching thread
    for key, thread in threads.items():
        if key in " ".join(trending_topics).lower() or any(t.lower() in key for t in trending_topics):
            return thread
    
    return threads["default"]

def generate_single_post(trending_topics):
    """Generate a single value-add post based on trending topics."""
    
    posts = [
        "Most AI products fail because they try to do too much. Pick one workflow. Automate it perfectly. Then expand. The best AI companies look trivial in retrospect.",
        "I see founders obsessing over which model to use. It barely matters. What matters: is your data clean? Is your error handling solid? Do you have caching? The model is the cheapest part of the stack.",
        "The 80/20 rule in AI: 80% of value comes from the simplest implementation. Prompt + context + output parsing. The last 20% takes 80% of the effort. Ship the 80% first.",
        "Question I ask every AI founder: what happens when the model goes down? If your answer is 'that wont happen' you have not run a production AI product. Every provider has outages.",
        "Hot take: AI is not replacing developers. It is making developers more valuable by removing the typing bottleneck. The real bottleneck is understanding the problem, which is the hardest part anyway.",
        "The most underrated AI skill in 2026: knowing when NOT to use AI. Some problems are better solved with a lookup table or a basic script. Not everything needs an agent.",
        "The pricing mistake founders make: charging per API call instead of per outcome. Users do not want to think about tokens. They want to think about results.",
        "Framework for evaluating AI tools: does it reduce the time between having an idea and seeing the result? If yes, adopt it. If it adds friction, skip it.",
    ]
    
    # Try to pick a post relevant to trending topics
    topic_str = " ".join(trending_topics).lower()
    for p in posts:
        p_lower = p.lower()
        for topic in trending_topics:
            if topic.lower() in p_lower:
                return p
    
    return random.choice(posts)

def generate_evening_post(trending_topics):
    """Generate a hot take or reflection based on trending topics."""
    
    posts = [
        "The best AI products are invisible. Users get their work done without thinking about the model. If your tagline is 'AI-powered' instead of what it does, rethink your positioning.",
        "Every AI product should have a human-in-the-loop mode. Let the AI suggest, the human approve. Over time the human trusts more and you phase out the loop. Builds trust gradually.",
        "Analogy I use with clients: AI agents are like junior employees. They need clear instructions, bounded scope, and supervision. You would not give a junior the keys to everything on day one.",
        "The biggest unlock for me building @logicbaseio was realizing I do not need the best AI. I need the most reliable AI. Consistent beats clever. Predictable beats powerful.",
        "If your AI product relies on the current model being good, you have no moat. The model will get better or cheaper or both. Build your moat on data and workflows, not on model access.",
        "Most AI agents are fancy if-then chains with an LLM in the middle. And that is fine. Users do not need AGI. They need their email sorted and their leads qualified.",
        "The most important metric for AI products: retention. Do users come back? If not, none of the other metrics matter. Ship. Measure retention. Iterate.",
        "3 questions before building: does the user do this manually? Is it painful enough to fix? Will 90% accuracy still be useful? If yes to all three, build it.",
    ]
    
    topic_str = " ".join(trending_topics).lower()
    for p in posts:
        p_lower = p.lower()
        for topic in trending_topics:
            if topic.lower() in p_lower:
                return p
    
    return random.choice(posts)

# ── MAIN ──

def run_morning():
    log(LOG, "=== MORNING: Researching X ===")
    findings = research_x()
    topics = extract_trending_topics(findings)
    log(LOG, f"MORNING: Generating thread based on: {', '.join(topics[:3])}")
    thread = generate_morning_thread(topics, findings["top_formats"])
    
    first_id = post(thread[0])
    if not first_id:
        log(LOG, "MORNING FAILED: could not post first tweet")
        return
    log(LOG, f"MORNING: Thread started (id: {first_id})")
    
    prev = first_id
    for i, txt in enumerate(thread[1:], 2):
        pid = reply(prev, txt)
        if pid:
            prev = pid
            log(LOG, f"MORNING: Tweet {i}/{len(thread)}")
        time.sleep(1)
    log(LOG, "MORNING: Thread complete")
    
    # Log research findings
    log(RESEARCH_LOG, f"--- MORNING THREAD on {topics[:3]} ---")

def run_afternoon():
    log(LOG, "=== AFTERNOON: Researching X ===")
    findings = research_x()
    topics = extract_trending_topics(findings)
    log(LOG, f"AFTERNOON: Generating post based on: {', '.join(topics[:3])}")
    text = generate_single_post(topics)
    pid = post(text)
    if pid:
        log(LOG, f"AFTERNOON: Posted (id: {pid})")
    else:
        log(LOG, "AFTERNOON FAILED")

def run_evening():
    log(LOG, "=== EVENING: Researching X ===")
    findings = research_x()
    topics = extract_trending_topics(findings)
    log(LOG, f"EVENING: Generating post based on: {', '.join(topics[:3])}")
    text = generate_evening_post(topics)
    pid = post(text)
    if pid:
        log(LOG, f"EVENING: Posted (id: {pid})")
    else:
        log(LOG, "EVENING FAILED")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
    if mode == "morning":
        run_morning()
    elif mode == "afternoon":
        run_afternoon()
    elif mode == "evening":
        run_evening()