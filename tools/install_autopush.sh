#!/bin/bash
# One-off: installs the launchd job that runs tools/autopush.sh every 5 minutes. Run from Terminal:
#   bash ~/booking-window/tools/install_autopush.sh
set -e
PLIST="$HOME/Library/LaunchAgents/co.whentobook.autopush.plist"
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>co.whentobook.autopush</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$HOME/booking-window/tools/autopush.sh</string></array>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/whentobook-autopush.log</string>
</dict></plist>
PL
launchctl bootout "gui/$(id -u)/co.whentobook.autopush" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed. First run happening now; log: ~/Library/Logs/whentobook-autopush.log"
sleep 20; tail -5 "$HOME/Library/Logs/whentobook-autopush.log" 2>/dev/null || true
