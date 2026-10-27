# Optional capability design

These twelve cards help a project consider useful engineering work without adopting
a framework or duplicating its existing commands. They summarize current toolkit
decisions.

The cards and this rationale are MIT-licensed; the [licence map](../LICENSING.md)
states the terms. The [source catalog](capability-sources.json) binds these exact bytes
as current local design evidence and records their rights.

| Capability | Decision it helps a project make |
|---|---|
| `testing-feedback` | Choose quick feedback and deeper checks that reach the actual hazards. |
| `delivery-git-hooks` | Place local checks at the existing delivery boundary without competing Git owners. |
| `dependencies-licences` | Inspect dependencies, licences and maintenance cost before adding tools. |
| `ci-build-release-deploy` | Keep local proof, CI, release and deployment claims separate. |
| `security-privacy-secrets` | Inspect sensitive surfaces without disclosing secret values. |
| `observability-diagnostics` | Collect useful bounded diagnostics with explicit access and retention. |
| `data-database-operations` | Respect native data ownership, recovery and live-operation authority. |
| `api-service-contracts` | Check service boundaries without mistaking fakes for live integration. |
| `device-rig-app-control` | Separate simulated behavior from physical-device proof and resource leases. |
| `quality-evaluation` | Evaluate meaningful outcomes rather than count-based quality proxies. |
| `code-native-graphics` | Prefer editable repository-native graphics when they explain behavior. |
| `public-api-catalogue` | Discover useful interfaces while keeping network access separately authorized. |

A target inspects its native tooling first, then chooses `ADOPT`, `MERGE INTO EXISTING`,
`CITE ONLY` or `OMIT` for relevant cards. Adoption names one owner, native command,
evidence boundary, maintenance cost and revisit condition. A card grants no permission
to install, publish, access data, run a service or operate hardware.

Targets keep their native commands and existing wrappers. Focused and
closing checks may use the same command when their evidence needs coincide.
The capability oracle validates library structure, selections and local fake
decisions; it does not launch target commands.

The capability oracle checks the local catalog, card mappings, rights inheritance,
recursive duplicate-key rejection, repository containment and symlink refusal. Invented
restricted fixtures preserve negative rights checks. Deterministic checks establish only
those local contracts; fresh outsiders must separately assess discovery and useful
selection on the same final snapshot.

Owner: toolkit maintainer. Update this rationale when a capability decision changes;
then refresh its catalog digest and all affected evidence before review.
