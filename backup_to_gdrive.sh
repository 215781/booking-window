#!/usr/bin/env bash
# Backs up whentobook.co.uk project files to Google Drive for Desktop sync folder.
# Creates a dated snapshot at: WhenToBook_Backups/YYYY-MM-DD/

REPO_DIR="$HOME/booking-window"
LOG_FILE="$REPO_DIR/backup.log"
BACKUP_DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Locate Google Drive sync root dynamically
GDRIVE_ROOT=""
for dir in "$HOME/Library/CloudStorage"/GoogleDrive-*/; do
    if [ -d "${dir}My Drive" ]; then
        GDRIVE_ROOT="${dir}My Drive"
        break
    fi
done

# Fallback to legacy Google Drive path
if [ -z "$GDRIVE_ROOT" ]; then
    for candidate in "$HOME/Google Drive/My Drive" "$HOME/Google Drive"; do
        if [ -d "$candidate" ]; then
            GDRIVE_ROOT="$candidate"
            break
        fi
    done
fi

if [ -z "$GDRIVE_ROOT" ]; then
    echo "[$TIMESTAMP] ERROR: Google Drive folder not found — is Google Drive for Desktop running?" >> "$LOG_FILE"
    exit 1
fi

BACKUP_DIR="$GDRIVE_ROOT/WhenToBook_Backups/$BACKUP_DATE"
mkdir -p "$BACKUP_DIR"

if ! cd "$REPO_DIR"; then
    echo "[$TIMESTAMP] ERROR: Cannot cd to $REPO_DIR" >> "$LOG_FILE"
    exit 1
fi

ERRORS=0

# Copy a directory into BACKUP_DIR (silently skips if it doesn't exist)
backup_dir() {
    local src="$1"
    if [ -d "$src" ]; then
        rsync -a --delete "$src" "$BACKUP_DIR/" 2>>"$LOG_FILE" || ERRORS=$((ERRORS + 1))
    fi
}

# Copy a single file into BACKUP_DIR (silently skips if it doesn't exist)
backup_file() {
    local src="$1"
    local dest_dir="${2:-$BACKUP_DIR}"
    if [ -f "$src" ]; then
        cp "$src" "$dest_dir/" 2>>"$LOG_FILE" || ERRORS=$((ERRORS + 1))
    fi
}

# Directories
backup_dir "_data"
backup_dir "_posts"
backup_dir "_layouts"
backup_dir "_includes"
backup_dir "assets"
backup_dir ".github"

# clubmed/index.html — preserve subdirectory structure
if [ -f "clubmed/index.html" ]; then
    mkdir -p "$BACKUP_DIR/clubmed"
    backup_file "clubmed/index.html" "$BACKUP_DIR/clubmed"
fi

# Individual project files
for f in index.html about.md _config.yml PLAN.md ORCHESTRATOR.md BUILDER.md SCRIBE.md CLAUDE.md NEXT_SESSION_PROMPT.md IMPROVEMENT_PLAN.md; do
    backup_file "$f"
done

# Python scripts
for py in *.py; do
    [ -f "$py" ] && backup_file "$py"
done

if [ $ERRORS -eq 0 ]; then
    echo "[$TIMESTAMP] OK backup → $BACKUP_DIR" >> "$LOG_FILE"
    exit 0
else
    echo "[$TIMESTAMP] PARTIAL: $ERRORS error(s) — backup may be incomplete → $BACKUP_DIR" >> "$LOG_FILE"
    exit 1
fi
