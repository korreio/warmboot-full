# Changelog

Template use: merge into an existing changelog or release-history surface. Adopt only
when the project needs a user-visible change history and has no stronger existing
source. Do not create two ledgers, and do not log refactors, agent process, or internal
churn unless users must act on them. Replace every `{{MARKER}}` and delete this note.

- Changelog owner: {{RELEASE_OR_PRODUCT_OWNER}}
- Authority: records changes; grants no Git, package, network, credential, deployment,
  release, or publication permission.
- Evidence boundary: an entry does not claim a tag, publication, deployment, or
  release.
- Maintenance: update in the same change as any user-visible behavior, compatibility,
  or migration impact.
- Revisit or retire: merge when another release or history surface becomes
  authoritative.

## [{{VERSION_OR_UNRELEASED}}] — {{YYYY_MM_DD}} ({{PLAIN_LANGUAGE_THEME}})

### {{ADDED_CHANGED_FIXED_REMOVED_SECURITY}}

- {{USER_VISIBLE_CHANGE}} — {{MIGRATION_OR_ACTION_IF_ANY}} ({{ISSUE_OR_RELEASE_REFERENCE}})

Move entries to a dated/versioned release when it is published. Publication remains
separately authorized; editing this file does not authorize a release.

For a coded project this change-history role is required, but the role may merge into an
existing release/history surface; do not keep this template as a competing file.
