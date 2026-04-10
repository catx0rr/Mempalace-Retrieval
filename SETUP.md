# MemPalace Retrieval — First-Time Setup

Agent-run first-time configuration for MemPalace as a read-only retrieval layer.
Follow every step in order.

**Prerequisites (must be complete before this runs):**
- MemPalace installed and callable (`mempalace --help` works)
- The `mempalace-retrieval` skill is installed somewhere in the agent’s skill roots
- Directories created per [INSTALL.md](INSTALL.md)
- At least one memory surface exists (`MEMORY.md` or `LTMEMORY.md`)

This setup must **not** assume the skill lives only under:

- `~/.openclaw/workspace/skills/mempalace-retrieval/`

The skill may instead be loaded from:
- `~/.openclaw/workspace/skills/`
- `~/.openclaw/workspace/.agents/skills/`
- `~/.agents/skills/`
- `~/.openclaw/skills/`
- any configured `skills.load.extraDirs`

---

## Step 0: Discover the Skill Location

Before running setup, determine where the `mempalace-retrieval` skill is actually installed.

### 0a. Try standard skill roots first

```bash
for root in \
  "$HOME/.openclaw/workspace/skills" \
  "$HOME/.openclaw/workspace/.agents/skills" \
  "$HOME/.agents/skills" \
  "$HOME/.openclaw/skills"
do
  if [ -f "$root/mempalace-retrieval/SKILL.md" ]; then
    export SKILL_ROOT="$root/mempalace-retrieval"
    break
  fi
done
```

### 0b. If not found, check configured `extraDirs`

```bash
if [ -z "${SKILL_ROOT:-}" ]; then
  python3 - <<'PY'
import json, os, subprocess, sys

HOME = os.path.expanduser("~")
WORKSPACE = os.path.join(HOME, ".openclaw", "workspace")

def normalize_root(root: str) -> str:
    root = os.path.expanduser(root)
    if os.path.isabs(root):
        return root
    return os.path.normpath(os.path.join(WORKSPACE, root))

try:
    raw = subprocess.check_output(
        ["openclaw", "config", "get", "skills.load.extraDirs", "--json"],
        text=True
    ).strip()
    extra_dirs = json.loads(raw) if raw else []
except Exception:
    extra_dirs = []

for root in extra_dirs:
    normalized = normalize_root(root)
    candidate = os.path.join(normalized, "mempalace-retrieval", "SKILL.md")
    if os.path.isfile(candidate):
        print(os.path.dirname(candidate))
        sys.exit(0)

sys.exit(1)
PY
fi
```

If the Python check prints a path, export it:

```bash
export SKILL_ROOT="<PASTE_OUTPUT_HERE>"
```

### 0c. Fail if still unresolved

```bash
if [ -z "${SKILL_ROOT:-}" ] || [ ! -f "$SKILL_ROOT/SKILL.md" ]; then
  echo "Could not locate mempalace-retrieval skill directory."
  echo "Install the skill first or ensure skills.load.extraDirs includes its parent root."
  exit 1
fi

export SCRIPTS_DIR="$SKILL_ROOT/scripts"
echo "Using SKILL_ROOT=$SKILL_ROOT"
echo "Using SCRIPTS_DIR=$SCRIPTS_DIR"
```

---

## Step 1: Confirm Prerequisites

Verify the installation is ready:

```bash
# MemPalace CLI works
mempalace --help

# Skill repo exists
ls "$SKILL_ROOT/SKILL.md"

# Scripts exist
ls "$SCRIPTS_DIR/sync_curated.py"
ls "$SCRIPTS_DIR/mine_curated.py"
ls "$SCRIPTS_DIR/status.py"
ls "$SCRIPTS_DIR/search.py"
ls "$SCRIPTS_DIR/wakeup.py"

# Runtime directories exist
ls -d "$HOME/.openclaw/mempalace/" || true
ls -d "$HOME/.openclaw/mempalace-sources/curated/" || true
```

If any of these fail, follow [INSTALL.md](INSTALL.md) first.

---

## Step 2: Select Agent Profile

**Check for pre-selected profile first:**

If the environment variable `MEMPALACE_PROFILE` is set, use that value without prompting:

```bash
# Non-interactive (fleet rollout / automation)
export MEMPALACE_PROFILE=business-employee
# or
export MEMPALACE_PROFILE=personal-assistant
```

If `MEMPALACE_PROFILE` is not set, ask the operator which profile to use:

| Profile | File | Best for |
|---------|------|----------|
| `business-employee` | `profiles/business-employee.md` | RBAC agents, team workflows, project management |
| `personal-assistant` | `profiles/personal-assistant.md` | Home automation, butler, family companion |

Read the selected profile to understand the recommended wing taxonomy and wake-up priorities.

This choice is persisted in Step 4.
It determines wake-up priorities and retrieval guidance.

The live phase-one default wing remains `agent_memory` regardless of profile.
Multi-wing profile-specific runtime is future work.

---

## Step 3: Create Runtime Directories

```bash
mkdir -p "$HOME/.openclaw/mempalace"/{palace,agents,diaries,exports,cache}
mkdir -p "$HOME/.openclaw/mempalace-sources/curated"
```

---

## Step 4: Create Configuration Files

### 4a. Create `config.json`

```bash
cat > "$HOME/.openclaw/mempalace/config.json" << EOF
{
  "palace_path": "$HOME/.openclaw/mempalace/palace",
  "collection_name": "mempalace_drawers",
  "venv_python": "$HOME/.openclaw/venvs/mempalace/bin/python",
  "curated_dir": "$HOME/.openclaw/mempalace-sources/curated"
}
EOF
```

### 4b. Create `wing_config.json`

Persist the profile selection from Step 2.

**For business-employee profile** (`MEMPALACE_PROFILE=business-employee`):

```bash
cat > "$HOME/.openclaw/mempalace/wing_config.json" << 'EOF'
{
  "profile": "business-employee",
  "default_wing": "agent_memory",
  "wing_taxonomy": [
    "agent_memory",
    "general",
    "project_<slug>",
    "team_<slug>",
    "person_<slug>",
    "client_<slug>",
    "department_<slug>",
    "domain_<slug>"
  ],
  "wake_up_priorities": [
    "active project context",
    "team structure",
    "client state",
    "pending actions"
  ]
}
EOF
```

**For personal-assistant profile** (`MEMPALACE_PROFILE=personal-assistant`):

```bash
cat > "$HOME/.openclaw/mempalace/wing_config.json" << 'EOF'
{
  "profile": "personal-assistant",
  "default_wing": "agent_memory",
  "wing_taxonomy": [
    "agent_memory",
    "general",
    "household",
    "person_<slug>",
    "device_<slug>",
    "location_<slug>",
    "routine_<slug>",
    "service_<slug>",
    "domain_<slug>"
  ],
  "wake_up_priorities": [
    "household state",
    "active routines",
    "person context",
    "device state",
    "pending tasks"
  ]
}
EOF
```

### 4c. Create `identity.txt`

Read the agent’s `IDENTITY.md` and replace `<AGENT_NAME>` with the real name.

```bash
cat > "$HOME/.openclaw/mempalace/identity.txt" << 'EOF'
I am <AGENT_NAME> running on this system. I use MemPalace for relation-aware
memory retrieval, timeline queries, and wake-up context. My canonical memory
lives in MEMORY.md (native memory-core) and LTMEMORY.md (Auto-Dream).
MemPalace is my read-only retrieval overlay.
EOF
```

---

## Step 5: Sync Curated Sources

Copy workspace memory surfaces to the curated mirror:

```bash
python3 "$SCRIPTS_DIR/sync_curated.py"
```

Verify output shows synced files.

If `LTMEMORY.md` does not exist yet, that is acceptable.
`MEMORY.md` alone is enough to begin.

---

## Step 6: Initialize Palace

Initialize MemPalace against the curated sources:

```bash
mempalace --palace "$HOME/.openclaw/mempalace/palace" init \
  "$HOME/.openclaw/mempalace-sources/curated/" --yes
```

This prepares the palace structure from the curated content.

---

## Step 7: Mine Curated Sources

Index the curated memory into MemPalace’s ChromaDB:

```bash
python3 "$SCRIPTS_DIR/mine_curated.py"
```

---

## Step 8: Verify Installation

```bash
python3 "$SCRIPTS_DIR/status.py"
```

Expected output:
- palace directory exists
- `config.json` and `wing_config.json` present
- at least one curated source synced
- palace status shows indexed drawers

---

## Step 9: Test Retrieval

### Search

```bash
python3 "$SCRIPTS_DIR/search.py" --query "preferences"
```

### Wake-up

```bash
python3 "$SCRIPTS_DIR/wakeup.py"
```

---

## Step 10: Set Up Scheduled Maintenance

MemPalace sync + mine runs as a deterministic scheduled task, staggered after Auto-Dream:

| System | Schedule | Runs at | Purpose |
|--------|----------|---------|---------|
| memory-core | `0 3 * * *` | 3:00 AM | Canonical promotion |
| Auto-Dream | `30 4,10,16,22 * * *` | 4:30 / 10:30 / 16:30 / 22:30 | Reflective consolidation |
| **MemPalace** | `0 5,11,17,23 * * *` | **5:00 / 11:00 / 17:00 / 23:00** | Curated sync + mine |

Resolve this skill directory as `SKILL_ROOT`, then read and execute:

```
$SKILL_ROOT/runtime/create-cron-prompt.md
```

This is a **one-time task** that creates the recurring cron.
The cron delegates all maintenance logic to `runtime/mempalace-sync-mine.md`.

Do not embed the full maintenance command sequence here.
Do not create the cron inline — use the dedicated cron creation prompt.

---

## Post-Setup Checklist

- [ ] `SKILL_ROOT` was resolved correctly
- [ ] `SCRIPTS_DIR` (`$SKILL_ROOT/scripts`) was resolved correctly
- [ ] Profile selected and `wing_config.json` created
- [ ] `~/.openclaw/mempalace/palace/` exists with ChromaDB data
- [ ] `~/.openclaw/mempalace/config.json` exists with correct palace path, venv_python, and curated_dir
- [ ] `~/.openclaw/mempalace/wing_config.json` exists with correct profile
- [ ] `~/.openclaw/mempalace/identity.txt` exists
- [ ] `~/.openclaw/mempalace-sources/curated/` has at least `MEMORY.md`
- [ ] `mempalace status --palace ~/.openclaw/mempalace/palace` shows indexed content
- [ ] Search returns results
- [ ] Wake-up generates context
- [ ] Gateway cron is scheduled

---

## What’s NOT Set Up Yet

The following features are not enabled in this initial deployment:

- conversation mining (`convos/` stays empty)
- multi-wing mining (curated content mines into `agent_memory`; profile-specific wing routing is future enhancement)
- specialist agent diaries
- AAAK compression
- knowledge graph queries
- auto-save hooks
- direct drawer creation
- write-back into workspace memory

The selected profile is persisted for metadata, wake-up priorities, and retrieval guidance.
The live phase-one default wing remains `agent_memory`.
Multi-wing profile-specific runtime will be added later, after curated ingestion and retrieval are proven stable.

---

## Cleanup

These are optional cleanup targets if the copied skill repo includes development-only files that should not remain in the deployed skill directory:

- [ ] `.git`
- [ ] `LICENSE`
- [ ] `README.md`
- [ ] `INSTALL.md`
- [ ] `SETUP.md`
- [ ] `profiles/`

Do not remove:
- `SKILL.md`
- `scripts/`
