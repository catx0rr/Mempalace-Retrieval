# MemPalace Profile: Business Employee Agent

**Agent type:** Autonomous employee-level companion for business workflows
**Memory emphasis:** Team structure, project continuity, client relationships, decisions

---

## Wing Taxonomy

| Wing | Type | Purpose |
|------|------|---------|
| `agent_memory` | System | Agent's own operational continuity |
| `general` | Catch-all | Items not yet categorized into a specific wing |
| `project_<slug>` | Project | Per-project memory (milestones, decisions, architecture) |
| `team_<slug>` | Group | Team-level continuity and group dynamics |
| `person_<slug>` | Person | Individual contacts — managers, colleagues, stakeholders |
| `client_<slug>` | Client | Client/customer/account relationships |
| `department_<slug>` | Org | Organizational structure (accounting, HR, ops, sales) |
| `domain_<slug>` | Expertise | Knowledge domains (security, compliance, legal, procurement) |

### Wing vs Room distinction

Wings are durable retrieval axes. Rooms are finer topics within a wing.

Example:
```
project_t5-business-arm/
├── room_auth
├── room_deployment
├── room_pricing
└── room_memory-architecture

person_<manager>/
├── room_preferences
├── room_communication-style
├── room_projects
└── room_relationship-continuity

department_finance/
├── room_budgets
├── room_approvals
├── room_reporting
└── room_compliance
```

---

## Wake-Up Priorities

For a business employee agent, wake-up should prioritize:

1. **Active project context** — current sprint, blockers, recent decisions
2. **Team structure** — who does what, reporting lines, availability
3. **Client state** — last interaction, open commitments, sentiment
4. **Pending actions** — unresolved threads, follow-ups, deadlines

### Wake-up trigger emphasis

| Trigger | Priority |
|---------|----------|
| New workday session | High — load project + team context |
| Project switch | High — load project-specific wing |
| Client meeting prep | High — load client wing |
| Cross-team question | Medium — load relevant department/team wings |
| General question | Low — QMD is usually sufficient |

---

## Relation Significance

For a business agent, "important relation" means:

- **Decision chains** — who decided what, when, and why
- **Accountability links** — who owns which deliverable
- **Escalation paths** — who to involve when blocked
- **Cross-project dependencies** — shared resources, timelines, blockers
- **Client history** — prior commitments, agreements, preferences

---

## Retrieval Examples

| Question | Route | Wing/Room |
|----------|-------|-----------|
| "Who approved the new pricing?" | MemPalace | project → room_pricing |
| "What did the finance team say about Q3?" | MemPalace | department_finance |
| "How are the auth migration and deployment related?" | MemPalace | tunnel between rooms |
| "What's the client's communication preference?" | MemPalace | client → room_preferences |
| "What's our deployment process?" | QMD | procedures.md |
| "What happened in yesterday's standup?" | LCM / session-retrieval | — |
