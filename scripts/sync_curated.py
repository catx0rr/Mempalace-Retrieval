#!/usr/bin/env python3
"""
mempalace-retrieval: sync_curated — copy workspace memory surfaces to curated mirror

Copies the authoritative memory files from the workspace into the MemPalace
curated sources directory. This is the only input path for MemPalace — it never
reads directly from the workspace.

Usage:
    python3 sync_curated.py
    python3 sync_curated.py --workspace ~/.openclaw/workspace --target ~/.openclaw/mempalace-sources/curated
    python3 sync_curated.py --dry-run
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_WORKSPACE = os.path.expanduser('~/.openclaw/workspace')
DEFAULT_TARGET = os.path.expanduser('~/.openclaw/mempalace-sources/curated')

# Files to sync from workspace to curated mirror
SYNC_MAP = [
    {'src': 'MEMORY.md', 'dst': 'MEMORY.md'},
    {'src': 'LTMEMORY.md', 'dst': 'LTMEMORY.md'},
    {'src': 'memory/procedures.md', 'dst': 'procedures.md'},
]

# Directory to sync (episodes)
SYNC_DIRS = [
    {'src': 'memory/episodes', 'dst': 'episodes'},
]


def sync_curated(workspace: str, target: str, dry_run: bool = False) -> dict:
    ws = Path(workspace)
    tgt = Path(target)
    now = datetime.now(tz=timezone.utc).isoformat()

    if not ws.exists():
        return {
            'error': f'Workspace not found: {workspace}',
            'timestamp': now,
            'synced_count': 0,
            'skipped_count': 0,
            'error_count': 1,
            'synced': [],
            'skipped': [],
            'errors': [{'src': 'workspace', 'error': f'not found: {workspace}'}],
        }

    # Ensure target dirs exist
    if not dry_run:
        tgt.mkdir(parents=True, exist_ok=True)
        (tgt / 'episodes').mkdir(exist_ok=True)

    synced = []
    skipped = []
    errors = []

    # Sync individual files
    for entry in SYNC_MAP:
        src_path = ws / entry['src']
        dst_path = tgt / entry['dst']

        if not src_path.exists():
            skipped.append({
                'src': str(src_path),
                'reason': 'source does not exist',
            })
            continue

        src_size = src_path.stat().st_size
        src_mtime = datetime.fromtimestamp(
            src_path.stat().st_mtime, tz=timezone.utc
        ).isoformat()

        # Check if target exists and is identical
        if dst_path.exists():
            dst_size = dst_path.stat().st_size
            if dst_size == src_size:
                src_content = src_path.read_bytes()
                dst_content = dst_path.read_bytes()
                if src_content == dst_content:
                    skipped.append({
                        'src': entry['src'],
                        'reason': 'unchanged',
                    })
                    continue

        if not dry_run:
            try:
                shutil.copy2(src_path, dst_path)
            except (IOError, OSError) as e:
                errors.append({
                    'src': entry['src'],
                    'error': str(e),
                })
                continue

        synced.append({
            'src': entry['src'],
            'dst': entry['dst'],
            'size_bytes': src_size,
            'modified': src_mtime,
        })

    # Sync episode directories
    for entry in SYNC_DIRS:
        src_dir = ws / entry['src']
        dst_dir = tgt / entry['dst']

        if not src_dir.exists() or not src_dir.is_dir():
            skipped.append({
                'src': entry['src'],
                'reason': 'source directory does not exist',
            })
            continue

        episode_files = sorted(src_dir.glob('*.md'))
        for ep_file in episode_files:
            dst_file = dst_dir / ep_file.name
            ep_size = ep_file.stat().st_size

            # Check if unchanged
            if dst_file.exists():
                if dst_file.read_bytes() == ep_file.read_bytes():
                    skipped.append({
                        'src': f'{entry["src"]}/{ep_file.name}',
                        'reason': 'unchanged',
                    })
                    continue

            if not dry_run:
                try:
                    shutil.copy2(ep_file, dst_file)
                except (IOError, OSError) as e:
                    errors.append({
                        'src': f'{entry["src"]}/{ep_file.name}',
                        'error': str(e),
                    })
                    continue

            synced.append({
                'src': f'{entry["src"]}/{ep_file.name}',
                'dst': f'{entry["dst"]}/{ep_file.name}',
                'size_bytes': ep_size,
            })

    return {
        'timestamp': now,
        'workspace': workspace,
        'target': target,
        'dry_run': dry_run,
        'synced_count': len(synced),
        'skipped_count': len(skipped),
        'error_count': len(errors),
        'synced': synced,
        'skipped': skipped,
        'errors': errors,
    }


def main():
    parser = argparse.ArgumentParser(
        description='MemPalace Retrieval: Sync curated sources from workspace'
    )
    parser.add_argument(
        '--workspace', default=DEFAULT_WORKSPACE,
        help=f'Workspace path (default: {DEFAULT_WORKSPACE})'
    )
    parser.add_argument(
        '--target', default=DEFAULT_TARGET,
        help=f'Curated mirror path (default: {DEFAULT_TARGET})'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show what would be synced without copying'
    )
    args = parser.parse_args()

    result = sync_curated(args.workspace, args.target, args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0 if result.get('error_count', 0) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
