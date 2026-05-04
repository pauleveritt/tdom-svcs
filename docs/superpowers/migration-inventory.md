# tdom-svcs Superpowers Migration Inventory

This inventory records the `tdom-svcs` Agent OS to Superpowers migration pilot
state. It follows the repeatable process proven in `svcs-di`, while recording
package-specific differences.

## Repository State

- Branch: `codex/tdom-svcs-superpowers-migration-pilot`
- Agent OS config: not present
- `.codex/`: not present
- `AGENTS.md`: not present
- Local Agent OS Claude commands: present under `.claude/commands/agent-os/`
- Sphinx wrapper docs: not present under `docs/specifications/`
- `docs/research/`: present and separate from Agent OS specs

Note: classify specs by observed artifact shape. This repo contains both older
`spec.md` plus `tasks.md` artifacts and newer `shape.md` plus `plan.md`
artifacts.

## Agent OS Product Docs

Source directory: `agent-os/product/`

| Source | Destination | Notes |
| --- | --- | --- |
| `agent-os/product/mission.md` | `docs/superpowers/product/mission.md` | Product context, preserved in `tdom-svcs`. |
| `agent-os/product/roadmap.md` | `docs/superpowers/roadmap.md` | Historical/current roadmap content. |
| `agent-os/product/tech-stack.md` | `docs/superpowers/product/tech-stack.md` | Product technical context. |

Pilot status: copied to `docs/superpowers/` on 2026-05-04. The original
`agent-os/product/` files remain in place until cleanup.

## Agent OS Specs

Source directory: `agent-os/specs/`

Total directories: 15.

### Older Agent OS Shape

These usually contain `spec.md`, `tasks.md`, `planning/`, and sometimes
verification files.

- `2025-12-27-core-tdom-integration-hooks`
- `2025-12-28-basic-svcs-container-integration`
- `2025-12-28-component-decorator-discovery`
- `2025-12-28-component-lifecycle-middleware-system`
- `2025-12-29-component-lifecycle-middleware-system`
- `2025-12-31-documentation`

### Newer Agent OS Shape

These usually contain `shape.md`, `plan.md`, `references.md`, and sometimes
`standards.md`.

- `2026-01-31-path-middleware`
- `2026-02-01-reorg-docs`
- `2026-02-06-refactor-inject-categories`
- `2026-02-06-registry-introspection-helpers`
- `2026-02-15-reduce-middleware-tdom-specific`
- `2026-04-11-add-tdom-svcs-to-workspace`
- `2026-04-11-migrate-processor-api`
- `2026-04-26-1130-cleanup-container-only-context`
- `2026-04-26-1700-migrate-template-return-types`

Pilot status: all 15 directories were copied byte-for-byte into
`docs/superpowers/specs/` on 2026-05-04. Filename normalization and publishing
behavior are deferred.

## Agent OS Standards

Source directory: `agent-os/standards/`

| Source | Destination | Notes |
| --- | --- | --- |
| `agent-os/standards/agent-verification.md` | delete after cleanup | Replaced by root `t-strings/docs/superpowers/policies/verification.md`. |
| `agent-os/standards/index.yml` | delete | Agent OS index only. |
| `agent-os/standards/services/frozen-dataclass-services.md` | migrated to root policy | Folded into `t-strings/docs/superpowers/policies/protocol-first-service-design.md`. |
| `agent-os/standards/services/protocol-first-design.md` | migrated to root policy | Replaced by `t-strings/docs/superpowers/policies/protocol-first-service-design.md`. |
| `agent-os/standards/testing/fakes-over-mocks.md` | migrated to Codex testing skill | Folded into `/Users/pauleveritt/.codex/skills/testing/SKILL.md`. |
| `agent-os/standards/testing/function-based-tests.md` | migrated to Codex testing skill | Already covered by `/Users/pauleveritt/.codex/skills/testing/SKILL.md`. |
| `agent-os/standards/testing/protocol-satisfaction-test.md` | migrated to Codex testing skill | Folded into `/Users/pauleveritt/.codex/skills/testing/SKILL.md` with static-first guidance. |
| `agent-os/standards/testing/sybil-doctest.md` | migrated to Codex Sybil skill | Folded into `/Users/pauleveritt/.codex/skills/sybil/SKILL.md`; broader Sybil redesign remains parked. |

## Local Agent OS Tooling

Source directory: `.claude/commands/agent-os/`

Files:

- `discover-standards.md`
- `index-standards.md`
- `inject-standards.md`
- `plan-product.md`
- `shape-spec.md`

Proposed migration: delete after content migration. These are framework
commands, not `tdom-svcs` project history.

Pilot status: deleted after Superpowers history preservation.

## Docs Integration

`tdom-svcs` does not have `docs/specifications/` wrappers, so there is no Sphinx
mirror to repoint.

`docs/research/` exists and is preserved as a separate research stream. Do not
migrate research docs as Agent OS specs.

## Docs Integration

Pilot status: `docs/conf.py` excludes `superpowers/**` and `research/**` from
Sphinx source discovery so the preserved history and separate research stream do
not become orphan pages before the future Superpowers Sphinx plugin exists.

Active tooling config cleanup: removed the stale `agent-os` entry from
`pyproject.toml`'s `tool.ty.src.exclude` list.

`just docs-build` passes after resolving pre-existing stale category example
links and excluding the separate research stream from Sphinx source discovery.

`just quality` passes after adding explicit protocol annotations to the
imperatively registered category middleware examples. `just test` passes.

## Open Questions

- Should this package gain an `AGENTS.md` as part of the broader workspace agent
  setup cleanup, or remain out of scope for the Agent OS migration?
