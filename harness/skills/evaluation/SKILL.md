---
name: evaluation
description: The process for a code check. Describes it as a node graph (the langgraph analogy: state, nodes, edges) so every other skill can say exactly which part of it they implement.
---

# How we evaluate a code check

This is the root process. It is not a checklist you execute yourself, line by line — `code-review` already
implements it concretely, step by step, with the exact tool calls to make. Read this first so you know *why*
those steps exist and in what order, then follow `code-review`.

## State

The code you are checking: which branch, at which commit, and its newest commits with their diffs.
This is resolved and handed to you automatically, before you take your first step — you never choose a branch
yourself, and there is no tool to do so. The commits you see are always on `dev` or `main`, never a local or
feature branch: a developer's own branch is not part of this tool's job.

## Nodes (what each step decides)

1. **Initial Prompt Analysis** — Read the user's question and decide which module (area — e.g. Regninger,
   Profil, Overblik, or the user story/feature it names) it is about.
   - Module identified → go to node 3.
   - Module not identified → go to node 2.
2. **Contribution Scan (fallback)** — Look at the newest commits (already shown to you, or fetched with
   `list_recent_changes`) to see which files and features they touch, and use that to resolve the module.
   Then go to node 3.
3. **Retrieve Testing Protocols** — Find the user story and its test cases with `search_requirements` (and
   `list_requirements` if the question is broad, e.g. "which tests are there").
4. **Evaluate Conflicts** — Read the actual code (`list_code_files`, `read_code_file`) and cross-reference it
   against the acceptance criteria and against how the team is supposed to code. Give each requirement a
   status and each architecture deviation a `RISK` line. This is the result everything downstream is built on.

## Edges

Moving between nodes is just calling the next tool the current node needs — there is no separate mechanism
for it. A gate is never skipped by guessing instead of calling the tool it depends on.

## Downstream of this graph

This graph produces one assessment, shared by every reader. What happens to it afterward is a presentation
step, not part of the evaluation itself, and must never add, remove or re-score a finding:
- `audience-it` rewrites it for a developer.
- `audience-product` rewrites it for a non-technical reader.
