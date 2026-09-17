# Worklog CLI

A real time-tracking tool for freelancers and focused work.

## Features
- Start / stop timers with project name + tags + note
- Automatic duration calculation
- Daily / weekly reports by project
- CSV export
- Single JSON file storage

## Usage
```bash
python worklog.py start "Client X" --tags design frontend -n "Homepage redesign"
python worklog.py status
python worklog.py stop

python worklog.py report          # last 7 days
python worklog.py report --days 30

python worklog.py export -o timesheet.csv
```
