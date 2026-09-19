# Platform Ops backlog

## Advanced troubleshooting assistant

**Status:** Backlog. Authentication and role separation ship first.

Build a more capable troubleshooting assistant while keeping the public service within free Cloudflare allowances.

Acceptance criteria:

- Use a server-side model through Cloudflare Workers AI; no provider key or privileged token reaches browser code.
- Retrieve from published Platform Ops and Srivan Technologies content before generating an answer.
- Cite the exact internal pages used, distinguish sourced facts from inference, and say when the corpus does not support an answer.
- Use live Google/web search only as a clearly labelled secondary source where policy and free-tier limits allow it.
- Prefer diagnostic questions, commands, expected output, and rollback-safe steps over generic explanations.
- Preserve the current browser-only retrieval assistant as a zero-cost fallback when AI quota is exhausted or unavailable.
- Add abuse controls, input limits, prompt-injection defenses, request logging without sensitive command output, and daily quota enforcement.
- Keep the public knowledge base readable without an account; reserve saved history or personalization for authenticated users.
