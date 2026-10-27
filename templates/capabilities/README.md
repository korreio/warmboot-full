# Optional engineering capability library

This library is discovery material for an agent that is already inspecting a real
target. It is outside the managed payload: nothing here is selected, copied,
installed or executed by default.

## Two use modes

### Ordinary target use

1. Inspect the target's existing owners, commands, constraints and evidence first.
2. Review the names and one-line summaries in the twelve-row inventory once.
3. Open only a card whose trigger is real, or whose anti-trigger is needed to decide
   `OMIT`. Do not create twelve recurring records by default.
4. Choose `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT` using the
   [disposition definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit).
   Record one disposition per opened card.
5. Name the surviving target owner and native command. Related-card links are for
   navigation only; they never select another card or create a dependency.
6. Prove the highest relevant hazard with target-native evidence. A local fake or
   syntax check never proves a live service, database, deployment, device, API, model
   or provider.

### Acceptance or audit mode

Only when the acceptance authority explicitly invokes
[`acceptance/capability-outsider.md`](../../acceptance/capability-outsider.md),
inspect all twelve cards and report one disposition per card. These are audit
recommendations, not target edits or accepted adoption decisions. Proposed
destinations preserve the recorded target owners. The evaluator's own lack of write
authority does not change a label; `authority_sufficient` concerns the target's
recorded authority.

Admission requires all of the following:

```text
observed_need
AND owner_known
AND native_command_known
AND authority_sufficient
AND highest_hazard_provable
AND recurring_tax_accepted
AND deletion_or_revisit_observable
```

When the expression is false, choose `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`.
Never invent an owner, command or permission to make a card fit.

## Inventory

| Card | Purpose |
|---|---|
| [testing-feedback](testing-feedback.md) | Focused feedback, closing proof and honest escalation |
| [delivery-git-hooks](delivery-git-hooks.md) | Local delivery checks without transferring Git authority |
| [ci-build-release-deploy](ci-build-release-deploy.md) | Separate build, release and external mutation boundaries |
| [quality-evaluation](quality-evaluation.md) | Decision-changing quality evaluation without a dashboard tax |
| [code-native-graphics](code-native-graphics.md) | Reviewable diagrams and generated graphics |
| [data-database-operations](data-database-operations.md) | Schema, migration, backup and recovery ownership |
| [security-privacy-secrets](security-privacy-secrets.md) | Threat-led local security and data minimization |
| [dependencies-licences](dependencies-licences.md) | Dependency, licence and supply-chain decisions |
| [observability-diagnostics](observability-diagnostics.md) | Diagnostics that preserve privacy and degraded operation |
| [api-service-contracts](api-service-contracts.md) | Owned API boundaries, schemas and failure semantics |
| [public-api-catalogue](public-api-catalogue.md) | External API fitness, privacy, cost and substitute paths |
| [device-rig-app-control](device-rig-app-control.md) | Single-holder simulator-first rig, app and LLM control |

## Authority boundary

A card is knowledge, not authorization. This library grants no Git, package-install,
hosted-CI, deployment, rollback, network, external scan, database, credential, device,
LLM, publication or user-data authority. Record unavailable proof as `UNPROVED` or
missing required authority/input as `BLOCKED`.
