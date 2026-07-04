# JARVIS OS VPS Auto-Sync

This script syncs your JARVIS OS from GitHub to your Hostinger VPS automatically.

## Setup (run once on VPS)

ssh root@2.25.142.122 'bash -s' < setup.sh <YOUR_GITHUB_PAT>

## What it does
- Clones Hermes_bot.Jarvis repo
- Copies skills, memory, SOUL.md to Hermes profile
- Sets up hourly git pull cron
- Restarts Hermes container

## Manual sync anytime
ssh root@2.25.142.122 'cd /root/Hermes_bot.Jarvis && git pull && cp -r skills/ /docker/hermes-agent-7t79/data/profiles/unrestricted/skills/ && docker restart hermes-agent-7t79-hermes-agent-1'
