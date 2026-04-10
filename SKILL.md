---
name: mempalace-retrieval
description: "MemPalace-specific retrieval workflow. Use when the question is relation-shaped, timeline-shaped, cross-domain, navigation-shaped, or wake-up-worthy. Read-only Layer 3 retrieval over curated memory surfaces."
---

# MemPalace Retrieval — Layer 3 Workflow

MemPalace is a **read-only Layer 3 retrieval overlay**.

It is used for:
- relation retrieval
- timeline retrieval
- cross-domain retrieval
- navigation retrieval
- wake-up context preload

---

## What MemPalace is for

Use MemPalace when the question is:

- relation-shaped
- timeline-shaped
- cross-domain
- navigation-shaped
- wake-up-worthy

Examples:
- “how are X and Y connected?”
- “what changed over time?”
- “what bridges these domains?”
- “what topics exist under this project?”
- “load me into this context before answering”

---

## Do NOT use MemPalace first for

- simple facts
- procedures
- stable preferences
- conversation continuity
- exact quote recovery
- final truth verification

Use the global routing skill for that selection.
MemPalace is only one retrieval layer in the stack.

---

## What MemPalace reads

MemPalace does **not** read workspace memory directly.

It reads only the curated mirror:

```text
~/.openclaw/mempalace-sources/curated/
├── MEMORY.md
├── LTMEMORY.md
├── procedures.md
└── episodes/
```

Raw daily notes:

```text
memory/YYYY-MM-DD.md
```

are **not** direct phase-one MemPalace ingest.
They are upstream inputs for memory-core and Auto-Dream.

---

## Runtime store

```text
~/.openclaw/mempalace/
├── config.json
├── wing_config.json
├── identity.txt
├── palace/
└── cache/
```

The searchable MemPalace index is stored in:

```text
~/.openclaw/mempalace/palace/
```

---

## Wrapper scripts

MemPalace is accessed only through these governed wrappers:

- `sync_curated.py`
- `mine_curated.py`
- `search.py`
- `wakeup.py`
- `status.py`

Do not expose raw MemPalace MCP tools for this phase-one setup.

---

## Simple workflow

### A. Sync + Mine

```text
MEMORY.md / LTMEMORY.md / procedures / episodes
  ->
sync_curated.py
  ->
~/.openclaw/mempalace-sources/curated/
  ->
mine_curated.py
  ->
mempalace palace / ChromaDB updated
```

### B. Retrieval

```text
Question is relation / timeline / cross-domain / navigation shaped
  ->
search.py
  ->
MemPalace search
  ->
structured results returned
  ->
memory-retrieval skill decides final answer flow
  ->
truth-recovery before specific factual output
```

### C. Wake-up

```text
Cold start / context switch / wake-up-worthy question
  ->
wakeup.py
  ->
MemPalace wake-up
  ->
L0 + L1 scoped context
  ->
agent answers with better preload
```

---

## Operational cadence

Scheduled MemPalace maintenance is deterministic and delegated to
`mempalace-sync-mine.md`. That prompt runs curated sync, curated mine,
and status checks using wrapper scripts. Do not substitute raw MemPalace
CLI commands for wrapper scripts.

Schedule: `0 5,11,17,23 * * *` (after Auto-Dream).
Wake-up is **not** cron-based.

---

## Profile behavior

Phase one rules:

- default wing remains `agent_memory`
- profile metadata affects guidance and wake-up priorities
- multi-wing profile-specific runtime is future work

Do not pretend live multi-wing runtime exists yet.

---

## Safety rules

1. MemPalace is read-only
2. Curated sources are copies
3. MemPalace does not write workspace memory
4. MemPalace does not outrank truth-recovery
5. Do not use MemPalace for simple facts or procedures first
6. Do not directly ingest raw daily notes in phase one

---

## Phase-one boundaries

### Enabled
- curated sync
- curated mine
- search
- wake-up
- status
- profile-aware metadata guidance

### Not yet enabled
- multi-wing mining
- direct drawer creation
- AAAK compression
- conversation mining
- knowledge graph queries
- auto-save hooks
- write-back into workspace memory
- direct daily note ingestion
