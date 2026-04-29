# FQ Research Agent — User Guide

## What it does

You give it a research brief. It does the desk research and writes the report.

It handles two kinds of work:

- **Market intelligence** — competitive landscapes, market sizing, channel maps, buyer analysis. Fast, commercial.
- **Systematic review** — rigorous literature-based evidence reviews with scenario analysis. For strategic futures and evidence-led strategic intelligence.

The mode is set in the brief, not picked by you at run time.

## What you need to start

1. **A brief** — written using the FQ brief template. If you don't have one yet, copy `templates/brief-template.md` from the repo (or ask Steve) and fill it in. It takes about 30 minutes to write a good brief.
2. **(Optional) Pre-loaded documents** — purchased reports (IBISWorld, ESOMAR, etc.), client-supplied data, prior FQ work on the topic. These anchor the research. The agent reads them first and uses web search only for the gaps. If you have them, drop them in Box at the engagement's `Research Agent/[brief-name]/` folder before you start.

## How to run it

1. Open claude.ai (Fifth Quadrant workspace).
2. Start a new chat.
3. Drag the brief into the chat (DOCX or markdown), or paste it, or give the Box path to it.
4. Type: *"Run research on this brief"*
5. Confirm the brief details when the agent reads them back to you.
6. Wait. Status updates appear as each phase completes (search → extract → synthesise → scenarios if applicable → report). Typical run time: 20–40 minutes for market intelligence; 60–90 minutes for systematic review.
7. The final report appears as a downloadable DOCX in the chat. A copy is also saved to Box.

## Where outputs land

Box, at `[Engagement folder]/Research Agent/[brief-name]/`.

For example, the Valvoline Power Gen brief saves to:
`3. Proposals/FY 2026/Valvoline Power Gen/Research Agent/valvoline-power-gen/`

Inside that folder, you'll find:

| File | What it is |
| ---- | ---------- |
| `00-brief.md` | The brief the agent worked from |
| `01-search-log.md` | Every query it ran and which sources it included or excluded |
| `02-source-list.md` | All included sources with quality / relevance ratings |
| `03-extracts/` | One file per source — what the agent extracted from each |
| `04-synthesis.md` | The structured synthesis |
| `05-scenarios.md` | Three scenarios + competitive moat analysis (if scenarios were run) |
| `06-report.md` | The final report (markdown master) |
| `06-report.docx` | The final report (Word — this is the deliverable) |

You can review any intermediate file if you want to see how a finding was reached.

## Iterating

If the report misses something or you want to push a section further, tell the agent in the same chat:

- *"Re-run the synthesis with more weight on the data centre segment."*
- *"Add a Bullish Case scenario where the Cummins partnership accelerates."*
- *"Tighten the executive summary to half a page."*

The agent re-runs only the affected phases and updates the Box files in place.

## What to do before handing the report to a client

The agent's report is high quality but not client-ready out of the box. Before you send anything externally:

1. **Read it.** All of it.
2. **Spot-check three or four citations.** Open the source from `02-source-list.md`, find the figure in the document, confirm it matches what the synthesis says. The agent doesn't fabricate but extraction errors do happen.
3. **Sense-check the recommendations.** They should specify what to do, when, and what success looks like. If any feel woolly, ask the agent to redo them ("rewrite recommendation 3 with a specific timeframe").
4. **Apply FQ branding.** The DOCX uses the FQ template but check headers, footers, and the cover slide.
5. **Add any client-specific framing** the agent doesn't have visibility into — internal politics, prior conversations, things you can't put in the brief.

## What it can and can't do

**Can:**
- Read pre-loaded documents and extract structured findings.
- Run web searches and assess source quality.
- Synthesise findings across many sources, including reconciling contradictions.
- Build PRISMA-aligned methodology trails for systematic reviews.
- Develop three-scenario futures with explicit, falsifiable assumptions.
- Produce competitive moat analyses.
- Write reports in either commercial or evidence-based academic-adjacent tone.

**Can't:**
- Run primary research (qualitative interviews, surveys). Where the desk research can't answer something, the report flags it as a gap and suggests primary research priorities.
- Read paywalled content the FQ subscriptions don't cover. If a key source is paywalled, drop the report or PDF in Box first as a pre-loaded document.
- Replace your judgment. The agent surfaces evidence and produces well-structured outputs; you're still the one signing off on the recommendations.

## Common pitfalls

- **Brief is too vague** → outputs are too vague. Spend the 30 minutes writing a sharp brief.
- **Pre-loaded documents not in Box yet** → agent uses only web search and the report misses the depth those documents would have provided. Drop them in Box *before* starting the run.
- **Asking for too narrow a scope** → thin evidence, lots of "data gap" flags. Either widen the scope in the brief or accept the gaps and plan primary research.
- **Skipping the spot-check** → an extraction error makes it into the client report. Always spot-check.

## Help

Stuck? Talk to Steve (snuttall@fifthquadrant.com.au) or check the README.md for technical detail.
