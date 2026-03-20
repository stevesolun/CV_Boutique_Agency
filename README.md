# CV Boutique Agency — Claude Code Skill

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

**Context-dependent additions:**
- Domain expert + industry-specific reviewer (when industry is provided)
- Language / localization expert (when language ≠ English)
- ATS specialist
- Executive branding expert

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

---

## Repository layout

```
CV_Boutique_Agency/
  CLAUDE.md                    # Wires skill to this project
  README.md                    # This file
  install_and_use.md           # Detailed installation guide
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

## Install as a plugin (one command)

If this repo is public on GitHub, anyone can install the skill directly from Claude Code:

```
/plugin marketplace add stevesolun/CV_Boutique_Agency
/plugin install boutique-resume-agency@cv-boutique-agency
```

That's it — no cloning, no pip install needed to get the skill. Python (`pip install python-docx`) is only needed if you want DOCX export.

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
pip install -r requirements.txt
```

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
from boutique-resume-agency.scripts.memory_manager import DEFAULT_MEMORY, DEFAULT_PROGRESS
import json, pathlib
pathlib.Path('workspace/memory.json').write_text(json.dumps(DEFAULT_MEMORY, indent=2))
pathlib.Path('workspace/progress.json').write_text(json.dumps(DEFAULT_PROGRESS, indent=2))
print('workspace files restored')
"
```

---

## Usage

### Start a session

Tell Claude Code any of the following:

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
`python-docx` is not installed. Run `pip install python-docx` and retry.

**Skill not activating**
Confirm you opened the `CV_Boutique_Agency` folder (not a parent folder) in Claude Code so that `CLAUDE.md` is loaded.

**Score stuck below 8.5 after multiple iterations**
There are unresolved critical blocker flags. Review `boutique-resume-agency/references/scoring_rubric.md` for the full blocker flag list. Address each flag explicitly before re-scoring.

**Memory or progress file corrupted**
Delete the affected file and let the skill regenerate it, or run the restore script in Step 4 above.

---

## Score targets quick reference

| Target | Score | Meaning |
|--------|-------|---------|
| Minimum to stop | 8.5+ | Send-ready |
| Strong target | 9.0+ | Must-call quality |
| Exceptional | 9.5+ | Rare — only when evidence fully supports it |
