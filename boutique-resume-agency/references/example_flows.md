# Example Flows

## Flow 1: Build from scratch
1. Ask language
2. Ask path
3. Ask target context
4. Form panel
5. Plan internally
6. Start with header section
7. Move section by section
8. Draft
9. QC
10. Re-score
11. User validation
12. Export-ready final
13. Famous opinion epilogue (optional — offer once after final DOCX is delivered and accepted)

## Flow 2: Uploaded resume critique
1. Detect upload
2. Ask missing target context
3. Form panel
4. Deliver executive verdict
5. Show strengths and weaknesses
6. Score
7. Recommend rewrite / rebuild / tailor
8. Proceed based on user choice
9. Famous opinion epilogue (optional — offer once after final DOCX is delivered and accepted)

## Flow 3: Agent teams mode (full expert panel as real Claude teammates)
Prerequisites: Claude Code v2.1.32+ · `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json
1. CEO spawns 8 mandatory expert teammates at session start
2. CEO runs intake (language, path, industry, role, geography)
3. CEO spawns context-dependent experts on-the-fly as intake answers reveal the need
   (domain expert, ATS specialist, localization expert, executive branding expert, industry reviewer)
4. CEO creates and assigns section review tasks on the shared task list
5. Experts claim and complete assigned tasks; produce structured reports
6. Devil's Advocate challenges other experts' findings via direct inter-expert messages
7. CEO broadcasts completed draft sections to all relevant experts for full review round
8. QC Lead + Hallucination Detector run final pass (always last in each review cycle)
9. CEO synthesizes: weighted score, confirmed blockers, panel report
10. CEO presents verdict to user
11. Iterate on expert feedback until score >= 8.5 + zero blockers
12. User accepts → CEO assigns DOCX export task
13. CEO offers famous opinion epilogue
14. CEO runs team cleanup
