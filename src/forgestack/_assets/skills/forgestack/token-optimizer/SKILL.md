---
name: forgestack-token-optimizer
description: Reduce excessive ForgeStack context or tool output while preserving exact verification evidence.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

# Token Optimizer Sub-skill

Reduce unnecessary token/context consumption without sacrificing correctness. This is an optional adaptive capability.

**1. Reduce at Source:** Narrow searches and bound tool output first. Detect optional tooling like RTK or Caveman only when further savings are useful; do not auto-install.
**2. Choose by Workload:**
   - Prefer tool-output reducers (RTK) for noisy shell/search/git output.
   - Prefer response compression (Caveman) for chatty manager responses, large summaries, or human inboxes.
**3. Exactness Matters:** Avoid aggressive compression for precise errors, security reviews, diagnostics, diffs, acceptance criteria, migrations. Prefer raw evidence.
**4. Adaptive Behavior:** Use when expected savings are meaningful. Skip for small outputs. Do not silently change permanent global integration without approval.
**5. Integration:** Verify RTK integration for specific agents dynamically. Use concise, readable prose by default; compression tooling is optional.
**6. Avoid Stacking:** Do not blindly stack RTK + Caveman + Manager summaries. Multiple layers allowed only if evidence is preserved.
**7. Budgeting:** Load only relevant skills, files, and tasks. Keep decisions, file pointers, blockers, and next steps across long tasks. Retrieve exact evidence when a summary is insufficient. Measure task quality, time, retries, and context use before claiming an optimization.
