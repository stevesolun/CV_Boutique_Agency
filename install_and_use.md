# Install and Use Guide

## Part 1: Custom GPT
### Install
1. Create a new custom GPT.
2. Paste `gpt_builder_instructions.md` into the system instructions.
3. Keep `gpt_mega_prompt.md` for portability and testing outside the builder.
4. Use `gpt_conversation_starters.md` as conversation starter ideas.
5. Keep `gpt_internal_workflow_and_rubric.md` as your maintenance and QA reference.

## Part 2: Claude Code skill
### Install
1. Save `claude_code_skill.md` in your project.
2. Save the helper Python modules:
   - `resume_agency_helpers.py`
   - `memory_manager.py`
   - `docx_export.py`
3. Save the support docs:
   - `templates.md`
   - `scoring_rubric.md`
   - `memory_progress_spec.md`
   - `example_flows.md`
4. Make a `workspace/` folder with:
   - `memory.json`
   - `progress.json`
   - `outputs/`

### Python dependencies
```bash
pip install python-docx
```

### Use
Tell Claude Code:
- "Use the boutique resume agency skill."
- "Build from scratch."
- "Critique my uploaded resume."
- "Fast mode."
- "Export the final result to DOCX."
