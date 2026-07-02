#!/usr/bin/env bash
set -euo pipefail

REPO="hamzaashergill/xfactor"
BRANCH="main"
HERMES_SKILLS="$HOME/.hermes/skills/social-media/xfactor"
DASHBOARD_DIR="$HOME/.hermes/x-dashboard"

echo "╔═══════════════════════════════════════════╗"
echo "║     XFactor - X Growth Engine Setup      ║"
echo "╚═══════════════════════════════════════════╝"

# ── Prerequisites ──
echo ""
echo "Checking prerequisites..."

# Check xurl
if ! command -v xurl &>/dev/null; then
    echo "  Installing xurl..."
    curl -fsSL https://raw.githubusercontent.com/xdevplatform/xurl/main/install.sh | bash
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "  ✓ xurl found"
fi

# Check xurl auth
if ! xurl auth status &>/dev/null; then
    echo ""
    echo "  ⚠ No X API credentials configured."
    echo "  You need to set up OAuth 2.0 first:"
    echo ""
    echo "  1. Go to https://developer.x.com/en/portal/dashboard"
    echo "  2. Create an app or use existing one"
    echo "  3. Get Client ID and Client Secret (OAuth 2.0)"
    echo "  4. Set callback URI to http://localhost:8080/callback"
    echo ""
    echo "  Then run:"
    echo "    xurl auth apps add xfactor --client-id YOUR_ID --client-secret YOUR_SECRET"
    echo "    xurl auth oauth2 --app xfactor YOUR_HANDLE"
    echo "    xurl auth default xfactor"
    echo ""
    read -p "  Press Enter after completing auth setup, or Ctrl+C to abort..."
fi

# ── Install skill files ──
echo ""
echo "Installing XFactor skill..."
mkdir -p "$HERMES_SKILLS/scripts"

# Download from GitHub
BASE_URL="https://raw.githubusercontent.com/$REPO/$BRANCH"

echo "  Downloading SKILL.md..."
curl -fsSL "$BASE_URL/SKILL.md" -o "$HERMES_SKILLS/SKILL.md" 2>/dev/null || {
    echo "  SKILL.md not found on GitHub, you'll need to add it manually"
}

echo "  Downloading scripts..."
for script in x-daily-poster.py x-engagement.py x-dashboard-collector.py; do
    curl -fsSL "$BASE_URL/scripts/$script" -o "$HERMES_SKILLS/scripts/$script" 2>/dev/null && \
        chmod +x "$HERMES_SKILLS/scripts/$script" && \
        echo "    ✓ $script"
done

echo "  Downloading dashboard..."
mkdir -p "$DASHBOARD_DIR"
curl -fsSL "$BASE_URL/dashboard/index.html" -o "$DASHBOARD_DIR/index.html" 2>/dev/null && \
    echo "    ✓ dashboard/index.html"

# ── Create symlinks for cron access ──
echo ""
echo "Setting up script links..."
ln -sf "$HERMES_SKILLS/scripts/x-daily-poster.py" "$HOME/.hermes/scripts/x-daily-poster.py" 2>/dev/null || true
ln -sf "$HERMES_SKILLS/scripts/x-engagement.py" "$HOME/.hermes/scripts/x-engagement.py" 2>/dev/null || true
ln -sf "$HERMES_SKILLS/scripts/x-dashboard-collector.py" "$HOME/.hermes/scripts/x-dashboard-collector.py" 2>/dev/null || true

# ── Verify ──
echo ""
echo "Verifying installation..."
if [ -f "$HERMES_SKILLS/scripts/x-daily-poster.py" ]; then
    echo "  ✓ Scripts installed"
else
    echo "  ✗ Scripts not found - manual copy needed"
fi

# ── Next steps ──
echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║  XFactor installed successfully!         ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Set up X API auth (if not done):"
echo "   xurl auth apps add xfactor --client-id YOUR_ID --client-secret YOUR_SECRET"
echo "   xurl auth oauth2 --app xfactor YOUR_HANDLE"
echo "   xurl auth default xfactor"
echo ""
echo "2. Start the dashboard:"
echo "   cd ~/.hermes/x-dashboard && python3 -m http.server 3000"
echo "   Then open http://localhost:3000"
echo ""
echo "3. Set up cron jobs in Hermes:"
echo "   - Morning thread: python3 ~/.hermes/scripts/x-daily-poster.py morning (8 AM)"
echo "   - Afternoon post: python3 ~/.hermes/scripts/x-daily-poster.py afternoon (10 AM)"
echo "   - Evening post:  python3 ~/.hermes/scripts/x-daily-poster.py evening (6 PM)"
echo "   - Engagement:    python3 ~/.hermes/scripts/x-engagement.py (2 PM)"
echo "   - Dashboard:     python3 ~/.hermes/scripts/x-dashboard-collector.py (every 30m)"
echo ""
echo "4. Test it:"
echo "   python3 ~/.hermes/scripts/x-daily-poster.py afternoon"
echo ""
echo "For full docs, see: https://github.com/$REPO"