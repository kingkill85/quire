#!/bin/bash
set -e

# Start virtual display for SeleniumBase (standard image only)
if [ "$QUIRE_CF_BYPASS" = "internal" ] && command -v Xvfb &> /dev/null; then
    Xvfb :99 -screen 0 1920x1080x24 &
    export DISPLAY=:99
fi

# Create temp directory
mkdir -p "${QUIRE_TEMP_DIR:-/tmp/quire}"

exec "$@"
