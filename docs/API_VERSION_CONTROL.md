# API and contract version control (v1)

Status: adopted repository policy; this file alone does not prove runtime enforcement or production deployment.

## Rules

1. Git commits track implementation. Git release tags use `vMAJOR.MINOR.PATCH` for a released service artifact; release metadata must identify source commit, immutable image digest, environment, and migration revision. Never claim a deployed version from a tag alone.
2. Externally consumed HTTP contracts use explicit major versions (prefer `/v1/...`). Existing unversioned routes and provider callbacks remain supported until consumers are inventoried and migrated; do not rewrite paths without compatibility tests. Provider-owned webhook URLs can remain unversioned while their payload schemas are versioned.
3. JSON Schema contracts live in versioned directories such as `contracts/<domain>/v1/`, with immutable `$id` and explicit compatibility rules. Every consumer/producer handoff records schema ID, owner, accepted major, and evidence. Existing schemas are not renamed solely for this policy.
4. Compatible additive changes can retain the major version when consumers tolerate them; removals, renamed fields, altered requiredness or semantics, changed auth expectations, and incompatible response changes require a new major or a verified compatibility adapter. Schema shape validation is not authorization.
5. Database migrations are append-only, sequentially identified, reviewed for rollback/forward recovery, and tested against production-like schema state. Do not edit an applied migration; use a new migration. Database migration numbers are independent of HTTP major versions.
6. Authentication/session contracts, event envelopes, idempotency, error responses, and inter-service tokens must be inventoried as interfaces. Secrets and token values must never be committed to a version manifest.
7. CI acceptance for each interface change: validate schema syntax and IDs; compare against the previous released contract; run producer and consumer tests (including invalid payloads, authorization failures, and old-major compatibility); verify migration upgrades; record immutable artifact identity. A passing build alone is not proof of compatibility.
8. Release records distinguish **documented**, **tested**, **deployed**, and **verified in production**. No automatic deprecation or removal of v1; record consumer inventory and migration approval before removing a version.

## Version inventory and acceptance

| Interface | Current status | Follow-up required |
| --- | --- | --- |
| HTTP routes | Existing paths retained; some services already expose `/v1` | Inventory actual routes, owners and consumers; document exceptions |
| JSON Schema | Existing contracts retained | Validate IDs and breaking-change compatibility against last release |
| DB schema | Existing migration files retained | Confirm applied revisions against database and forward/rollback tests |
| Authentication | Existing credentials and sessions unchanged | Map consumers, scope, expiry, revocation and backward compatibility |
| Deployment | Git source tracked | Record release tag, commit, image digest, runtime environment and live SHA |

## Change record template

`interface | producer | consumer | current_major | proposed_major | schema_id | change_class | compatibility_test | migration | source_sha | image_digest | deployed_sha | evidence | approval`

**Implementation boundary:** This governance file does not add routes, change API authentication, alter Neon, tag releases, or change running deployments. Those changes require service-specific PRs and evidence.
