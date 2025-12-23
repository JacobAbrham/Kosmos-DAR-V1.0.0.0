# Sprint Delivery Plan

**Audience:** Engineering + product leads coordinating KOSMOS delivery  
**Purpose:** Translate the implementation roadmap into executable two-week sprints without losing the “vertical slice” principle.

---

## 1. Cadence & Ceremonies

- **Sprint length:** 14 days. Day 1 = roadmap-aligned planning; Day 10 = demo; Day 14 = retro + release readiness check.
- **Checkpoints:**  
  1. **Kickoff (Day 1)** — pick deliverables from the roadmap tables that can be finished inside the sprint.  
  2. **Mid-sprint demo (Day 10)** — show a running vertical slice (Docker stack, auth flow, CI job, etc.).  
  3. **Retro (Day 14)** — review burndown against the roadmap success metrics and close the sprint checklist below.

---

## 2. Backlog Shaping

1. **Start from `IMPLEMENTATION_ROADMAP.md`.** Only pull items that appear under the current phase (e.g., Week 1‑2 bootstrap, Week 3‑4 core infra).
2. **Slice vertically.** Each ticket must trace an end-to-end capability (environment setup, auth MVP, CI pipeline) rather than a single layer.
3. **Attach measurable output.** Examples: “`docker compose` stack passes health checks”, “Zitadel SSO demo at `/docs`”, “build workflow publishes coverage badge”.

---

## 3. Definition of Ready

Before a story enters a sprint:

- Teammate has completed the **Immediate Actions** block in `TEAM_CHECKLIST.md` (env synced, new compose command verified).
- Dependencies (env vars, secrets, access) are documented in the ticket.
- Acceptance criteria state which tests/logs/commands will be produced (e.g., `pytest`, `docker compose up`, `curl /health`).

Stories that fail these gates are sent back to backlog grooming.

---

## 4. Definition of Done

Every sprint deliverable must satisfy:

1. **Working Software** — the vertical slice runs locally via `docker compose -f config/environments/development/docker-compose.yml up`.
2. **Automation Hooks** — CI configuration, scripts, or docs are updated alongside the code.
3. **Testing** — at minimum `pytest tests/test_api_health.py -v` and any new targeted tests pass; frontend or infra changes add equivalent checks.
4. **Documentation** — README/roadmap/checklists reflect the new capability.
5. **Demo Artifact** — short video, screenshot, or commands logged in `TASK_JOURNAL.md` to prove the slice works.

---

## 5. Sprint Checklist

Use this quick list at retro time:

| Item | Owner | Status |
|------|-------|--------|
| Selected roadmap deliverables completed? | PM | ☐ |
| `TEAM_CHECKLIST.md` Immediate Actions reconfirmed? | All devs | ☐ |
| Docker stack verified on at least two machines? | DevOps | ☐ |
| Tests + lint (`pytest`, `ruff`, etc.) recorded in task comments? | Feature owners | ☐ |
| Documents updated (README, roadmap, journal)? | Docs lead | ☐ |
| Demo/retro notes added to `TASK_JOURNAL.md`? | PM | ☐ |

---

## 6. Suggested Sprint Flow

1. **Day 0 Prep:** Groom backlog against roadmap tables, ensure stories meet the Definition of Ready.
2. **Day 1 Kickoff:** Commit to 2–3 vertical slices that move the roadmap metrics (env setup, auth, CI, etc.).
3. **Execution:**  
   - Implement code + infra + docs simultaneously.  
   - Keep Docker + pytest green daily.  
   - Update `TASK_JOURNAL.md` with progress notes.
4. **Day 10 Demo:** Showcase the end-to-end feature live (compose stack, API flow, CI run).
5. **Day 14 Retro:** Walk through the sprint checklist, capture carry-overs, and queue the next roadmap slice.

Following this plan keeps every sprint measurable, demo-ready, and anchored to the documented success metrics.
