# Adversarial: MCP path escape

## Setup
MCP `kubrick_do` with `intent=compile` and `--out` pointing outside `KUBRICK_PROJECT_DIR`.

## Expect
- Tool result `isError: true`
- `structuredContent.code == MCP_ARG_POLICY`
- No file written outside the project root

## Covered by
`scripts/test_io_safety.py::test_mcp_server_policy_rejection`
