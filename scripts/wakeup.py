#!/usr/bin/env python3
"""
mempalace-retrieval: wakeup — generate scoped wake-up context

Runs MemPalace wake-up to generate L0 + L1 context (~600-900 tokens).
Useful for session start or context preloading before answering domain questions.

Usage:
    python3 wakeup.py
    python3 wakeup.py --wing agent_memory
    python3 wakeup.py --palace ~/.openclaw/mempalace/palace
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

DEFAULT_PALACE = os.path.expanduser('~/.openclaw/mempalace/palace')
WING_CONFIG_PATH = os.path.expanduser('~/.openclaw/mempalace/wing_config.json')
MEMPALACE_BIN = os.environ.get(
    'MEMPALACE_BIN',
    os.path.expanduser('~/.openclaw/venvs/mempalace/bin/mempalace'),
)


def load_wing_config() -> dict:
    """Load wing_config.json for profile-aware wake-up."""
    try:
        with open(WING_CONFIG_PATH, 'r') as f:
            return json.loads(f.read())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_wakeup(palace: str, wing: str = None) -> dict:
    now = datetime.now(tz=timezone.utc).isoformat()
    wing_cfg = load_wing_config()

    # Use profile default_wing if no explicit wing given
    effective_wing = wing or wing_cfg.get('default_wing')

    cmd = [MEMPALACE_BIN, 'wake-up', '--palace', palace]

    if effective_wing:
        cmd.extend(['--wing', effective_wing])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = proc.stdout.strip() if proc.stdout else ''

        result = {
            'timestamp': now,
            'wing_requested': wing,
            'wing_effective': effective_wing,
            'profile': wing_cfg.get('profile', 'unknown'),
            'wake_up_priorities': wing_cfg.get('wake_up_priorities', []),
            'returncode': proc.returncode,
            'context': output,
            'word_estimate': len(output.split()),
            'stderr': proc.stderr.strip()[:500] if proc.stderr else '',
        }

        if proc.returncode != 0:
            result['error'] = f'mempalace wake-up failed (exit {proc.returncode})'

        return result

    except subprocess.TimeoutExpired:
        return {
            'timestamp': now,
            'error': 'wake-up timeout after 30s',
        }
    except FileNotFoundError:
        return {
            'timestamp': now,
            'error': 'mempalace command not found — is it installed?',
        }


def main():
    parser = argparse.ArgumentParser(
        description='MemPalace Retrieval: Wake-up context generator'
    )
    parser.add_argument(
        '--palace', default=DEFAULT_PALACE,
        help=f'Palace path (default: {DEFAULT_PALACE})'
    )
    parser.add_argument(
        '--wing', default=None,
        help='Generate wake-up for a specific wing'
    )
    args = parser.parse_args()

    result = get_wakeup(args.palace, args.wing)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0 if 'error' not in result else 1


if __name__ == '__main__':
    sys.exit(main())
