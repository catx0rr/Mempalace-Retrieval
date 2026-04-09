#!/usr/bin/env python3
"""
mempalace-retrieval: mine_curated — run MemPalace mining against curated mirror

Mines the curated memory surfaces into MemPalace's ChromaDB index.
This is the only ingest path — MemPalace never reads from the workspace directly.

Mines in projects mode against the curated mirror (MEMORY.md, LTMEMORY.md,
procedures.md, episodes/). Conversation mining (convos/) is not enabled in phase one.

Usage:
    python3 mine_curated.py
    python3 mine_curated.py --dry-run
    python3 mine_curated.py --sources ~/.openclaw/mempalace-sources/curated --palace ~/.openclaw/mempalace/palace
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_SOURCES = os.path.expanduser('~/.openclaw/mempalace-sources/curated')
DEFAULT_PALACE = os.path.expanduser('~/.openclaw/mempalace/palace')
WING_CONFIG_PATH = os.path.expanduser('~/.openclaw/mempalace/wing_config.json')
FALLBACK_WING = 'agent_memory'
MEMPALACE_BIN = os.environ.get(
    'MEMPALACE_BIN',
    os.path.expanduser('~/.openclaw/venvs/mempalace/bin/mempalace'),
)


def get_default_wing() -> str:
    """Read default_wing from wing_config.json, fall back to 'agent_memory'."""
    try:
        with open(WING_CONFIG_PATH, 'r') as f:
            cfg = json.loads(f.read())
        return cfg.get('default_wing', FALLBACK_WING)
    except (FileNotFoundError, json.JSONDecodeError):
        return FALLBACK_WING


def run_mine(sources: str, palace: str, wing: str, dry_run: bool = False) -> dict:
    now = datetime.now(tz=timezone.utc).isoformat()
    src = Path(sources)
    results = []

    if not src.exists():
        return {
            'error': f'Curated sources not found: {sources}',
            'timestamp': now,
        }

    # Check what's available to mine
    available = []
    for name in ['MEMORY.md', 'LTMEMORY.md', 'procedures.md']:
        if (src / name).exists():
            available.append(name)

    episodes_dir = src / 'episodes'
    episode_count = 0
    if episodes_dir.exists() and episodes_dir.is_dir():
        episode_count = len(list(episodes_dir.glob('*.md')))
        if episode_count > 0:
            available.append(f'episodes/ ({episode_count} files)')

    if not available:
        return {
            'timestamp': now,
            'sources': sources,
            'status': 'nothing_to_mine',
            'available': [],
        }

    # Build the mine command
    cmd = [
        MEMPALACE_BIN, '--palace', palace,
        'mine', sources,
        '--wing', wing,
    ]

    if dry_run:
        cmd.append('--dry-run')

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )

        results.append({
            'command': ' '.join(cmd),
            'returncode': proc.returncode,
            'stdout': proc.stdout.strip()[-2000:] if proc.stdout else '',
            'stderr': proc.stderr.strip()[-500:] if proc.stderr else '',
        })

        if proc.returncode != 0:
            return {
                'error': f'mempalace mine failed (exit {proc.returncode})',
                'timestamp': now,
                'sources': sources,
                'palace': palace,
                'wing': wing,
                'mine_results': results,
            }

    except subprocess.TimeoutExpired:
        results.append({
            'command': ' '.join(cmd),
            'error': 'timeout after 300s',
        })
    except FileNotFoundError:
        return {
            'error': 'mempalace command not found — is it installed? (pip install mempalace)',
            'timestamp': now,
        }

    return {
        'timestamp': now,
        'sources': sources,
        'palace': palace,
        'wing': wing,
        'dry_run': dry_run,
        'available_files': available,
        'mine_results': results,
    }


def main():
    parser = argparse.ArgumentParser(
        description='MemPalace Retrieval: Mine curated sources into palace'
    )
    parser.add_argument(
        '--sources', default=DEFAULT_SOURCES,
        help=f'Curated sources path (default: {DEFAULT_SOURCES})'
    )
    parser.add_argument(
        '--palace', default=DEFAULT_PALACE,
        help=f'Palace path (default: {DEFAULT_PALACE})'
    )
    parser.add_argument(
        '--wing', default=None,
        help=f'Wing name for mined content (default: from wing_config.json or {FALLBACK_WING})'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show what would be mined without filing'
    )
    args = parser.parse_args()

    wing = args.wing or get_default_wing()
    result = run_mine(args.sources, args.palace, wing, args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0 if 'error' not in result else 1


if __name__ == '__main__':
    sys.exit(main())
