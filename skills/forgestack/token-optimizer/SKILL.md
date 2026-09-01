---
name: forgestack-token-optimizer
description: Adaptive logic to reduce unnecessary token/context consumption.
---

# Token Optimizer Sub-skill

Reduce unnecessary token/context consumption without sacrificing correctness. This is an optional adaptive capability.

**1. Detect Optimizers:** Detect tooling like RTK, Caveman, etc. Do not hard-code or auto-install without approval.
**2. Choose by Workload:**
   - Prefer tool-output reducers (RTK) for noisy shell/search/git output.
   - Prefer response compression (Caveman) for chatty manager responses, large summaries, or human inboxes.
**3. Exactness Matters:** Avoid aggressive compression for precise errors, security reviews, diagnostics, diffs, acceptance criteria, migrations. Prefer raw evidence.
**4. Adaptive Behavior:** Use when expected savings are meaningful. Skip for small outputs. Do not silently change permanent global integration without approval.
**5. Integration:** Verify RTK integration for specific agents dynamically. Prefer light Caveman modes by default for Manager/Inbox.
**6. Avoid Stacking:** Do not blindly stack RTK + Caveman + Manager summaries. Multiple layers allowed only if evidence is preserved.
**7. Budgeting:** Load only relevant skills, files, and tasks. Summarize outputs instead of reading transcripts.
