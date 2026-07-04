#!/bin/bash
# JARVIS OS Auto-Sync Setup
# Run once on your Hostinger VPS as root
# Usage: bash setup.sh <GITHUB_PAT>

PAT=$1
GH_USER='thegreatsagetattoosandtarot-tech'
REPO='Hermes_bot.Jarvis'
VPS_DEST='/docker/hermes-agent-7t79/data/profiles/unrestricted'
SYNC_LOG='/root/jarvis-sync.log'

# Clone or pull the repo
if [ ! -d /root/Hermes_bot.Jarvis ]; then
  git clone https://${PAT}@github.com/${GH_USER}/${REPO}.git /root/Hermes_bot.Jarvis
  echo "Cloned JARVIS OS repo"
else
  cd /root/Hermes_bot.Jarvis && git pull
  echo "Pulled latest JARVIS OS"
fi

# Copy files to Hermes profile
cp -r /root/Hermes_bot.Jarvis/skills/ ${VPS_DEST}/skills/ 2>/dev/null
cp /root/Hermes_bot.Jarvis/SOUL.md ${VPS_DEST}/ 2>/dev/null
cp /root/Hermes_bot.Jarvis/Continuity.md ${VPS_DEST}/memory/ 2>/dev/null
cp -r /root/Hermes_bot.Jarvis/memory/ ${VPS_DEST}/memory/ 2>/dev/null
echo "Files synced to Hermes profile"

# Set up hourly cron
CRON_CMD="0 * * * * cd /root/Hermes_bot.Jarvis && git pull >> ${SYNC_LOG} 2>&1 && cp -r /root/Hermes_bot.Jarvis/skills/ ${VPS_DEST}/skills/ && cp -r /root/Hermes_bot.Jarvis/memory/ ${VPS_DEST}/memory/"
(crontab -l 2>/dev/null | grep -v Hermes_bot; echo "$CRON_CMD") | crontab -
echo "Hourly auto-sync cron installed"

# Restart Hermes container to pick up new files
docker restart hermes-agent-7t79-hermes-agent-1
echo "Hermes restarted"

echo "=== JARVIS OS auto-sync active ==="
echo "Repo: https://github.com/${GH_USER}/${REPO}"
echo "Log: ${SYNC_LOG}"
