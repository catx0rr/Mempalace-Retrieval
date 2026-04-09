#!/usr/bin/env python3
"""
mempalace-retrieval: search — structured search wrapper

Runs MemPalace semantic search with optional wing/room scoping.
Returns structured JSON output for LLM consumption.

Usage:
    python3 search.py --query "why did we switch to GraphQL"
    python3 search.py --query "auth decisions" --wing agent_memory
    python3 search.py --query "pricing" --wing agent_memory --room projects
    python3 search.py --query "timeline" --results 10
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

DEFAULT_PALACE = os.path.expanduser('~/.openclaw/mempalace/palace')
DEFAULT_RESULTS = 5
WING_CONFIG_PATH = os.path.expanduser('~/.openclaw/mempalace/wing_config.json')
MEMPALACE_BIN = os.environ.get(
    'MEMPALACE_BIN',
    os.path.expanduser('~/.openclaw/venvs/mempalace/bin/mempalace'),
)


def load_wing_config() -> dict:
    """Load wing_config.json for profile-aware defaults."""
    try:
        with open(WING_CONFIG_PATH, 'r') as f:
            return json.loads(f.read())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def search_palace(query: str, palace: str, wing: str = None,
                  room: str = None, results: int = DEFAULT_RESULTS) -> dict:
    now = datetime.now(tz=timezone.utc).isoformat()
    wing_cfg = load_wing_config()

    # Use profile default_wing if no explicit wing given
    effective_wing = wing or wing_cfg.get('default_wing')

    cmd = [
        MEMPALACE_BIN, '--palace', palace,
        'search', query,
        '--results', str(results),
    ]

    if effective_wing:
        cmd.extend(['--wing', effective_wing])
    if room:
        cmd.extend(['--room', room])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        result = {
            'timestamp': now,
            'query': query,
            'wing_requested': wing,
            'wing_effective': effective_wing,
            'room': room,
            'profile': wing_cfg.get('profile', 'unknown'),
            'wing_taxonomy': wing_cfg.get('wing_taxonomy', []),
            'results_requested': results,
            'returncode': proc.returncode,
            'output': proc.stdout.strip() if proc.stdout else '',
            'stderr': proc.stderr.strip()[:500] if proc.stderr else '',
        }

        if proc.returncode != 0:
            result['error'] = f'mempalace search failed (exit {proc.returncode})'

        return result

    except subprocess.TimeoutExpired:
        return {
            'timestamp': now,
            'query': query,
            'error': 'search timeout after 60s',
        }
    except FileNotFoundError:
        return {
            'timestamp': now,
            'query': query,
            'error': 'mempalace command not found — is it installed?',
        }


def main():
    parser = argparse.ArgumentParser(
        description='MemPalace Retrieval: Semantic search'
    )
    parser.add_argument(
        '--query', required=True,
        help='Search query'
    )
    parser.add_argument(
        '--palace', default=DEFAULT_PALACE,
        help=f'Palace path (default: {DEFAULT_PALACE})'
    )
    parser.add_argument(
        '--wing', default=None,
        help='Limit search to a specific wing'
    )
    parser.add_argument(
        '--room', default=None,
        help='Limit search to a specific room'
    )
    parser.add_argument(
        '--results', type=int, default=DEFAULT_RESULTS,
        help=f'Number of results (default: {DEFAULT_RESULTS})'
    )
    args = parser.parse_args()

    result = search_palace(
        args.query, args.palace, args.wing, args.room, args.results
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0 if 'error' not in result else 1


if __name__ == '__main__':
    sys.exit(main())
