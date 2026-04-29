# FQ Research Agent

A reusable secondary research agent for Fifth Quadrant. An analyst submits a brief, the agent runs the full research pipeline autonomously, and a structured report comes back.

This repository contains the **agent logic**. Work product (briefs, intermediate outputs, final reports) lives in **Box**.

> **Looking for how to use it?** See [`USER_GUIDE.md`](./USER_GUIDE.md). This README is for whoever deploys and maintains the plugin.

## Architecture

```
fq-research (orchestrator Skill — what users invoke)
  ├─ invokes → research-search-agent       Phase 1: source gathering
  ├─ invokes → research-extract-agent      Phase 2: structured findings per source
  ├─ invokes → research-synthesise-agent   Phase 3: synthesis
  ├─ invokes → research-scenarios-agent    Phase 4: scenarios + moat analysis (when required)
  └─ invokes → research-report-agent       Phase 5: final report
                                           (orchestrator then converts to DOCX via `docx` Skill)
```

The orchestrator is the only thing analysts interact with. Sub-agents run in their own context windows, persist intermediate outputs to Box, and return short structured summaries to the orchestrator.

## Repository layout

```
fq-research-agent/
├── README.md                           ← you are here (technical)
├── USER_GUIDE.md                       ← analyst-facing
├── .claude-plugin/
│   └── plugin.json                     ← plugin manifest
├── skills/
│   └── fq-research/
│       └── SKILL.md                    ← orchestrator skill
├── agents/
│   ├── research-search.md              ← Phase 1 sub-agent
│   ├── research-extract.md             ← Phase 2 sub-agent
│   ├── research-synthesise.md          ← Phase 3 sub-agent
│   ├── research-scenarios.md           ← Phase 4 sub-agent
│   └── research-report.md              ← Phase 5 sub-agent
├── templates/
│   ├── brief-template.md               ← copy this for new briefs
│   └── prisma-checklist.md             ← appendix for systematic-review reports
└── examples/
    ├── valvoline-power-gen.md          ← market-intelligence example
    └── future-of-research-2030.md      ← systematic-review example
```

## Research modes

The brief sets `research_mode`:

| Mode | Use for | Key features |
| ---- | ------- | ------------ |
| `market-intelligence` | Commercial market research, market entry, competitor profiling, channel mapping | Fast (hours to days), structured outputs, no PRISMA |
| `systematic-review` | Strategic futures, evidence-based literature reviews, scenario analysis | PRISMA-aligned methodology, thematic meta-synthesis, scenario analysis required |

## State and outputs

All work product lives in **Box** at:

```
[Engagement folder]/Research Agent/[brief-name]/
├── 00-brief.md
├── 01-search-log.md
├── 02-source-list.md
├── 03-extracts/             (one file per source + index.md)
├── 04-synthesis.md
├── 05-scenarios.md          (only if scenarios required)
├── 06-report.md             (markdown master)
└── 06-report.docx           (final deliverable)
```

For known engagements (e.g. *Valvoline Power Gen* under `3. Proposals/FY 2026/`), outputs go inside the existing engagement folder. Otherwise the orchestrator asks the user where to land them.

The pipeline is resumable. If the orchestrator is asked to redo Phase 3, it reads existing Phase 1 + 2 outputs from Box rather than re-running them.

## Dependencies

- **Box MCP** — connected and authenticated for every team member who will use the agent. Used for reading pre-loaded documents, persisting all phase outputs, and saving the final DOCX. Required.
- **`docx` Skill** — already on the FQ team workspace. Used by the orchestrator's final step to convert the markdown report to a properly formatted FQ Word document.
- **Web tools** — `WebSearch` and `WebFetch` are used by the search and extract sub-agents.

## Deployment to the FQ Team workspace

1. Push this repo to the private FQ GitHub organisation (`fifthquadrant/fq-research-agent`).
2. From the Anthropic admin console (Team plan Owner), import the plugin from the GitHub repo. The manifest at `.claude-plugin/plugin.json` registers one Skill (`fq-research`) and five sub-agents.
3. Set scope: **Team — Fifth Quadrant**. Every team member sees the orchestrator Skill `fq-research` automatically. Sub-agents are invoked internally and don't appear in the user-facing Skill list.
4. Verify the Box MCP and `docx` Skill are enabled in the team workspace.
5. Smoke-test: open claude.ai, attach `examples/valvoline-power-gen.md`, type *"Run research on this brief"*, and confirm the orchestrator triggers and the pipeline runs end to end.

## Versioning

Bump `version` in `.claude-plugin/plugin.json` for any change to agent behaviour. Use semver:

- **Patch** (0.1.0 → 0.1.1): wording fixes, minor instruction tweaks.
- **Minor** (0.1.0 → 0.2.0): new sub-agent, new mode, new output section, new template.
- **Major** (0.x → 1.0): breaking change to the brief format or the Box workspace structure.

## Adding or modifying agents

1. Edit the relevant `.md` file in `skills/` or `agents/`.
2. Bump version in `plugin.json`.
3. Test locally on an example brief before pushing.
4. PR review by another agent author at FQ.
5. After merge, re-import the plugin into the Anthropic console — the Team workspace picks up the new version.

## Adding a new brief

1. Copy `templates/brief-template.md` to a new location (Box recommended; or anywhere convenient).
2. Fill it in. Set `research_mode`. Drop pre-loaded documents in the engagement's `Research Agent/` folder if any.
3. Hand the brief to an analyst — they trigger the agent with *"Run research on this brief"*.

## Quality standards

A recommendation is actionable only if it satisfies all three:

1. Specifies what the organisation should do — not just what findings suggest.
2. Indicates a timeframe or trigger conditions.
3. Identifies what success looks like.

The report sub-agent enforces this gate before finalising. Recommendations that can't be made actionable are dropped, not included.

## Handling data gaps

- **market-intelligence:** the report flags gaps explicitly and notes whether they're fillable through primary research or are genuine voids. Never extrapolate market sizing.
- **systematic-review:** evidential gaps are surfaced prominently as primary research priorities. Hedged language for thin evidence; never confident conclusions.

## Troubleshooting

| Symptom | Likely cause | Fix |
| ------- | ------------ | --- |
| Orchestrator doesn't trigger when user attaches a brief | Skill description not matching the user phrasing | Check `description` in `skills/fq-research/SKILL.md`. Add the phrasing to the trigger list and bump version. |
| Sub-agent reports "couldn't write to Box" | Box MCP not authenticated for that user | User runs Box auth flow. Confirm in admin console. |
| Final DOCX not produced | `docx` Skill not enabled in team workspace | Enable from admin console. |
| Sub-agents are visible in the user's Skills list | Wrong scope on agents | Set agents to internal-only in the admin console. They should only be invoked via the Agent tool by the orchestrator. |

## Contact

Owner: Steve Nuttall (snuttall@fifthquadrant.com.au).
