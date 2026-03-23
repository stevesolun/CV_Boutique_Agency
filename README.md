# CV Boutique Agency — Claude Code Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-204%20passed-brightgreen)](boutique-resume-agency/tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](boutique-resume-agency/tests/)

If you use or adapt this project, a credit or link back to this repository is appreciated — see [Citation / credit](#citation--credit).

A top-tier boutique resume agency skill for Claude Code. Acts as a panel of eight expert reviewers — AI veteran, HR specialist, founder, business operator, devil's advocate, creative reframer, QC lead, and hallucination detector — to build, critique, rewrite, and quality-control resumes until they reach 8.5+ quality with zero hallucinated claims. Final output includes a send-ready `.docx`.

---

## What this skill does

### Core capability
The skill orchestrates a virtual agency panel that interviews you, drafts your resume section by section, challenges every claim, scores the result using a weighted multi-expert model, and iterates until the resume passes the stop conditions (overall score ≥ 8.5, no critical blocker flags, user acceptance).

### Three operating modes

**Mode 1 — Build from scratch**
Starts with a structured intake (language → target industry → role/seniority → geography/company stage), builds the expert panel, then works through your resume section by section: header, summary, achievements, experience, education, skills. Each section is drafted, QC-reviewed, scored, and refined before moving on.

**Mode 2 — Uploaded resume critique**
Paste or upload your existing resume. The skill detects it, asks only for missing targeting context, then delivers a full executive verdict: strengths, weaknesses, per-section scores, critical blocker flags, and an exact fix list. You then choose to rewrite, rebuild, or tailor.

**Mode 3 — Fast mode**
Ask only the minimum blocking questions, run the full agency process behind the scenes, enforce all QA and hallucination controls, and deliver the strongest possible result with minimal back-and-forth.

### Expert panel
**Mandatory (always active):**
1. AI veteran
2. HR / recruiter specialist
3. Founder / entrepreneur
4. Business leader / operator
5. Devil's advocate
6. Brainstorm / creative reframer
7. Quality-control lead
8. Hallucination detector

**Context-dependent additions** (spawned by the CEO as context reveals the need):
- Domain expert + industry-specific reviewer (when industry is provided)
- Language / localization expert (when language ≠ English)
- ATS specialist (corporate / large org targets)
- Executive branding expert (director+ / C-suite / partner roles)

When Claude Code agent teams are enabled, each of these experts runs as a **real independent Claude instance** — own context window, own task, direct inter-expert messaging. See [Agent teams architecture](#agent-teams-architecture-experimental) below.

### Scoring model
Each expert scores independently. A weighted overall score is computed. The skill also maintains internal per-section scores and tracks critical blocker flags. It stops only when all three stop conditions are met: score ≥ 8.5, zero blockers, user acceptance.

| Score range | Meaning |
|-------------|---------|
| 0 – 3       | Weak / non-competitive |
| 4 – 6       | Usable but weak |
| 7 – 8.4     | Strong with clear issues |
| 8.5 – 8.9   | Send-ready strong |
| 9.0 – 9.4   | Must-call quality |
| 9.5+        | Exceptional (rare) |

### Hard rules
- No hallucinated claims — ever
- No unsupported percentages or metrics
- No fake or inflated seniority
- No generic self-praise without evidence
- No sugarcoating — if something is weak, the panel will say so
- Memory (`workspace/memory.json`) and progress (`workspace/progress.json`) are updated at every stage

### Final output bundle
- Final resume (formatted text)
- Panel report (per-expert verdicts)
- Scorecard (per-section + weighted overall)
- Rewrite / action plan
- Downloadable `.docx`

**Optional extras:** tailored variants, LinkedIn summary, cover letter starter, interview talking points

**Fun epilogue:** once your resume is delivered, the agency offers to channel a famous figure from your industry (or a historical wildcard) for a 3–4 sentence in-character reaction to your resume — Elon Musk, Warren Buffett, Marie Curie, Sun Tzu, and more. Purely for fun; zero effect on the resume or scores.

---

## Repository layout

```
CV_Boutique_Agency/
  CLAUDE.md                    # Wires skill to this project
  README.md                    # This file
  requirements.txt             # Python dependency (python-docx)
  .gitignore
  .claude-plugin/              # Marketplace catalog (plugin distribution)
    marketplace.json
  boutique-resume-agency/      # Plugin folder
    .claude-plugin/
      plugin.json              # Plugin manifest
    skills/
      boutique-resume-agency/
        SKILL.md               # Main skill file with YAML frontmatter
    scripts/
      resume_agency_helpers.py # Panel building, weighted scoring, length checks
      memory_manager.py        # Load/save memory.json and progress.json
      docx_export.py           # DOCX export via python-docx
      _file_utils.py           # Shared atomic JSON write utility
    tests/
      test_resume_agency_helpers.py # 204 pytest tests across 4 files, 100% coverage
      test_e2e.py
      test_docx_export.py
      test_memory_manager.py
    references/
      templates.md             # Intake + critique + output templates
      scoring_rubric.md        # Score scale, blocker flags, pass criteria
      memory_progress_spec.md  # JSON schemas for memory and progress files
      example_flows.md         # Step-by-step example flows for each path
  workspace/
    memory.json                # Persistent session memory
    progress.json              # Stage tracking and scores
    outputs/                   # Generated .docx files land here
```

---

## Installation

Choose the setup that fits you:

| Option | Who it's for | Time |
|--------|-------------|------|
| [Plugin (one command)](#install-as-a-plugin-one-command) | Claude Code users — quickest start | 30 sec |
| [Local clone](#install-locally-clone-the-repo) | Claude Code users — want full control | 5 min |
| [Claude.ai Project](#use-in-claudeai-no-claude-code-needed) | No Claude Code — using Claude desktop or browser app | 5 min |

---

## Install as a plugin (one command)

If this repo is public on GitHub, anyone can install the skill directly from Claude Code:

```
/plugin marketplace add stevesolun/CV_Boutique_Agency
/plugin install boutique-resume-agency@cv-boutique-agency
```

That's it — no cloning, no pip install needed to get the skill. Python (`python -m pip install python-docx`) is only needed if you want DOCX export.

---

## Install locally (clone the repo)

### Prerequisites
- [Claude Code](https://claude.ai/code) installed and running
- Python 3.9+ (only needed for DOCX export)

### Step 1 — Clone or download the repo

```bash
git clone https://github.com/stevesolun/CV_Boutique_Agency
cd CV_Boutique_Agency
```

Or download and extract the ZIP, then open the folder.

### Step 2 — Install the Python dependency

The DOCX export function requires `python-docx`. Install it once:

```bash
python -m pip install python-docx
```

> **Why `python -m pip` and not `pip`?** On machines with multiple Python versions, bare `pip` may target a different interpreter than `python`. Using `python -m pip` ensures both commands hit the same installation.

To verify:
```bash
python -c "from docx import Document; print('python-docx OK')"
```

### Step 3 — Open the project in Claude Code

Open the `CV_Boutique_Agency` folder in Claude Code. Claude Code automatically reads `CLAUDE.md` on project open and activates the boutique resume agency skill.

You do not need to manually load any files. The skill is ready to use immediately.

### Step 4 — Verify workspace files

The `workspace/` folder ships with initialized `memory.json` and `progress.json`. Confirm they exist:

```bash
cat workspace/memory.json
cat workspace/progress.json
```

If either file is missing, regenerate defaults:

```bash
python -c "
import sys, json, pathlib
sys.path.insert(0, 'boutique-resume-agency/scripts')
from memory_manager import DEFAULT_MEMORY, DEFAULT_PROGRESS
pathlib.Path('workspace/memory.json').write_text(json.dumps(DEFAULT_MEMORY, indent=2))
pathlib.Path('workspace/progress.json').write_text(json.dumps(DEFAULT_PROGRESS, indent=2))
print('workspace files restored')
"
```

---

## Use in Claude.ai (no Claude Code needed)

No terminal, no install. The full expert panel, scoring model, intake flows, and resume length research all work inside a **Claude Project** on claude.ai — on any device (Windows, Mac, Linux, browser).

### What works in Claude.ai

| Feature | Works? | Notes |
|---------|--------|-------|
| Expert panel (all 8 experts) | ✅ | Full panel runs in conversation |
| Build from scratch (Path A) | ✅ | Section by section |
| Upload / critique resume (Path B) | ✅ | Paste your resume into the chat |
| Scoring model | ✅ | Per-expert + weighted overall |
| Hallucination detection | ✅ | All hard blocks enforced |
| Resume length research | ✅ | Claude.ai can search the web |
| Fast mode | ✅ | Say `fast mode` as normal |
| Memory / progress persistence | ⚠️ | State lives in the conversation only — not persisted across sessions |
| DOCX export (auto) | ⚠️ | Requires manual script run (see below) |
| Python script execution (auto) | ❌ | No file system access |

### Setup — Claude Project (5 minutes)

**Step 1 — Create a new Project**

Go to [claude.ai](https://claude.ai) → **Projects** → **New Project**. Give it a name like "CV Boutique Agency".

**Step 2 — Set the skill as Project Instructions**

Open the Project → **Instructions** → paste the full contents of [`boutique-resume-agency/skills/boutique-resume-agency/SKILL.md`](boutique-resume-agency/skills/boutique-resume-agency/SKILL.md) into the instructions field.

The agency will activate automatically for every conversation in this Project.

**Step 3 — Upload the reference files**

Upload these files to the Project's knowledge base (drag and drop):

- `boutique-resume-agency/references/templates.md`
- `boutique-resume-agency/references/scoring_rubric.md`
- `boutique-resume-agency/references/example_flows.md`
- `boutique-resume-agency/references/memory_progress_spec.md`

**Step 4 — Start a conversation**

Use the same trigger phrases as Claude Code. The agency activates immediately.

### DOCX export in Claude.ai

Claude.ai cannot execute Python directly, but you have two options:

**Option A — Copy-paste into Word / Google Docs**

When the resume reaches 8.5+, ask:
```
Format the final resume for copy-paste into Microsoft Word.
```
Claude will produce clean, structured text you can paste directly.

**Option B — Run the export script manually**

Ask Claude to produce the `resume_data` dict, then run it yourself:
```
Give me the resume_data dict for docx_export.py.
```
Then locally:
```bash
cd CV_Boutique_Agency
python -c "
import sys; sys.path.insert(0, 'boutique-resume-agency/scripts')
from docx_export import export_resume_to_docx
resume_data = { ... }  # paste dict from Claude
export_resume_to_docx(resume_data, 'workspace/outputs/my_resume.docx')
"
```

### Session memory in Claude.ai

Memory doesn't auto-persist between conversations. To continue a session:

1. At the end of a session, ask: `Give me the current memory.json and progress.json state.`
2. Claude will output the JSON.
3. At the start of your next session, paste it back: `Here's my previous session state: [paste JSON]`

---

## Usage

### Mode reference

| Mode | How to activate | What happens |
|------|----------------|--------------|
| **Tier 1 — Simulation** (default) | Just start a session — no config needed | CEO simulates all 8+ experts in one context window. Works on Claude.ai, Claude Code, any subscription tier. |
| **Tier 2 — Agent teams** (experimental) | Enable `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json + Claude Code v2.1.32+ | Every expert runs as a real independent Claude instance with its own context. See [Agent teams architecture](#agent-teams-architecture-experimental). |
| **Fast mode** | Say `fast mode` or type `/fast` in the conversation | Skips non-critical intake questions. Full agency logic runs behind the scenes. All QA and hallucination controls still enforced. |
| **Interactive mode** (default) | No phrase needed, or say `interactive mode` | One section at a time, full back-and-forth with the panel. |
| **Build from scratch** | `build my resume` | Full intake → section-by-section build → score → export |
| **Critique / rewrite** | Paste resume + `critique my resume` | Executive verdict, per-section scores, fix list |
| **Tailor to JD** | `tailor my resume for this JD:` + paste JD | Gap analysis, fit score, tailored version |

### Toggling fast mode

Say `fast mode` or type `/fast` at any point in the session (or prefix the session opener: `fast mode. build my resume`). These are skill trigger phrases — say them in the conversation, not as top-level CLI commands.

Fast mode skips geography, company stage, and other optional intake questions. The agency asks only the minimum blocking questions (language, path, industry/role) and then works autonomously.

To return to interactive mode, say `interactive mode` or `standard mode`.

### Toggling Tier 2 (agent teams)

See [Tier 2 setup](#tier-2-setup-claude-code) in the Agent teams section. To disable, remove `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` from `settings.json` — the agency falls back to Tier 1 simulation automatically with no change to the user experience.

---

### Start a session

Tell Claude Code (or Claude.ai with a Project) any of the following:

```
Build my resume from scratch.
```
```
I have my current resume here. Critique it.
```
```
Fast mode. Make this resume must-call quality.
```
```
Tailor my resume for this job description: [paste JD]
```
```
Push this resume to 9+ if realistically possible.
```

### Recommended trigger phrases

| Goal | Phrase |
|------|--------|
| Build from scratch | `build my resume`, `resume from scratch` |
| Critique existing | `critique my resume`, `resume critique` |
| Full rewrite | `rewrite my resume` |
| Role-specific tailoring | `tailor my resume` |
| Minimal questions | `fast mode resume` |
| Activate explicitly | `boutique resume agency` |

### Export to DOCX

Once the resume reaches 8.5+ and you accept it, Claude Code will call `docx_export.py` and save the file to `workspace/outputs/`. You can also request it explicitly:

```
Export the final resume to DOCX.
```

---

## Troubleshooting

**DOCX export fails with `ModuleNotFoundError`**
`python-docx` is not installed. Run `python -m pip install python-docx` and retry. Use `python -m pip` (not bare `pip`) to ensure the package is installed for the same Python interpreter Claude Code is using.

**Skill not activating**
Confirm you opened the `CV_Boutique_Agency` folder (not a parent folder) in Claude Code so that `CLAUDE.md` is loaded.

**Score stuck below 8.5 after multiple iterations**
There are unresolved critical blocker flags. Review `boutique-resume-agency/references/scoring_rubric.md` for the full blocker flag list. Address each flag explicitly before re-scoring.

**Memory or progress file corrupted**
Delete the affected file and let the skill regenerate it, or run the restore script in Step 4 above.

---

## Agent teams architecture (experimental)

The boutique resume agency uses a two-tier execution model. The expert panel, scoring, hallucination detection, and context-dependent expert additions are identical in both tiers — only the execution model differs.

### Two-tier overview

| | Tier 1 — Simulation (default) | Tier 2 — Agent teams (experimental) |
|-|-------------------------------|--------------------------------------|
| **Works on** | Claude.ai, Claude Code, any tier — zero config | Claude Code v2.1.32+ with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| **Execution model** | CEO simulates all experts in one context window | Every expert is a real independent Claude instance |
| **Context-dependent experts** | ✅ CEO adds them via simulation as context reveals the need | ✅ CEO spawns real subagents on-the-fly with full context |
| **Scoring / QC / hallucination detection** | ✅ Identical logic | ✅ Identical logic |
| **Expert-to-expert messaging** | Simulated by CEO | Real direct inter-expert messages |
| **Token cost** | Single context window | Scales with active experts (8–13 instances) |
| **Session announcement** | "Running in agency simulation mode…" | No announcement — normal operation |

Both tiers share the same stop conditions, scoring weights, blocker flags, and export flow.

### Tier 2 setup (Claude Code)

**Step 1 — Verify Claude Code version**

```bash
claude --version   # must be v2.1.32+
```

**Step 2 — Enable agent teams**

```json
// settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**Step 3 — Start a session as normal.** The CEO runs the full Tier 2 flow automatically — no special trigger phrase needed.

The "experimental" label is honest: the Claude Code agent teams API itself is experimental. The skill's architecture and protocols are production-ready.

### How Tier 2 works

**Session start:** CEO spawns all 8 mandatory core experts. Each expert receives a full spawn prompt with persona, scope, input contract (session context + task object), and required JSON output format.

**Wave execution per review cycle:**
- **Wave 1 (parallel):** AI Veteran, HR Specialist, Founder, Business Operator, Domain Expert (if active), ATS Specialist (if active)
- **Wave 2 (after Wave 1):** Devil's Advocate, Creative Reframer
- **Wave 3 (after Wave 2):** QC Lead, Hallucination Detector

**Context-dependent experts:** When intake reveals a specific industry, senior role, non-English language, or high-norm sector, the CEO generates a full tailored spawn prompt and spawns the specialist as a real subagent at that moment.

**Synthesis:** CEO reads all expert return contracts, runs `weighted_score()`, promotes any `HARD_BLOCK:` flag (Hallucination Detector) to a confirmed blocker regardless of other scores, and presents the panel verdict.

**Error / timeout:** Expert timeout = 90 seconds. On timeout, CEO marks status `error`, redistributes that expert's weight across remaining experts via normalization, and continues. Hallucination Detector failure blocks export entirely until resolved.

### Full production spec

Complete spawn prompts (one per expert, ~15 lines each), input/return contract JSON schemas, and error-handling protocol are defined in [`SKILL.md`](boutique-resume-agency/skills/boutique-resume-agency/SKILL.md) under "Agent teams architecture".

### Windows / VS Code note

In-process mode (default) works on Windows and in VS Code's integrated terminal. Split-pane mode requires tmux or iTerm2 and is not available in VS Code. Use Shift+Down to cycle between active expert sessions.

---

## Score targets quick reference

| Target | Score | Meaning |
|--------|-------|---------|
| Minimum to stop | 8.5+ | Send-ready |
| Strong target | 9.0+ | Must-call quality |
| Exceptional | 9.5+ | Rare — only when evidence fully supports it |

---

## Citation / credit

This project is released under the [MIT License](LICENSE). You are free to use, adapt, and redistribute it. If you use or build on this work, a credit or link back is appreciated but not legally required.

**Suggested citation format:**

```
Solun, S. (2025). CV Boutique Agency — Claude Code Skill [Software].
GitHub. https://github.com/stevesolun/CV_Boutique_Agency
```

**BibTeX:**

```bibtex
@software{solun2025cvboutique,
  author    = {Solun, Steve},
  title     = {{CV Boutique Agency} — Claude Code Skill},
  year      = {2025},
  publisher = {GitHub},
  url       = {https://github.com/stevesolun/CV_Boutique_Agency}
}
```
