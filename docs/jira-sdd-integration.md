# Jira + Spec-Driven Development: Integration Discussion

## Context

The team collaborates with BizOps directors to identify and prioritize high-value use cases. That collaboration needs to produce durable, agreed-to artifacts that are resilient to scope creep. Jira is also required for CAPEX cost accounting.

The tension: Jira tickets are poor containers for precise specifications. Spec-driven development (SDD) in git produces tamper-evident, reviewable contracts — but lives outside the PM workflow.

---

## The Core Problem

Agreed-to specifications are more resilient to scope creep than Jira tickets because:

- A spec with `SHALL` statements and explicit scenarios creates a clear, reviewable contract
- A Jira ticket's acceptance criteria is prose — easy to quietly edit, easy to interpret loosely, with no version history anyone actually reads
- Git-native specs are PR-reviewable and immutable once merged

---

## Source of Truth: Which Direction Does Truth Flow?

### Option A: Jira as Source of Truth
Jira ticket drives SDD proposal/spec generation; tasks sync back as Jira subtasks.

**Pro:** PMs already live there; stakeholder visibility is built in  
**Con:** Jira's text fields are poor containers for structured specs; acceptance criteria tend toward vague prose; you lose git-native, diffable, reviewable specs

### Option B: SDD as Source of Truth
Specs are authored in git; Jira tickets are auto-created/updated from them; Jira used for PM visibility only, not authoring.

**Pro:** Specs stay precise and reviewable; engineers never leave their workflow; Jira becomes a read-only dashboard  
**Con:** PMs cannot easily edit specs; requires discipline not to author in Jira

### Option C: Loose Coupling with Explicit Sync Points (Recommended)
Each tool does what it is good at. Jira tracks portfolio status and CAPEX; SDD captures structured decisions. They reference each other at defined handshake points — not live sync.

**Pro:** No complex bi-directional sync logic; works with the existing archive workflow; each tool optimized for its audience  
**Con:** Two places to look mid-flight; requires process discipline

---

## What "Locked Down" Actually Means

Scope creep resistance comes from combining four properties:

| Property | Tool | Why it matters |
|---|---|---|
| Visibility and CAPEX tracking | Jira ticket exists | Finance and PM can see it |
| Agreed scope | SDD proposal exists | What we committed to build |
| Non-engineering sign-off | BizOps approval on PR | Someone outside eng said yes |
| Tamper-evidence | Spec merged to git | Change requires a new PR |

The key dynamic: if a Jira ticket is quietly edited, the SDD spec is unchanged — the drift is visible. If the spec is changed, it requires a PR — the change is explicit and attributed.

---

## The Collaboration Flow

```
1. BizOps + Eng collaborate
   (meeting, doc, wherever this happens today)
          │
          ▼
2. Engineer authors SDD proposal
   BizOps director reviews GitHub PR
   Merge = approval = locked scope
          │
          ▼
3. Jira epic created (manually or via automation)
   linked to the proposal commit in git
   used only for CAPEX tracking
          │
          ▼
4. Implementation driven by SDD tasks
          │
          ▼
5. SDD archive → post summary comment
   to Jira epic (closes the loop for CAPEX accounting)
```

---

## The Role of the GitHub PR as Approval Artifact

A PR approval on `proposal.md` is a surprisingly strong approval artifact:

- Dated and attributed (who approved, when)
- Immutable once merged
- Diff shows exactly what was agreed to
- Naturally integrates into engineering workflow

**Key question:** Can BizOps directors participate in a GitHub PR review? If yes, the approval workflow is already there. If no, a lighter-weight review surface is needed — which is a UX problem, not a tooling problem.

---

## What CAPEX Accounting Actually Needs

CAPEX tracking typically requires:
- Epic exists with estimates attached
- Tickets closed when work is done
- Rough effort/cost attribution

This is a thin interface. It does **not** require Jira to own the specification — only to record that the work happened and at what cost. The archive step (posting a summary comment back to the Jira epic) is likely sufficient to close this loop.

**Key question:** Does CAPEX accounting need granular Jira data (story points, individual tickets) or epic-level evidence (initiative shipped, here's the cost)? The answer determines how much Jira integration is actually necessary.

---

## Practical Integration Points (Option C in Detail)

Concretely, loose coupling could look like:

- **Propose** — optionally accepts a Jira epic ID, links it in `proposal.md`
- **PR on proposal** — BizOps director approves; merge = locked scope
- **Apply/implement** — optionally pushes tasks as Jira subtasks (one-time, push-only)
- **Archive** — posts a summary comment to the linked Jira epic with change name, shipped capabilities, and link to archived artifacts

The Jira MCP server makes some of this buildable today (create/update issues, post comments).

---

## Open Questions Before Building

1. **Where does BizOps collaboration actually happen today?** If it's Confluence, email, or slide decks — that's where the friction lives, not Jira. The integration won't help if the upstream handoff isn't captured.

2. **Can BizOps directors review a GitHub PR?** Determines whether the existing PR-as-approval pattern works or needs a lighter UX layer.

3. **Granular vs. epic-level CAPEX data?** Determines the minimum viable Jira integration surface.

4. **Who is the signing authority on a proposal?** The approval chain (BizOps director + engineering lead, or one of the two) should be explicit before designing the workflow.

---

## AI-Native SDD Frameworks

Several AI-native frameworks implement spec-driven development and each has a different relationship to Jira. A prototype challenge was proposed to evaluate them against the requirements above.

### Framework Comparison

|  | Spec-Kit | BMAD | GSD | OpenSpec |
|---|---|---|---|---|
| **Philosophy** | Specs are executable, git-native | Agents collaborate with human across phases | Context management for AI coding sessions | Git-native contracts, archive-based |
| **Jira integration** | Deep, drift-aware sync engine | Publish-only, gated on confirmation | Minimal — not core to the framework | Handshake at archive |
| **BizOps collaboration** | PR review (same as OpenSpec) | Workflow discovery phases | Not really designed for this | PR review |
| **Scope creep resistance** | Drift-aware, CI/CD can fail on misalignment | `correct-course` workflow | Phase verification (engineering-internal) | `SHALL` + git diff |
| **Maturity** | Active, community extensions | Active, growing | Active, CLI-heavy | Newer, lean |
| **Best fit** | Spec as contract + Jira sync | Agentic multi-phase collaboration | Long AI coding sessions | Small team, git-native |

### Spec-Kit (github/spec-kit)

The closest philosophical cousin to OpenSpec. Specs live in git as markdown with a clear workflow from specification through task breakdown. Has the most mature Jira integration of the three:

- Community extension `speckit.jira.specstoissues` creates Epics, Stories, and Subtasks directly from specs
- A sync engine described as "idempotent and drift-aware" — detects when Jira and the spec have diverged
- CI/CD integration on the roadmap: specs can fail a PR build if misaligned with implementation
- Also has Linear integration

**For this context:** The strongest fit for the Jira/CAPEX angle. The drift-aware sync is exactly what scope-creep resistance needs. Tradeoff: BizOps participation still requires getting comfortable with PRs.

### BMAD (bmad-code-org/bmad-method)

A more opinionated, agent-heavy framework structured around specialized AI agents for different phases — architecture, sprint planning, QA. The philosophy is collaborative discovery between human and AI.

Jira integration exists but is explicitly framed as a downstream publication step, not a source of truth:

> "Jira epic creation is a team-visible action that initiates sprint-planning signals and should be gated on user confirmation."

The `bmad-correct-course` workflow handles mid-implementation scope changes — which maps to the scope-creep concern.

**For this context:** Interesting if the team wants to lean into an agentic, multi-phase approach. The architecture workflow's "collaborative discovery between architectural peers" could work well for the BizOps collaboration phase. Jira integration is looser than Spec-Kit — a publish step, not a sync engine.

### GSD (open-gsd/gsd-core)

Primarily focused on **execution** — managing context degradation during long AI coding sessions, YOLO vs. interactive modes, plan execution and verification. It has a `discuss → spec → plan → execute → verify` phase loop.

Less about the spec as a durable artifact for stakeholder sign-off and more about the spec as context for the AI agent during implementation. Jira integration does not appear prominently in the framework.

**For this context:** Weakest fit for the BizOps/CAPEX angle. Excellent engineering execution tooling but solves a different problem — keeping AI agents on track during implementation, not locking down requirements with non-engineering stakeholders.

### The Prototype Challenge

The recommendation is to have each solution engineer pick a different framework and build the **same use case** end-to-end:

```
BizOps collaboration → proposal → BizOps sign-off
      → Jira epic → implementation → archive → Jira comment
```

The three questions to answer per framework:

1. **Where does the spec live and who owns it?** All three say git. The difference is who can participate — if BizOps directors can't do PR reviews, none of them solve that problem natively.

2. **How resilient is the spec to drift?** Spec-Kit's CI/CD-fails-if-misaligned is the strongest answer. OpenSpec relies on discipline. BMAD has `correct-course`. GSD has phase verification but it's engineering-internal.

3. **How much does Jira get?** Spec-Kit: structured bidirectional sync. BMAD: post-completion publish. GSD: essentially nothing. OpenSpec: archive comment.

**Horse race prediction:** Spec-Kit vs. BMAD is the most interesting comparison given the governance requirements. GSD worth including but will likely win on execution speed and lose on the compliance/stakeholder angle.

---

## Summary

The right mental model is **attestation, not sync**. Jira and SDD don't need to be the same thing — they need to reference each other cleanly at two moments: when scope is agreed (proposal PR merged → Jira epic created) and when work is done (archive → Jira comment). Everything in between lives in git.

The spec-driven approach is inherently more scope-creep-resistant than Jira tickets because changing a spec requires a PR — a deliberate, attributed, reviewable act — rather than a quiet field edit.

Of the AI-native frameworks evaluated, Spec-Kit has the most production-ready Jira integration. BMAD has the strongest story for the BizOps collaboration phase. The prototype challenge will surface which tradeoffs matter most in practice.
