# MemPalace Profile: Personal Assistant / Butler Agent

**Agent type:** Autonomous butler / companion for home automation and personal workflows
**Memory emphasis:** Household routines, family preferences, device state, location context

---

## Wing Taxonomy

| Wing | Type | Purpose |
|------|------|---------|
| `agent_memory` | System | Agent's own operational continuity |
| `general` | Catch-all | Items not yet categorized into a specific wing |
| `household` | Home | Family-wide continuity — shared preferences, house rules, schedules |
| `person_<slug>` | Person | Individual family members, friends, staff, guests, contacts |
| `device_<slug>` | Device | Smart devices — state history, configs, issues |
| `location_<slug>` | Location | Rooms/areas — kitchen, bedroom, garage, office |
| `routine_<slug>` | Routine | Recurring patterns — morning, bedtime, commute, meals |
| `service_<slug>` | Service | External services — doctor, school, bank, utilities, delivery |
| `domain_<slug>` | Expertise | Knowledge areas — home-automation, personal-finance, wellness, travel |

### Wing vs Room distinction

Wings are durable retrieval axes. Rooms are finer topics within a wing.

Example:
```
household/
├── room_schedules
├── room_preferences
├── room_house-rules
└── room_guests

person_<family-member>/
├── room_preferences
├── room_health
├── room_schedule
└── room_communication-style

location_kitchen/
├── room_appliances
├── room_routines
└── room_inventory

routine_morning/
├── room_lighting
├── room_climate
├── room_schedule
└── room_preferences
```

---

## Wake-Up Priorities

For a personal assistant / butler agent, wake-up should prioritize:

1. **Household state** — who's home, what's scheduled, any alerts
2. **Active routines** — time-of-day context, current routine phase
3. **Person context** — preferences of whoever is interacting
4. **Device state** — any devices needing attention, automations active
5. **Pending tasks** — reminders, follow-ups, open requests

### Wake-up trigger emphasis

| Trigger | Priority |
|---------|----------|
| Morning cold start | High — load household + routine + schedule |
| Person arrives home | High — load person preferences + location context |
| Device/automation question | Medium — load device wing |
| Service inquiry | Medium — load service wing |
| General question | Low — QMD is usually sufficient |

---

## Relation Significance

For a personal assistant, "important relation" means:

- **Person-routine links** — who prefers what during which routine
- **Person-device links** — who uses which devices, preferences per person
- **Location-routine links** — what happens where and when
- **Schedule dependencies** — overlapping family schedules, conflicts
- **Service history** — last appointment, next due, provider preferences

---

## Retrieval Examples

| Question | Route | Wing/Room |
|----------|-------|-----------|
| "What's the morning routine for the kids?" | MemPalace | routine_morning + person |
| "When was the last time the AC filter was changed?" | MemPalace | device → room_maintenance |
| "What does the family usually eat on Sundays?" | MemPalace | routine → room_meals |
| "How are the kitchen lights and bedroom alarm connected?" | MemPalace | tunnel between location wings |
| "What's the dentist's phone number?" | QMD | MEMORY.md or procedures.md |
| "What did I ask about the thermostat yesterday?" | LCM / session-retrieval | — |
