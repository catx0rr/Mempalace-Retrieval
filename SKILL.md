---
name: mempalace-retrieval
description: "Relation-aware memory retrieval via MemPalace — structured search across wings, rooms, and timelines. Read-only overlay on canonical memory. Use when: question is relation-shaped, timeline-shaped, cross-domain, or wake-up context is needed before answering. Do NOT use for simple fact lookup (use QMD), conversation continuity (use LCM), or exact transcript quotes (use session-retrieval)."
---

# MemPalace Retrieval — Relation / Timeline / Wake-Up Layer

MemPalace is Layer 3 in the retrieval ladder. It provides structured, navigable memory retrieval
using wings (people/projects), rooms (topics), and semantic search over a local ChromaDB index.

**MemPalace does NOT own any canonical memory files.**
It reads from a curated mirror of the agent's memory surfaces.

## Architecture Role

| System | Role | Owns |
|--------|------|------|
| memory-core | Conservative canonical promotion | MEMORY.md |
| Auto-Dream | Reflective consolidation | LTMEMORY.md, procedures, episodes |
| QMD | Semantic retrieval over memory files | (read-only) |
| LCM | Conversation DAG / archive continuity | (read-only) |
| **MemPalace** | **Relation / timeline / wake-up overlay** | **(read-only)** |
| session-retrieval | Raw forensic recovery | (read-only) |
| truth-recovery | Final claim guardrail | control law |

## When to Use MemPalace

Use MemPalace as the preferred retrieval surface when the question is:

- **Relation-shaped** — "how are X and Y connected?", "who is involved in this?"
- **Timeline-shaped** — "what changed over time?", "when did this start?"
- **Cross-domain** — "what bridges these projects/people/topics?"
- **Wake-up worthy** — agent needs scoped context before answering
- **Navigation-shaped** — "what topics exist under this project?"

## When NOT to Use MemPalace

Do NOT use MemPalace first for:

- **Simple facts** — use QMD (searches MEMORY.md / LTMEMORY.md directly)
- **Procedures** — use QMD (searches memory/procedures.md)
- **Conversation continuity** — use LCM / DAG
- **Exact quotes / transcripts** — use session-retrieval
- **Canonical truth verification** — use truth-recovery

## Retrieval Ladder Position

```
1. Visible current context
2. Current session
3. Pasted text
4. Deterministic tool output already in hand
5. QMD — semantic search over curated markdown memory
6. LCM — conversation DAG / archive continuity
7. MemPalace — relation / timeline / wake-up / cross-domain
8. session-retrieval — raw forensic fallback
9. truth-recovery — guardrail before asserting specifics
```

MemPalace retrieval is still memory retrieval. It does not outrank truth discipline.
truth-recovery is the final gate before specific factual output.

## Directory Layout

```
~/.openclaw/mempalace/              # MemPalace runtime state (outside workspace)
├── config.json                     # MemPalace configuration
├── wing_config.json                # Profile selection + default wing + taxonomy + wake-up priorities
├── identity.txt                    # L0 identity (loaded every session)
├── palace/                         # ChromaDB vector store
├── agents/                         # Specialist agent configs (future)
├── diaries/                        # Agent diaries (future)
├── exports/                        # Migration bundles (future)
└── cache/                          # Search cache

~/.openclaw/mempalace-sources/      # Curated input mirror
├── curated/                        # Copies of memory surfaces
│   ├── MEMORY.md
│   ├── LTMEMORY.md
│   ├── procedures.md
│   └── episodes/
├── convos/                         # Conversation exports (future)
└── generated/                      # Generated content (future)
```

**MemPalace never reads from or writes to `~/.openclaw/workspace/` directly.**
It operates on the curated mirror in `~/.openclaw/mempalace-sources/curated/`.

**Raw `memory/YYYY-MM-DD.md` daily files are upstream inputs for consolidation by
memory-core and Auto-Dream. They are not direct MemPalace curated ingest sources.**
MemPalace ingests only the post-consolidation surfaces: MEMORY.md, LTMEMORY.md,
procedures.md, and episodes/.

## Core Files

| File | Purpose | Mutability |
|------|---------|------------|
| `~/.openclaw/mempalace/config.json` | Palace path + collection config | User-editable |
| `~/.openclaw/mempalace/wing_config.json` | Profile selection + default wing + taxonomy metadata + wake-up priorities | Created during setup |
| `~/.openclaw/mempalace/identity.txt` | L0 identity context | User-editable |
| `~/.openclaw/mempalace/palace/` | ChromaDB vector store | Rebuilt by mining |
| `~/.openclaw/mempalace-sources/curated/` | Mirror of workspace memory | Refreshed by sync |

**Config convention note:** `~/.openclaw/mempalace/config.json` is part of the OpenClaw integration
convention. The wrapper scripts pass `--palace` explicitly and do not rely on MemPalace's native
default config location (`~/.mempalace/config.json`). Direct raw CLI usage without `--palace` will
not honor the OpenClaw config path.

## Setup

For operator-level installation, follow [INSTALL.md](INSTALL.md).
For first-time agent configuration, follow [SETUP.md](SETUP.md).

## Operational Cadence

Sync + mine runs as a **deterministic system cron**, staggered after Auto-Dream:

| System | Schedule | Runs at | Purpose |
|--------|----------|---------|---------|
| memory-core | `0 3 * * *` | 3:00 AM | Canonical promotion |
| Auto-Dream | `30 4,10,16,22 * * *` | 4:30 / 10:30 / 16:30 / 22:30 | Reflective consolidation |
| **MemPalace** | `0 5,11,17,23 * * *` | **5:00 / 11:00 / 17:00 / 23:00** | Curated sync + mine |

Auto-Dream writes first → MemPalace ingests the newest structured memory after.
Sync + mine needs no LLM tokens — it is a deterministic file copy + index operation.

**Sync + mine is cron-based. Wake-up is NOT cron-based.**

## Wake-Up Trigger Conditions

Wake-up is **situational, not scheduled**. It fires when the agent needs scoped preloading.

### Use wake-up when:

**A. Session cold start**
- New session, reset session, thin context, recent restart
- Agent has no established anchors yet

**B. Context switch**
- Switching to a different project, person, or domain
- Moving into a workstream the agent hasn't touched this session

**C. Relation/timeline-heavy question**
- "What changed over time?"
- "How are these connected?"
- "What's the story around X?"
- "Load me into Project Y before answering"

**D. On-demand user request**
- "Wake up into project X"
- "Load context for Y"
- "Palace context"

### Do NOT use wake-up:
- On every turn (too noisy)
- On a cron schedule (wrong trigger model)
- When QMD/LCM already anchored the answer

## Wrapper Scripts

All arithmetic, file operations, and subprocess calls are handled by deterministic Python scripts.
The LLM orchestrates — calling scripts, reading their JSON output, then making judgment calls.

| Script | Purpose | When Called |
|--------|---------|-------------|
| `scripts/sync_curated.py` | Copy workspace memory surfaces to curated mirror | Before mining |
| `scripts/mine_curated.py` | Run MemPalace mining against curated mirror | After sync |
| `scripts/search.py` | Structured search with wing/room scoping | Retrieval |
| `scripts/wakeup.py` | Generate scoped wake-up context (L0+L1) | Session start / context preload |
| `scripts/status.py` | Palace health check — wings, rooms, drawer counts | Diagnostics |

### What stays LLM-driven

| Operation | Why |
|-----------|-----|
| Deciding when to use MemPalace | Question-type routing requires judgment |
| Interpreting search results | Understanding relevance, not just ranking |
| Choosing wing/room scope | Context-dependent decision |
| Synthesizing cross-domain results | Connecting dots across wings |

## Usage Flow

### Sync + Mine (cron-driven — 4x daily after Auto-Dream)

```
python3 skills/mempalace-retrieval/scripts/sync_curated.py
                    │
                    ▼
      Copies MEMORY.md, LTMEMORY.md,
      procedures.md, episodes/* to
      ~/.openclaw/mempalace-sources/curated/
      (skips unchanged files)
                    │
                    ▼
python3 skills/mempalace-retrieval/scripts/mine_curated.py
                    │
                    ▼
      Runs mempalace mine against curated mirror
      Updates ChromaDB in ~/.openclaw/mempalace/palace/
```

Schedule: `0 5,11,17,23 * * *` — runs 30 minutes after each Auto-Dream cycle.

### Retrieval (runtime)

```
Question arrives
       │
       ▼
Is the answer already in:
- visible context?
- current session?
- pasted text?
- deterministic tool output already in hand?
       │
       ├── yes → answer from that
       │
       └── no
            │
            ▼
  Is this a simple fact / procedure lookup?
            │
            ├── yes → QMD
            │
            └── no
                 │
                 ▼
  Is this about continuity / what was said / how it unfolded?
                 │
                 ├── yes → LCM
                 │
                 └── no
                      │
                      ▼
  Is this relation / timeline / cross-domain / wake-up?
                      │
                      ├── yes → MemPalace via search.py or wakeup.py
                      │
                      └── no → session-retrieval for raw forensic fallback

After retrieval:
       ▼
truth-recovery gate before specific factual output
```

### Wake-Up (situational — cold start, context switch, or on-demand)

```
Trigger fires (cold start / context switch / relation question / user request)
       │
       ▼
python3 skills/mempalace-retrieval/scripts/wakeup.py [--wing ...]
       │
       ▼
  L0 + L1 context (~600-900 tokens)
  Critical facts, team, projects, preferences
```

Wake-up is NOT cron-based. See "Wake-Up Trigger Conditions" above.

## Manual Triggers

| Command | Action |
|---------|--------|
| "Search palace for X" | Run search.py with query |
| "Palace wake-up" / "Palace context" | Run wakeup.py |
| "Palace status" | Run status.py |
| "Sync and mine palace" | Run sync_curated.py then mine_curated.py |
| "Search palace for X in wing Y" | Run search.py with --wing flag |

## Safety Rules

1. **MemPalace is read-only** — it does not write to workspace memory files
2. **Curated sources are copies** — workspace originals are never modified
3. **MemPalace retrieval does not outrank truth discipline** — results are memory, not verified truth
4. **Do not expose all 19 MCP tools** — use only the governed wrapper scripts
5. **Raw mode only** — do not use AAAK compression in phase one
6. **Do not create drawers directly** — all content enters through curated sync + mine

## Agent Profile Overlays

The core skill is agent-agnostic. Agent-specific wing taxonomies and priorities
live in profile overlays:

| Profile | File | Wing taxonomy |
|---------|------|---------------|
| Business employee | `profiles/business-employee.md` | agent_memory, general, project, team, person, client, department, domain |
| Personal assistant | `profiles/personal-assistant.md` | agent_memory, general, household, person, device, location, routine, service, domain |

The operator selects one profile during setup. The profile defines:
- Preferred wing structure
- Wake-up priorities
- What counts as "important relation" for that agent type
- Profile-specific retrieval examples

## Phase One Boundaries

### Enabled
- Sync curated memory surfaces
- Mine curated sources into palace
- Search with wing/room scoping
- Wake-up context generation with profile-aware priorities
- Status checks with profile reporting

### Not Yet Enabled
- Multi-wing mining (curated content mines into default wing; profile-specific routing is a future enhancement)
- Direct drawer creation/deletion
- Specialist agent diaries
- AAAK compression
- Conversation export mining
- Knowledge graph queries
- Auto-save hooks
- Write-back into workspace memory
- Direct daily note ingestion (`memory/YYYY-MM-DD.md` files are upstream inputs for
  consolidation by memory-core and Auto-Dream, not direct MemPalace curated ingest)

## Reference

- MemPalace repository: https://github.com/milla-jovovich/mempalace
- Palace path: `~/.openclaw/mempalace/palace`
- Config path: `~/.openclaw/mempalace/config.json`
- Curated sources: `~/.openclaw/mempalace-sources/curated/`
