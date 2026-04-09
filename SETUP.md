# MemPalace Retrieval — First-Time Setup

Agent-run first-time configuration for MemPalace as a read-only retrieval layer.
Follow every step in order.

**Prerequisites (must be complete before this runs):**
- MemPalace installed and callable (`mempalace --help` works)
- Skill repo at `~/.openclaw/workspace/skills/mempalace-retrieval/`
- Directories created per [INSTALL.md](INSTALL.md)
- At least one memory surface exists (MEMORY.md or LTMEMORY.md)

---

## Step 0: Confirm Prerequisites

Verify the installation is ready:

```bash
# MemPalace CLI works
mempalace --help

# Skill repo exists
ls skills/mempalace-retrieval/SKILL.md

# Runtime directories exist
ls -d ~/.openclaw/mempalace/
ls -d ~/.openclaw/mempalace-sources/curated/
```

If any of these fail, follow [INSTALL.md](INSTALL.md) first.

---

## Step 1: Select Agent Profile

**Check for pre-selected profile first:**

If the environment variable `MEMPALACE_PROFILE` is set, use that value without prompting:

```bash
# Non-interactive (fleet rollout / automation)
export MEMPALACE_PROFILE=business-employee
# or
export MEMPALACE_PROFILE=personal-assistant
```

If `MEMPALACE_PROFILE` is not set, **ask the operator which profile to use:**

| Profile | File | Best for |
|---------|------|----------|
| `business-employee` | `profiles/business-employee.md` | RBAC agents, team workflows, project management |
| `personal-assistant` | `profiles/personal-assistant.md` | Home automation, butler, family companion |

Read the selected profile to understand the recommended wing taxonomy and wake-up priorities.

**This choice is persisted in Step 3.** It determines wake-up priorities and retrieval guidance.
The live phase-one default wing remains `agent_memory` regardless of profile.
Multi-wing profile-specific runtime is future work.

---

## Step 2: Create Runtime Directories

```bash
mkdir -p ~/.openclaw/mempalace/{palace,agents,diaries,exports,cache}
```

---

## Step 3: Create Configuration Files

### 3a. Create `config.json`

```bash
cat > ~/.openclaw/mempalace/config.json << EOF
{
  "palace_path": "$HOME/.openclaw/mempalace/palace",
  "collection_name": "mempalace_drawers"
}
EOF
```

### 3b. Create `wing_config.json`

Persist the profile selection from Step 1. If `MEMPALACE_PROFILE` is set, use its value
to select the correct template below without prompting.

**For business-employee profile** (`MEMPALACE_PROFILE=business-employee`):

```bash
cat > ~/.openclaw/mempalace/wing_config.json << 'EOF'
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
cat > ~/.openclaw/mempalace/wing_config.json << 'EOF'
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

### 3c. Create `identity.txt`

```bash
cat > ~/.openclaw/mempalace/identity.txt << 'EOF'
I am an AI agent running on OpenClaw. I use MemPalace for relation-aware
memory retrieval, timeline queries, and wake-up context. My canonical memory
lives in MEMORY.md (native memory-core) and LTMEMORY.md (Auto-Dream).
MemPalace is my read-only retrieval overlay.
EOF
```

---

## Step 4: Sync Curated Sources

Copy workspace memory surfaces to the curated mirror:

```bash
python3 skills/mempalace-retrieval/scripts/sync_curated.py
```

Verify output shows synced files. If LTMEMORY.md doesn't exist yet
(Auto-Dream hasn't run), that's fine — MEMORY.md alone is enough to start.

---

## Step 5: Initialize Palace

Initialize MemPalace against the curated sources to prepare the palace structure:

```bash
mempalace init ~/.openclaw/mempalace-sources/curated/ \
  --palace ~/.openclaw/mempalace/palace --yes
```

This prepares the palace structure from the curated content.

---

## Step 6: Mine Curated Sources

Index the curated memory into MemPalace's ChromaDB:

```bash
python3 skills/mempalace-retrieval/scripts/mine_curated.py
```

---

## Step 7: Verify Installation

```bash
python3 skills/mempalace-retrieval/scripts/status.py
```

Expected output:
- Palace directory exists
- `config.json` and `wing_config.json` present
- At least one curated source synced
- Palace status shows indexed drawers

---

## Step 8: Test Retrieval

Search:

```bash
python3 skills/mempalace-retrieval/scripts/search.py --query "preferences"
```

Wake-up:

```bash
python3 skills/mempalace-retrieval/scripts/wakeup.py
```

---

## Step 9: Set Up Sync Cron

MemPalace sync + mine runs as a **deterministic system cron**, staggered after Auto-Dream:

| System | Schedule | Runs at | Purpose |
|--------|----------|---------|---------|
| memory-core | `0 3 * * *` | 3:00 AM | Canonical promotion |
| Auto-Dream | `30 4,10,16,22 * * *` | 4:30 / 10:30 / 16:30 / 22:30 | Reflective consolidation |
| **MemPalace** | `0 5,11,17,23 * * *` | **5:00 / 11:00 / 17:00 / 23:00** | Curated sync + mine |

Add to system crontab. Replace `<AGENT_HOME>` with the actual home directory
(e.g. `/home/mia`):

```bash
# MemPalace curated sync + mine (runs after Auto-Dream)
# Uses venv python, absolute paths, flock to prevent overlap, status after mine
SHELL=/bin/bash
HOME=<AGENT_HOME>

0 5,11,17,23 * * * /usr/bin/flock -n <AGENT_HOME>/.openclaw/mempalace/cache/sync.lock /bin/bash -lc '\
  <AGENT_HOME>/.openclaw/venvs/mempalace/bin/python <AGENT_HOME>/.openclaw/workspace/skills/mempalace-retrieval/scripts/sync_curated.py && \
  <AGENT_HOME>/.openclaw/venvs/mempalace/bin/python <AGENT_HOME>/.openclaw/workspace/skills/mempalace-retrieval/scripts/mine_curated.py && \
  <AGENT_HOME>/.openclaw/venvs/mempalace/bin/python <AGENT_HOME>/.openclaw/workspace/skills/mempalace-retrieval/scripts/status.py \
' >> <AGENT_HOME>/.openclaw/mempalace/cache/sync.log 2>&1
```

Why this form:

- **Absolute paths** — cron PATH is sparse; `~` and relative paths are unreliable
- **Venv python** — ties execution to the same environment as the installed MemPalace CLI
- **flock** — prevents overlapping runs if a previous cycle is still running
- **status after mine** — gives a post-run health snapshot in the log

---

## Post-Setup Checklist

- [ ] Profile selected and `wing_config.json` created
- [ ] `~/.openclaw/mempalace/palace/` exists with ChromaDB data
- [ ] `~/.openclaw/mempalace/config.json` exists with correct palace_path
- [ ] `~/.openclaw/mempalace/wing_config.json` exists with correct profile
- [ ] `~/.openclaw/mempalace/identity.txt` exists
- [ ] `~/.openclaw/mempalace-sources/curated/` has at least MEMORY.md
- [ ] `mempalace status --palace ~/.openclaw/mempalace/palace` shows indexed content
- [ ] Search returns results
- [ ] Wake-up generates context
- [ ] Sync cron is scheduled

---

## What's NOT Set Up Yet

The following features are not enabled in this initial deployment:

- Conversation mining (`convos/` stays empty)
- Multi-wing mining (curated content mines into `agent_memory`; profile-specific wing routing is a future enhancement)
- Specialist agent diaries
- AAAK compression
- Knowledge graph queries
- Auto-save hooks
- Direct drawer creation
- Write-back into workspace memory

The selected profile is persisted for metadata, wake-up priorities, and retrieval guidance.
The live phase-one default wing remains `agent_memory`. Multi-wing profile-specific
runtime will be added when curated ingestion and retrieval are proven stable.

## Cleanup
- [ ] .git
- [ ] LICENSE
- [ ] README.md
- [ ] INSTALL.md
- [ ] SETUP.md
- [ ] profiles
