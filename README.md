# MemPalace Retrieval Skill for OpenClaw

A governed, read-only retrieval layer that integrates [MemPalace](https://github.com/milla-jovovich/mempalace) into the OpenClaw agent memory stack as a **relation / timeline / wake-up overlay**.

MemPalace does not own canonical memory. It reads from a curated mirror of the agent's memory surfaces and provides structured, navigable retrieval using wings, rooms, and semantic search over a local ChromaDB index.

---

## Works With

- It works alongside the default `memory-core` (dreaming) of openclaw
- Works with the fork version of openclaw `auto-dream` 

## Architecture Role

```
memory-core   → canonical promotion        → MEMORY.md
Auto-Dream    → reflective consolidation   → LTMEMORY.md, procedures, episodes
MemPalace     → relation / timeline / wake-up overlay → (read-only)
session-ret.  → raw forensic recovery      → (read-only)
truth-rec.    → final claim guardrail      → control law
```

MemPalace is **Layer 3** in the retrieval ladder. It complements — never replaces — the existing memory systems.

---

## When to Use MemPalace

Use MemPalace when the question is:
- **Relation-shaped** — "how are X and Y connected?"
- **Timeline-shaped** — "what changed over time?"
- **Cross-domain** — "what bridges these projects/people/topics?"
- **Wake-up worthy** — agent needs scoped context before answering

Do NOT use MemPalace for simple facts (QMD), conversation continuity (LCM), or exact quotes (session-retrieval).

---

## Directory Layout

```
~/.openclaw/mempalace/              # Runtime state (outside workspace)
├── config.json
├── wing_config.json
├── identity.txt
├── palace/                         # ChromaDB vector store
├── agents/                         # (future)
├── diaries/                        # (future)
├── exports/                        # (future)
└── cache/

~/.openclaw/mempalace-sources/      # Curated input mirror
├── curated/
│   ├── MEMORY.md
│   ├── LTMEMORY.md
│   ├── procedures.md
│   └── episodes/
├── convos/                         # (future)
└── generated/                      # (future)

~/.openclaw/workspace/skills/mempalace-retrieval/   # This skill
├── SKILL.md                        # Runtime contract
├── INSTALL.md                      # Operator installation guide
├── SETUP.md                        # Agent first-time setup guide
├── README.md                       # This file
├── profiles/
│   ├── business-employee.md        # Business wing taxonomy
│   └── personal-assistant.md       # Personal wing taxonomy
└── scripts/
    ├── sync_curated.py             # Copy workspace memory to curated mirror
    ├── mine_curated.py             # Index curated sources into palace
    ├── search.py                   # Scoped semantic search
    ├── wakeup.py                   # L0+L1 wake-up context
    └── status.py                   # Palace health check
```

---

## Quick Start

**Operator:** Follow [INSTALL.md](INSTALL.md) to install MemPalace and prepare the environment.

**Agent:** Follow [SETUP.md](SETUP.md) for first-time configuration (profile selection, palace init, mining, cron).

See each file for detailed step-by-step instructions.

---

## Operational Cadence

Sync + mine runs on a deterministic system cron, staggered after Auto-Dream:

| System | Schedule | Purpose |
|--------|----------|---------|
| memory-core | `0 3 * * *` | Canonical promotion |
| Auto-Dream | `30 4,10,16,22 * * *` | Reflective consolidation |
| **MemPalace** | `0 5,11,17,23 * * *` | Curated sync + mine |

Wake-up is **not cron-based** — it fires situationally on cold starts, context switches, and relation/timeline-heavy questions.

---

## Agent Profiles

Two profile overlays define wing taxonomy and retrieval priorities per agent type:

| Profile | Wings | Best for |
|---------|-------|----------|
| [Business employee](profiles/business-employee.md) | project, team, person, client, department, domain | RBAC agents, workflow automation |
| [Personal assistant](profiles/personal-assistant.md) | household, person, device, location, routine, service, domain | Home automation, butler companion |

---

## Phase One Boundaries

**Enabled:** curated sync, mining, scoped search, wake-up, status checks.

**Disabled:** direct drawer writes, conversation mining, AAAK compression, knowledge graph queries, auto-save hooks, write-back into workspace memory, direct daily note ingestion (`memory/YYYY-MM-DD.md` files are upstream consolidation inputs, not curated ingest).

MemPalace is **read-only** in phase one.

---

## Dependencies

- Python 3.9+
- `mempalace` (`pip install mempalace`)
- OpenClaw agent with workspace at `~/.openclaw/workspace/`

---

## License

MIT — same as MemPalace upstream.
