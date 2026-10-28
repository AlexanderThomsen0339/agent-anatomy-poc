---
name: evaluation
description: THIS IS THE PROCESS FOR PROCESSING PROMPTS AND ANALYZING THEM, DETERMINING WHICH STATE, NODES AND EDGES (terminology borrowed from langgraph) ARE TO BE USED WHEN GIVING END-USERS A RESPONSE.
---

# How we evaluate what to do next
1. State Definition
We start by defining our State, which represents the current condition of the codebase and its recent history:
Target Environment Branch:
Pull and inspect the latest changes on dev if the end-user's query pertains to the staging or testing environment.
Pull and inspect main (or master) if the query pertains to the production environment.
Constraint: Do not account for or analyze any changes on local or feature branches.

2. Nodes & Conditional Flow (Execution Sequence)
The agent executes the following node graph, using conditional branching to determine the routing path:
- Node 1: Initial Prompt Analysis
Action: Analyze the incoming user prompt to identify which specific software module is being referenced or targeted.
Conditional Edge (Router):
If module is successfully identified: Route directly to Node 3.
If module cannot be identified: Route to Node 2.
- Node 2: Contribution Scan (Fallback Node)
Action: Scan the repository's latest contributions (focusing on the last month) to inspect all source files that were affected, added, modified, or deleted.
Outcome: Analyze file paths and changes to resolve and determine the target module, then proceed to Node 3.
- Node 3: Retrieve Testing Protocols
Action: Locate the testing protocol file associated with the determined module (located in the RAG folder under the data subfolder).
Outcome: Scan and parse the retrieved testing protocol, then proceed to Node 4.
- Node 4: Evaluate User Story & Test Case Conflicts
Action: Cross-reference the developer's latest contributions against the module's user stories and test cases.
Outcome: Identify which specific user stories or test cases are potentially in conflict or impacted by the code changes, then proceed to Node 5.
- Node 5: Knowledge Enrichment (Wiki Docs)
Action: Retrieve and scan additional wiki documentation to gather supplementary context, specifications, or edge cases.
Outcome: Use this enriched knowledge base to compute, refine, and finalize your evaluation results.

3. Edges & Graph Transitions
For the edges governing your journey and graph traversal, rely on your internal tool-calling capabilities and conditional logic handlers to move seamlessly between nodes, evaluate states, and compute the final response.