#!/bin/bash
# Update all clawdhub skills and capture results

cd ~/.openclaw/workspace

echo "=== Starting Skill Updates ==="
echo ""

# List of skills to update
skills=(
bailian-web-search
excel-xlsx
tavily-search
skill-vetter
find-skills
self-improving-agent
github
summarize
proactive-agent
humanizer
weather
auto-updater
imap-smtp-email
multi-search-engine
automation-workflows
obsidian-direct
playwright-scraper
akshare-stock
akshare-finance
yfinance-cli
tushare-finance
ai-ppt-generate
desktop-control
stock-market-pro
auto-redbook-skills
ontology
agent-browser-clawdbot
self-improving
ai-ppt-generator
skill-creator
trello
baidu-search
free-ride
elite-longterm-memory
stock-analysis
stock-watcher
sag
deep-research-pro
data-analyst
api-gateway
eastmoney-financial-data
qveris
peekaboo
faster-whisper-local-service
webchat-https-proxy
webchat-voice-gui
tushare-data
china-stock-analysis
ai-web-automation
mx-stocks-screener
obsidian
answeroverflow
nano-pdf
xiaohongshu-mcp
)

updated=()
failed=()
unchanged=()

for skill in "${skills[@]}"; do
    echo "Checking $skill..."
    result=$(clawdhub update --force "$skill" 2>&1)
    exit_code=$?
    
    if echo "$result" | grep -q "updated ->"; then
        version=$(echo "$result" | grep "updated ->" | sed 's/.*updated -> //')
        updated+=("$skill -> $version")
        echo "  ✓ Updated to $version"
    elif echo "$result" | grep -q "not found"; then
        failed+=("$skill (not found in registry)")
        echo "  ✖ Not found in registry"
    elif echo "$result" | grep -q "up to date"; then
        unchanged+=("$skill")
        echo "  - Already up to date"
    else
        # Check if it was already at the target version
        if echo "$result" | grep -q "->"; then
            version=$(echo "$result" | grep "->" | tail -1 | sed 's/.*-> //')
            updated+=("$skill -> $version")
            echo "  ✓ Updated to $version"
        else
            unchanged+=("$skill")
            echo "  - No update needed"
        fi
    fi
    echo ""
done

echo ""
echo "=== Update Summary ==="
echo ""
echo "Updated (${#updated[@]}):"
for u in "${updated[@]}"; do
    echo "  - $u"
done
echo ""
echo "Failed (${#failed[@]}):"
for f in "${failed[@]}"; do
    echo "  - $f"
done
echo ""
echo "Unchanged (${#unchanged[@]}):"
for u in "${unchanged[@]}"; do
    echo "  - $u"
done
