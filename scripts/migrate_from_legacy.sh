#!/usr/bin/env bash
# Safe one-time copy of Study Workflow data from a legacy app tree into this V3 project.
# - Does NOT modify or delete the legacy app (read-only from source).
# - Backs up existing V3 data/courses before overwriting (if any).
#
# Usage:
#   ./scripts/migrate_from_legacy.sh
#   LEGACY_ROOT=/path/to/study_workflow_app ./scripts/migrate_from_legacy.sh
#   ./scripts/migrate_from_legacy.sh --dry-run
#
# Stop uvicorn for BOTH apps before running (SQLite file copy must not race a running writer).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V3_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LEGACY_ROOT="${LEGACY_ROOT:-/Users/zay/Desktop/Projects/Study-bot/study_workflow_app}"

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

LEGACY_DATA="${LEGACY_ROOT}/data"
LEGACY_DB="${LEGACY_DATA}/app.db"
LEGACY_COURSES="${LEGACY_ROOT}/courses"

V3_DATA="${V3_ROOT}/data"
V3_DB="${V3_DATA}/app.db"
V3_COURSES="${V3_ROOT}/courses"

die() { echo "Error: $*" >&2; exit 1; }

[[ -d "$LEGACY_ROOT" ]] || die "Legacy app not found: $LEGACY_ROOT"
[[ -f "$LEGACY_DB" ]] || die "Legacy database not found: $LEGACY_DB"
[[ -d "$LEGACY_COURSES" ]] || die "Legacy courses dir not found: $LEGACY_COURSES"

echo "Legacy: $LEGACY_ROOT"
echo "V3:     $V3_ROOT"
echo ""

need_backup=0
if [[ -f "$V3_DB" ]] && [[ -s "$V3_DB" ]]; then
  need_backup=1
fi
if [[ -d "$V3_COURSES" ]] && [[ -n "$(ls -A "$V3_COURSES" 2>/dev/null || true)" ]]; then
  need_backup=1
fi

TS="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${V3_ROOT}/migration_backups/${TS}"

if [[ "$need_backup" -eq 1 ]]; then
  echo "Existing V3 data detected — will back up to:"
  echo "  $BACKUP_DIR"
else
  echo "V3 data/courses empty or minimal — no backup required (nothing to preserve)."
fi

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] $*"
  else
    eval "$@"
  fi
}

mkdir -p "${V3_DATA}" "${V3_COURSES}"

if [[ "$need_backup" -eq 1 ]]; then
  run "mkdir -p \"$BACKUP_DIR\""
  if [[ -f "$V3_DB" ]]; then
    run "cp -a \"$V3_DB\" \"$BACKUP_DIR/app.db.v3_before\""
  fi
  if [[ -d "$V3_COURSES" ]] && [[ -n "$(ls -A "$V3_COURSES" 2>/dev/null || true)" ]]; then
    run "cp -a \"$V3_COURSES\" \"$BACKUP_DIR/courses.v3_before\""
  fi
  echo "Backup step done (or dry-run)."
  echo ""
fi

echo "Importing SQLite database..."
run "cp -a \"$LEGACY_DB\" \"$V3_DB\""

echo "Importing courses tree (sources, outputs, topic_deep_dives, meta, etc.)..."
run "rsync -a --delete \"${LEGACY_COURSES}/\" \"${V3_COURSES}/\""

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo ""
  echo "Dry run finished. Run without --dry-run to apply."
  exit 0
fi

echo ""
echo "Done. Imported:"
echo "  - $V3_DB"
echo "  - $V3_COURSES/"
echo ""
echo "Next: start V3 from $V3_ROOT (uvicorn) and open /. Courses, lectures, generated files,"
echo "topic deep dives, planner rows, and study progress come from the copied database and folders."
echo "If something looks wrong, restore from: $BACKUP_DIR (if created)."
