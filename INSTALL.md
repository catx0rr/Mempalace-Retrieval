# MemPalace Retrieval — Installation Guide

One-time local installation of the MemPalace retrieval skill and upstream MemPalace package.
This is an **operator task** — run these commands on the host machine before agent setup.

**After installation, the agent runs [SETUP.md](SETUP.md) for first-time configuration.**

---

## Purpose

This guide must **not** assume the retrieval skill always lives at:

- `~/.openclaw/workspace/skills/mempalace-retrieval/`

The skill may be installed in:
- the default workspace skill root
- another standard skill root
- a shared skill pack loaded through `skills.load.extraDirs`

The installation should therefore be **path-variable driven**.

If still unsure, **ask** the operator where he downloaded the skill. 

---

## Prerequisites

- Python 3.9+
- Git
- OpenClaw installed
- `~/.local/bin` in PATH (for symlinked CLI)
- a chosen skill root for `mempalace-retrieval`

---

## Step 0: Choose the Skill Install Root

Choose where the `mempalace-retrieval` skill will live.

### Option A — default workspace skills

```bash
export SKILL_ROOT="$HOME/.openclaw/workspace/skills"
```

### Option B — shared skill pack loaded through `extraDirs`

Example category root:

```bash
export SKILL_ROOT="$HOME/.openclaw/skills-pack/cognitive"
```

If you use `extraDirs`, the parent root should contain the skill directory directly:

```text
$SKILL_ROOT/
└── mempalace-retrieval/
```

Do **not** point `SKILL_ROOT` at a repo root that requires undocumented recursive discovery.

Now derive the final skill path:

```bash
export SKILL_DIR="$SKILL_ROOT/mempalace-retrieval"
mkdir -p "$SKILL_ROOT"
```

---

## Step 1: Install the Retrieval Skill

```bash
git clone https://github.com/catx0rr/mempalace-retrieval.git "$SKILL_DIR"
```

Verify the skill exists:

```bash
ls "$SKILL_DIR/SKILL.md"
```

---

## Step 2: If Needed, Register `extraDirs`

Skip this step if you installed into the default workspace skill root.

If you installed into a shared skill pack root, register that root with OpenClaw:

```bash
openclaw config set skills.load.extraDirs "[
  \"$SKILL_ROOT\"
]" --strict-json
```

If you already have other extra skill roots configured, merge them instead of overwriting.

Verify:

```bash
openclaw config get skills.load.extraDirs --json
```

---

## Step 3: Prepare Skeleton Directories

```bash
# Upstream source + virtualenv
mkdir -p "$HOME/.openclaw/src"
mkdir -p "$HOME/.openclaw/venvs"

# MemPalace runtime state
mkdir -p "$HOME/.openclaw/mempalace"

# Curated source mirror
mkdir -p "$HOME/.openclaw/mempalace-sources"/{curated/episodes,convos,generated}
```

---

## Step 4: Clone Upstream MemPalace

```bash
git clone https://github.com/milla-jovovich/mempalace.git "$HOME/.openclaw/src/mempalace"
cd "$HOME/.openclaw/src/mempalace"
git checkout <TESTED_COMMIT_SHA>    # Pin to tested commit — do not track main
```

**Deployment note:** Always pin to a tested commit SHA. MemPalace `main` moves fast,
and unpinned `chromadb` 1.x builds can crash `status`, `search`, and `wake-up` after
indexing. Record the tested SHA in your deployment notes before moving on.

---

## Step 5: Create Dedicated Virtualenv

```bash
python3 -m venv "$HOME/.openclaw/venvs/mempalace"
```

---

## Step 6: Upgrade Packaging Tools

```bash
"$HOME/.openclaw/venvs/mempalace/bin/python" -m pip install --upgrade pip setuptools wheel
```

---

## Step 7: Install MemPalace in Editable Mode

```bash
"$HOME/.openclaw/venvs/mempalace/bin/python" -m pip install -e "$HOME/.openclaw/src/mempalace"
```

**Pin chromadb** to a tested range:

```bash
"$HOME/.openclaw/venvs/mempalace/bin/python" -m pip install 'chromadb>=0.4.0,<1.0.0'
```

---

## Step 8: Symlink CLI into PATH

```bash
mkdir -p "$HOME/.local/bin"
ln -sf "$HOME/.openclaw/venvs/mempalace/bin/mempalace" "$HOME/.local/bin/mempalace"
```

---

## Step 9: Verify Installation

```bash
# Check package is installed
"$HOME/.openclaw/venvs/mempalace/bin/python" -m pip show mempalace

# Check module loads
"$HOME/.openclaw/venvs/mempalace/bin/python" -c 'import mempalace; print(mempalace.__file__)'

# Check CLI binary exists
ls -la "$HOME/.openclaw/venvs/mempalace/bin/" | grep mempalace || true

# Check skill exists at chosen location
ls "$SKILL_DIR/SKILL.md"
```

---

## Step 10: Validate Commands

```bash
# CLI help
"$HOME/.openclaw/venvs/mempalace/bin/mempalace" --help

# MCP server (optional — for future MCP integration)
"$HOME/.openclaw/venvs/mempalace/bin/python" -m mempalace.mcp_server --help
```

---

## Post-Install Checklist

- [ ] `SKILL_ROOT` was chosen correctly
- [ ] `SKILL_DIR` exists with `SKILL.md`
- [ ] `~/.openclaw/src/mempalace/` exists (upstream clone)
- [ ] `~/.openclaw/venvs/mempalace/` exists (virtualenv)
- [ ] `mempalace --help` works from PATH
- [ ] `~/.openclaw/mempalace/` directory exists
- [ ] `~/.openclaw/mempalace-sources/curated/` directory exists
- [ ] `skills.load.extraDirs` was updated if using a non-default skill root

---

## Next Step

Tell the agent:

> Set up MemPalace retrieval. Read the installed `SETUP.md` in the `mempalace-retrieval` skill directory and follow every step.

If both install and setup need to happen:

> Install and set up MemPalace retrieval. Read the installed `INSTALL.md` first, then follow `SETUP.md`.

---

## Important Alignment Notes

- The install location of the skill is **operator-chosen**.
- The setup process should **discover the skill location dynamically** rather than assume a single hardcoded workspace path.
- If the skill is installed through `extraDirs`, OpenClaw should be pointed at the parent skill root, not a higher-level repo root that relies on undocumented recursive discovery.
- The runtime MemPalace paths remain fixed by design:
  - `~/.openclaw/mempalace/`
  - `~/.openclaw/mempalace-sources/curated/`
- Only the **skill install path** is dynamic.

