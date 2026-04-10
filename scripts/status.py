#!/usr/bin/env python3
"""
mempalace-retrieval: status — palace health check

Runs MemPalace status to show palace overview: wings, rooms, drawer counts.
Also checks that curated sources exist and reports their state.

Usage:
    python3 status.py
    python3 status.py --palace ~/.openclaw/mempalace/palace
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PALACE = os.path.expanduser('~/.openclaw/mempalace/palace')
DEFAULT_SOURCES = os.path.expanduser('~/.openclaw/mempalace-sources/curated')
MEMPALACE_BIN = os.environ.get(
    'MEMPALACE_BIN',
    os.path.expanduser('~/.openclaw/venvs/mempalace/bin/mempalace'),
)


def check_sources(sources_path: str) -> dict:
    src = Path(sources_path)
    files = {}

    for name in ['MEMORY.md', 'LTMEMORY.md', 'procedures.md']:
        f = src / name
        if f.exists():
            files[name] = {
                'exists': True,
                'size_bytes': f.stat().st_size,
                'modified': datetime.fromtimestamp(
                    f.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
            }
        else:
            files[name] = {'exists': False}

    episodes_dir = src / 'episodes'
    if episodes_dir.exists() and episodes_dir.is_dir():
        episode_files = list(episodes_dir.glob('*.md'))
        files['episodes/'] = {
            'exists': True,
            'count': len(episode_files),
            'files': [f.name for f in sorted(episode_files)],
        }
    else:
        files['episodes/'] = {'exists': False, 'count': 0}

    return files


def get_status(palace: str, sources: str) -> dict:
    now = datetime.now(tz=timezone.utc).isoformat()

    # Check palace status via CLI
    cmd = [MEMPALACE_BIN, '--palace', palace, 'status']

    palace_status = None
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
        )
        palace_status = {
            'returncode': proc.returncode,
            'output': proc.stdout.strip() if proc.stdout else '',
            'stderr': proc.stderr.strip()[:500] if proc.stderr else '',
        }
    except subprocess.TimeoutExpired:
        palace_status = {'error': 'status timeout'}
    except FileNotFoundError:
        palace_status = {'error': 'mempalace command not found'}

    # Check curated sources
    source_status = check_sources(sources)

    # Check directory structure
    palace_path = Path(palace)
    wing_config_path = Path(os.path.expanduser('~/.openclaw/mempalace/wing_config.json'))
    dirs = {
        'palace_dir': palace_path.exists(),
        'config': Path(os.path.expanduser('~/.openclaw/mempalace/config.json')).exists(),
        'wing_config': wing_config_path.exists(),
        'identity': Path(os.path.expanduser('~/.openclaw/mempalace/identity.txt')).exists(),
        'curated_dir': Path(sources).exists(),
    }

    # Read profile from wing_config if it exists
    profile_info = {}
    if wing_config_path.exists():
        try:
            with open(wing_config_path, 'r') as f:
                wing_cfg = json.loads(f.read())
            profile_info = {
                'profile': wing_cfg.get('profile', 'unknown'),
                'default_wing': wing_cfg.get('default_wing', 'agent_memory'),
                'wing_taxonomy': wing_cfg.get('wing_taxonomy', []),
                'wake_up_priorities': wing_cfg.get('wake_up_priorities', []),
            }
        except json.JSONDecodeError:
            profile_info = {'error': 'wing_config.json is malformed'}

    result = {
        'timestamp': now,
        'palace_path': palace,
        'sources_path': sources,
        'directories': dirs,
        'profile': profile_info,
        'palace': palace_status,
        'curated_sources': source_status,
    }

    # Flag critical failures
    errors = []
    if not dirs['palace_dir']:
        errors.append('palace directory missing')
    if not dirs['config']:
        errors.append('config.json missing')
    if not dirs['wing_config']:
        errors.append('wing_config.json missing')
    if not dirs['curated_dir']:
        errors.append('curated sources directory missing')
    if palace_status and palace_status.get('error'):
        errors.append(f'palace status: {palace_status["error"]}')
    if palace_status and palace_status.get('returncode', 0) != 0:
        errors.append(f'mempalace status failed (exit {palace_status["returncode"]})')

    if errors:
        result['error'] = '; '.join(errors)

    result['ok'] = len(errors) == 0
    result['config_ready'] = dirs['config'] and dirs['wing_config']
    result['curated_ready'] = dirs['curated_dir']
    result['palace_ready'] = dirs['palace_dir'] and bool(
        palace_status and palace_status.get('returncode') == 0
    )
    result['retrieval_ready'] = (
        result['config_ready'] and result['curated_ready'] and result['palace_ready']
    )

    return result


def main():
    parser = argparse.ArgumentParser(
        description='MemPalace Retrieval: Palace status check'
    )
    parser.add_argument(
        '--palace', default=DEFAULT_PALACE,
        help=f'Palace path (default: {DEFAULT_PALACE})'
    )
    parser.add_argument(
        '--sources', default=DEFAULT_SOURCES,
        help=f'Curated sources path (default: {DEFAULT_SOURCES})'
    )
    args = parser.parse_args()

    result = get_status(args.palace, args.sources)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 1 if 'error' in result else 0


if __name__ == '__main__':
    sys.exit(main())
