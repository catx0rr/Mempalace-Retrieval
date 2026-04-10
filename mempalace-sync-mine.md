# MemPalace Scheduled Maintenance — Sync + Mine + Status

This is the **recurring hybrid maintenance prompt** for MemPalace.
It is executed by cron on schedule `0 5,11,17,23 * * *`, after Auto-Dream.

This prompt orchestrates the deterministic worker scripts.
It does not contain the maintenance logic itself — the scripts do the work.

---

## Rules

You MUST follow these rules exactly:

- Do not improvise.
- Do not search for alternatives.
- Do not rewrite paths.
- Do not skip steps.
- Do not substitute raw `mempalace` CLI commands for wrapper scripts.
- Do not casually summarize to the user.
- Run each command in order and **stop on first failure**.
- This is internal maintenance, not an analysis task.

---

## Step 1: Resolve SKILL_ROOT

This file's own directory is the skill root.

```
SKILL_ROOT = <absolute path of the directory containing this file>
SCRIPTS_DIR = $SKILL_ROOT/scripts
```

Do not hardcode the skill path. Resolve it from this file's location.

---

## Step 2: Resolve the Authoritative Python Interpreter

Read `~/.openclaw/mempalace/config.json` and extract the `venv_python` field.

```bash
VENV_PYTHON=$(python3 -c "
import json, os
cfg_path = os.path.expanduser('~/.openclaw/mempalace/config.json')
with open(cfg_path) as f:
    cfg = json.load(f)
print(cfg.get('venv_python', os.path.expanduser('~/.openclaw/venvs/mempalace/bin/python')))
")
```

If `venv_python` is not present in config.json, fall back to:

```
~/.openclaw/venvs/mempalace/bin/python
```

Also read the profile and default wing from `~/.openclaw/mempalace/wing_config.json` for the report:

```bash
PROFILE=$(python3 -c "
import json, os
cfg_path = os.path.expanduser('~/.openclaw/mempalace/wing_config.json')
with open(cfg_path) as f:
    cfg = json.load(f)
print(cfg.get('profile', 'unknown'))
")

DEFAULT_WING=$(python3 -c "
import json, os
cfg_path = os.path.expanduser('~/.openclaw/mempalace/wing_config.json')
with open(cfg_path) as f:
    cfg = json.load(f)
print(cfg.get('default_wing', 'agent_memory'))
")
```

---

## Step 3: Run sync_curated.py

```bash
$VENV_PYTHON $SCRIPTS_DIR/sync_curated.py
```

Parse the JSON output. Check the `ok` field.

- If `ok: true` — record sync results and proceed to Step 4.
- If `ok: false` — **stop immediately**. Record the error and skip to Step 6 (report).

Extract from the sync output:
- `synced_count`
- `skipped_count`
- `error_count`
- `errors` (if any)

---

## Step 4: Run mine_curated.py

Only run this step if Step 3 succeeded.

```bash
$VENV_PYTHON $SCRIPTS_DIR/mine_curated.py
```

Parse the JSON output. Check the `ok` field.

- If `ok: true` — record mine results and proceed to Step 5.
- If `ok: false` — **stop immediately**. Record the error and skip to Step 6 (report).

Extract from the mine output:
- `available_count`
- `palace` (path)
- `wing`
- `mine_results` (warnings if any)

---

## Step 5: Run status.py

Only run this step if Steps 3 and 4 both succeeded.

```bash
$VENV_PYTHON $SCRIPTS_DIR/status.py
```

Parse the JSON output. Extract:
- `ok`
- `config_ready`
- `curated_ready`
- `palace_ready`
- `retrieval_ready`
- `profile`

---

## Step 6: Compose the Maintenance Report

Using the outputs from Steps 3–5, compose the following structured report.
Use this template exactly. Fill in the values from the script outputs.
If a stage was skipped due to earlier failure, mark it as `skipped`.

```
🧠 MemPalace Sync+Mine Status
━━━━━━━━━━━━━━━━━━
✅ Final: success | ❌ Final: failed at <stage>
🕒 Run window: <current UTC timestamp>
📂 Profile: <PROFILE>
🪽 Default wing: <DEFAULT_WING>
━━━━━━━━━━━━━━━━━━

🔄 Sync stage
• Result: ok|failed
• Files copied/updated: <synced_count>
• Files unchanged/skipped: <skipped_count>
• Errors: <error_count>
• Source surfaces: MEMORY.md, LTMEMORY.md, procedures.md, episodes/*
• Notes: <warnings or errors if any, otherwise "none">

⛏️ Mine stage
• Result: ok|failed|skipped
• Available sources mined: <available_count>
• Palace target: <palace path>
• Wing used: <wing>
• Notes: <warnings if any, otherwise "none">

📊 Palace status
• Result: ok|failed|skipped
• Config: <config_ready → ok|missing>
• Curated mirror: <curated_ready → healthy|degraded>
• Palace store: <palace_ready → healthy|degraded>
• Retrieval readiness: <retrieval_ready → ready|not ready>

━━━━━━━━━━━━━━━━━━
💡 Insight: <one-line operational observation based on the data>
⚠️ Follow-up: <only if a stage failed or readiness is degraded, otherwise omit>
```

Do not improvise the report format. Do not add extra sections. Do not casually summarize.

---

## Anti-Patterns

Do NOT:
- Run `mempalace mine`, `mempalace status`, or any raw MemPalace CLI command directly
- Substitute the wrapper scripts with raw commands
- Guess paths — always use the resolved SKILL_ROOT and VENV_PYTHON
- Skip the report even if all stages succeed
- Add conversational commentary outside the report format
- Rewrite this prompt or modify its steps during execution
