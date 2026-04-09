# MemPalace Retrieval — Installation Guide

One-time local installation of the MemPalace retrieval skill and upstream MemPalace package.
This is an **operator task** — run these commands on the host machine before agent setup.

**After installation, the agent runs [SETUP.md](SETUP.md) for first-time configuration.**

---

## Prerequisites

- Python 3.9+
- Git
- OpenClaw workspace at `~/.openclaw/workspace/`
- `~/.local/bin` in PATH (for symlinked CLI)

---

## Step 0: Install the Retrieval Skill

```bash
git clone https://github.com/catx0rr/mempalace-retrieval.git \
  ~/.openclaw/workspace/skills/mempalace-retrieval
```

## Step 1: Prepare Skeleton Directories

```bash
# Upstream source + virtualenv
mkdir -p ~/.openclaw/src
mkdir -p ~/.openclaw/venvs

# MemPalace runtime state
mkdir -p ~/.openclaw/mempalace

# Curated source mirror
mkdir -p ~/.openclaw/mempalace-sources/{curated/episodes,convos,generated}
```

## Step 2: Clone Upstream MemPalace

```bash
git clone https://github.com/milla-jovovich/mempalace.git ~/.openclaw/src/mempalace
cd ~/.openclaw/src/mempalace
git checkout <TESTED_COMMIT_SHA>    # Pin to tested commit — do not track main
```

**Deployment note:** Always pin to a tested commit SHA. MemPalace `main` moves fast
and unpinned `chromadb` 1.x builds can crash `status`, `search`, and `wake-up` after
indexing. Record the tested SHA in your deployment notes before moving on.

## Step 3: Create Dedicated Virtualenv

```bash
python3 -m venv ~/.openclaw/venvs/mempalace
```

## Step 4: Upgrade Packaging Tools

```bash
~/.openclaw/venvs/mempalace/bin/python -m pip install --upgrade pip setuptools wheel
```

## Step 5: Install MemPalace in Editable Mode

```bash
~/.openclaw/venvs/mempalace/bin/python -m pip install -e ~/.openclaw/src/mempalace
```

**Pin chromadb** to a tested range (upstream does not pin it and 1.x can cause segfaults):

```bash
~/.openclaw/venvs/mempalace/bin/python -m pip install 'chromadb>=0.4.0,<1.0.0'
```

## Step 6: Symlink CLI into PATH

```bash
mkdir -p ~/.local/bin
ln -sf ~/.openclaw/venvs/mempalace/bin/mempalace ~/.local/bin/mempalace
```

## Step 7: Verify Installation

```bash
# Check package is installed
~/.openclaw/venvs/mempalace/bin/python -m pip show mempalace

# Check module loads
~/.openclaw/venvs/mempalace/bin/python -c 'import mempalace; print(mempalace.__file__)'

# Check CLI binary exists
ls -la ~/.openclaw/venvs/mempalace/bin/ | grep mempalace || true
```

## Step 8: Validate Commands

```bash
# CLI help
~/.openclaw/venvs/mempalace/bin/mempalace --help

# MCP server (optional — for future MCP integration)
~/.openclaw/venvs/mempalace/bin/python -m mempalace.mcp_server --help
```

---

## Post-Install Checklist

- [ ] `~/.openclaw/workspace/skills/mempalace-retrieval/` exists with SKILL.md
- [ ] `~/.openclaw/src/mempalace/` exists (upstream clone)
- [ ] `~/.openclaw/venvs/mempalace/` exists (virtualenv)
- [ ] `mempalace --help` works from PATH
- [ ] `~/.openclaw/mempalace/` directory exists
- [ ] `~/.openclaw/mempalace-sources/curated/` directory exists

---

## Next Step

Tell the agent:

> Set up MemPalace retrieval. Read `skills/mempalace-retrieval/SETUP.md` and follow every step.

Or if both install and setup need to happen:

> Install and set up MemPalace retrieval. Read `skills/mempalace-retrieval/INSTALL.md` first, then follow `SETUP.md`.
