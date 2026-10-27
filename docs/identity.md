# Warmboot Full identity

The product is **Warmboot Full**. Its human workspace is
`warmboot-full.code-workspace`. No checkout path, account or host is prescribed here.

The protocol identifiers are the managed directory `.agent-warmboot/`, the manifest
toolkit id `agent-warmboot` and manifest schema `1`; they stay fixed for existing
installations. The source revision is informational and edition-specific
(`UNRELEASED-development` here). The helper `bin/warmboot` writes the same nine-file
layout in both editions: the root loaders `AGENTS.md` and `CLAUDE.md`, and
`.agent-warmboot/` with `core.md`, five routes and `.agent-warmboot/manifest.json`.

`SOURCE_REVISION` is `UNRELEASED-development`. The current tree has no release manifest
or inherited release-readiness claim. A future release needs its own immutable candidate,
review, tag and receipt under [the release contract](release.md). Illustrative manifests
and synthetic upgrade fixtures are examples, never evidence that these bytes shipped.

Owner: maintainer coordinator. Update when the product, installed format or release
identity changes; a name alone proves neither authenticity nor publication.
