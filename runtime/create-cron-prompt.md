# MemPalace — One-Time Cron Creation

This prompt is executed **once** to create the recurring MemPalace maintenance cron.
After execution, this file is not used again — the cron runs `runtime/mempalace-sync-mine.md` directly.

---

## Rules

- Run this prompt exactly once.
- Do not embed maintenance logic here.
- Do not leave `SKILL_ROOT` or any placeholder literal in the created cron payload.
- Replace all path references with resolved absolute paths before creating the cron.
- Do not improvise. Follow every step in order.

---

## Step 1: Resolve SKILL_ROOT

This file lives inside `runtime/`. The skill root is the parent directory.

```
SKILL_ROOT = <absolute path of the parent directory of runtime/>
```

Verify it:

```bash
ls "$SKILL_ROOT/SKILL.md"
```

If the file does not exist, stop. The skill is not installed correctly.

---

## Step 2: Verify mempalace-sync-mine.md Exists

```bash
ls "$SKILL_ROOT/runtime/mempalace-sync-mine.md"
```

If the file does not exist, stop. Run SETUP.md first or verify the skill installation.

---

## Step 3: Resolve Absolute Path

Resolve the full absolute path to the recurring maintenance prompt:

```
SYNC_MINE_PATH = <resolved absolute path to $SKILL_ROOT/runtime/mempalace-sync-mine.md>
```

This path will be baked into the cron payload. It must be a fully resolved absolute path —
no `~`, no `$SKILL_ROOT`, no `$HOME`, no placeholders.

Example (your resolved path will differ):

```
/home/user/.openclaw/workspace/skills/mempalace-retrieval/runtime/mempalace-sync-mine.md
```

---

## Step 4: Create the Recurring Cron

Use the platform's cron creation mechanism (OpenClaw cron add or equivalent agent-side cron creation flow).

### Cron Parameters

| Parameter | Value |
|-----------|-------|
| Name | `MemPalace sync+mine` |
| Schedule | `0 5,11,17,23 * * *` |
| Timezone | `Asia/Manila` |
| Session | `isolated` |
| Delivery | internal / no-deliver |

### Cron Payload

Use the resolved `SYNC_MINE_PATH` (from Step 3) in the payload.
Do NOT use `$SKILL_ROOT` or any variable — use the actual resolved path.

```
Run MemPalace sync+mine.
Read <SYNC_MINE_PATH> and follow every step strictly.
Working directory: the workspace root.
```

Where `<SYNC_MINE_PATH>` is replaced with the actual absolute path before cron creation.

### Example (illustrative — your paths will differ)

```bash
openclaw cron add \
  --name "MemPalace sync+mine" \
  --cron "0 5,11,17,23 * * *" \
  --tz "Asia/Manila" \
  --session isolated \
  --no-deliver \
  --message "Run MemPalace sync+mine.
Read /home/user/.openclaw/workspace/skills/mempalace-retrieval/runtime/mempalace-sync-mine.md and follow every step strictly.
Working directory: the workspace root."
```

---

## Step 5: Verify Cron Was Created

Confirm the cron exists and the payload contains the correct absolute path.

```bash
openclaw cron list
```

Check that:
- The name matches `MemPalace sync+mine`
- The schedule is `0 5,11,17,23 * * *`
- The payload references the absolute path to `runtime/mempalace-sync-mine.md`
- No placeholder literals (`SKILL_ROOT`, `$HOME`, `~`) appear in the payload

---

## Anti-Patterns

Do NOT:
- Embed the full sync/mine/status command sequence in the cron payload
- Leave variable names or placeholders in the cron payload
- Use this file as the recurring runtime prompt — that is `runtime/mempalace-sync-mine.md`
- Run this prompt more than once (it creates a duplicate cron)
- Hardcode any skill path assumption — resolve from this file's location

---

## Context

This cron runs **after** Auto-Dream and does not replace it:

| System | Schedule | Purpose |
|--------|----------|---------|
| memory-core | `0 3 * * *` | Canonical promotion |
| Auto-Dream | `30 4,10,16,22 * * *` | Reflective consolidation |
| **MemPalace** | `0 5,11,17,23 * * *` | Curated sync + mine |

MemPalace remains a **read-only Layer 3 retrieval overlay**.
