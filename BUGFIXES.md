# Observed-defect ledger

These causal notes preserve observed defects and their recurrence owners. Test pointers
name current methods; they are not fresh execution evidence. Current results come from
rerunning the [command inventory](docs/acceptance.md#deterministic-command-inventory).
IDs are permanent and never reused; retired records leave gaps. IDs are per edition;
the sibling edition's ledger numbers its own defects. Defects in the shared installer are
recorded in both ledgers, each under its own ID.

Recurring tax is limited to the named local cases when their owning boundary changes,
plus the live gates explicitly named below. No retained pin needs anything outside this
repository, an external service or a permanent extra lane. Fold a pin into a cheaper
behavior check only when it reaches the same cause; a narrower synthetic replacement
or a source-text canary does not prove the retired live behavior.

## WB-058 — Acceptance JSON beyond the decoder's depth or integer limits escaped as a traceback

- Owner: `acceptance/strict_json.py` maintainer, for every acceptance loader that decodes through it.
- Cause/fix: each loader caught `json.JSONDecodeError`, but nesting deeper than the decoder's stack raises `RecursionError` and an integer longer than the interpreter's digit limit raises a plain `ValueError`. Either one passed every loader and ended the CLI with a traceback instead of `FAIL`. The shared decoder now raises `json.JSONDecodeError` for both, so every loader reports its own verification error.
- Recurrence/limit: 200000 nested arrays, and an integer one digit past the interpreter's limit where one exists, must raise `json.JSONDecodeError` from the decoder for text and bytes, and each of the seven loaders must raise its own error class. The depth that triggers the failure depends on the host's decoder and stack.
  - `acceptance/tests/test_strict_json.py::StrictJsonLimitTests.test_decoder_limits_raise_json_decode_error`.
  - `acceptance/tests/test_strict_json.py::StrictJsonLimitTests.test_every_loader_reports_decoder_limits_as_its_own_error`.
- Retirement: remove these cases when the standard decoder reports its depth and integer limits as `json.JSONDecodeError` on every supported interpreter.

## WB-057 — Unhashable capability JSON values escaped controlled validation

- Owner: `acceptance/capability_oracle.py` library, selection and fake-case maintainer.
- Cause/fix: an array or object where a string was expected (a considered module, a disposition's module ID or disposition, a refused action, a manifest enum or list item, a fake operation) reached a set or dictionary lookup and raised `TypeError`. The CLI catches only `CapabilityVerificationError`, so it printed a traceback instead of `FAIL`. One `_strings` helper and exact string checks now run before every such lookup.
- Recurrence/limit: Each listed selection, manifest and fake-case position must raise `CapabilityVerificationError` for a nested array or object; valid fixtures stay accepted.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_unhashable_json_values_fail_as_verification_errors`.
- Retirement: Retire the separate case when typed JSON ingress rejects non-string values before every capability validator and the CLI reach them.

## WB-055 — A late parent relocation during apply was reported without saying recorded paths may have moved

- Owner: `bin/warmboot` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause/fix: creation is descriptor-relative and postflight already refused `APPLIED` when an opened managed directory was renamed after validation, but the preservation warning named the recorded paths as if they were still where the receipt says. A rename by another actor can move an opened directory, and the files written into it, outside the target. Every preservation warning now ends with "recorded paths may have moved", so a reader does not trust the named locations.
- Recurrence/limit: A managed directory renamed between validation and the first create must leave its original inode with the written file, keep the replacement directory empty, exit 1 without `APPLIED`, and warn that recorded paths may have moved. Detection is after the fact; the installer does not provide continuous pathname containment or rollback, and it assumes no other actor relocates opened parents.
  - `tests/test_warmboot.py::WarmbootCliTests.test_late_parent_rename_preserves_inode_and_warns_paths_may_have_moved`.
- Retirement: remove this scar only when installation holds every opened parent against relocation, or verifies containment continuously, so a warning about moved paths can no longer be needed.
- Sibling edition: Warmboot Light records this defect as WB-004.

## WB-054 — Installer output printed raw manifest and filesystem names, so a name could forge a line

- Owner: `bin/warmboot` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause/fix: only the invalid-entry line escaped its path (through `repr`). Every other message interpolated manifest keys, managed filesystem names, checkout route names and the target path raw, so a name carrying a newline, carriage return or terminal escape could start or overwrite an output line: a `PASS` line inside a `check` `FAIL` report, or an extra line in an `init` preview or refusal. Every such value now passes through one helper, `printable_path`, which writes each unprintable character, and the backslash itself, as the escape `repr` uses, and leaves printable names, ordinary Unicode included, unchanged. It also takes over WB-049's surrogate escape in the `check` failure list, whose strict UTF-8 pin still applies.
- Recurrence/limit: Each message that can carry such a name (unexpected manifest entries, missing and unexpected managed paths and directories, the per-file missing line, the target in the verdict line, the `init` refusal and preview) must keep every output line printable, show the escaped form and print no line starting with `PASS` or `APPLIED`. The `missing entries` list names only the fixed required paths and cannot carry a manifest name. A literal backslash in a name is shown doubled.
  - `tests/test_warmboot.py::WarmbootCliTests.test_printable_path_escapes_only_what_could_forge_or_blur_a_line`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_check_output_cannot_be_forged_by_a_newline_in_a_manifest_key`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_check_escapes_manifest_route_keys_in_missing_path_failures`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_check_escapes_filesystem_names_in_unexpected_managed_paths`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_check_escapes_the_target_path_in_its_verdict_line`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_init_escapes_filesystem_and_route_names_in_output`.
- Retirement: remove this scar only when every output line is produced by one renderer that escapes each interpolated value by construction.
- Sibling edition: Warmboot Light records this defect as WB-008.

## WB-053 — Installed-state manifest check accepted non-JSON numeric constants

- Owner: `bin/warmboot` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause/fix: `check_command` decoded `manifest.json` with the stdlib defaults, which accept `NaN`, `Infinity` and `-Infinity` as floats although they are not JSON, so a manifest carrying one reached the field checks (reported as `unsupported schema` in the schema position) instead of failing as invalid input. `loads_rejecting_duplicate_keys` now passes a `parse_constant` hook that raises `ValueError` for each token, which the load point reports as `manifest.json: invalid JSON`.
- Recurrence/limit: Each token in the schema position must exit 1 with `manifest.json: invalid JSON` and no traceback. Out-of-range numbers such as `1e400` are grammatical JSON, still decode to a float infinity and are left to the field checks.
  - `tests/test_warmboot.py::WarmbootCliTests.test_check_rejects_non_json_numeric_constants`.
- Retirement: remove this scar only when the installed manifest is parsed through a shared strict decoder that cannot yield non-JSON constants at the CLI boundary.
- Sibling edition: Warmboot Light records this defect as WB-007.

## WB-052 — Deeply nested manifest JSON escaped `check` as a traceback

- Owner: `bin/warmboot` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause/fix: the manifest load point caught only `ValueError`. Nesting deep enough to exhaust the decoder raises `RecursionError`, which is not a `ValueError`, so `check` stopped with an uncaught traceback and printed no FAIL report. The load point now catches `RecursionError` alongside `ValueError` and reports `manifest.json: invalid JSON` with exit 1.
- Recurrence/limit: A manifest of 200000 `[` followed by 200000 `]` must exit 1 with `manifest.json: invalid JSON` on stdout and no traceback on stderr. The depth that triggers the error depends on the host's decoder and stack; shallower nesting still decodes and is judged by the field checks.
  - `tests/test_warmboot.py::WarmbootCliTests.test_check_rejects_deeply_nested_manifest_as_invalid_json`.
- Retirement: remove this scar only when the installed manifest is parsed through a shared decoder whose depth failure is already a controlled validation error at the CLI boundary.
- Sibling edition: Warmboot Light records this defect as WB-007.

## WB-051 — Unhashable manifest enum values escaped controlled validation

- Owner: `acceptance/release_manifest.py` payload/manifest maintainer.
- Cause/fix: A manifest with an array or object in `manifest_kind`, release `status` or exclusion `scope` raised `TypeError` during set membership. Exact string checks now precede membership in each owning enum validator, preserving controlled validation failures.
- Recurrence/limit: Valid enums and invalid strings did not reach unhashable JSON containers. The boundary case covers malformed values through release/illustrative APIs and CLI, requiring FAIL without traceback; valid candidate/illustrative controls remain accepted.
  - `acceptance/tests/test_upgrade_oracle.py::ReleaseManifestBoundaryTests.test_invalid_set_membership_domains_fail_cleanly_in_api_and_cli`.
  - `acceptance/tests/test_upgrade_oracle.py::ReleaseManifestBoundaryTests.test_valid_candidate_api_cli_and_illustrative_controls`.
- Retirement: Retire the separate cases when typed JSON ingress rejects non-string enum values before every API and CLI path reaches these validators.

## WB-050 — Nested payload includes followed symlinked ancestors

- Owner: `acceptance/release_manifest.py` payload/manifest maintainer.
- Cause/fix: A maintainer selecting a nested include could hash outside bytes because leaf inspection did not validate include ancestry. `_included_nodes` now checks each include through `_repository_path` before traversal, rejecting symlink components even when they point back inside the repository.
- Recurrence/limit: Root-level includes and leaf-symlink checks did not reach a symlink above a nested include. Negative cases cover external/internal ancestors; controls retain ordinary nested selection and an excluded leaf symlink.
  - `acceptance/tests/test_upgrade_oracle.py::ReleaseManifestBoundaryTests.test_nested_include_refuses_external_and_internal_symlink_ancestors`.
  - `acceptance/tests/test_upgrade_oracle.py::ReleaseManifestBoundaryTests.test_ordinary_nested_include_and_excluded_symlink_control`.
- Retirement: Fold into a shared no-follow selection primitive only when its behavior covers every include ancestor before hashing.

## WB-049 — Manifest pathname failures escaped controlled validation and diagnostics

- Owner: `bin/warmboot` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause/fix: lexical path checks omitted host encoding and NUL validation; failure rendering also assumed every encodable filename was printable. Validate with `os.fsencode` and reject encoded NUL through `invalid managed file entry`; preserve host-encodable names and escape unprintable surrogates locally in failure output.
- Recurrence/limit: Reject unencodable/NUL keys without mutation, preserve host-representable controls, and render surrogateescape paths through strict UTF-8 stdout.
  - `tests/test_warmboot.py::WarmbootCliTests.test_check_rejects_unrepresentable_manifest_paths_without_mutation`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_check_reports_surrogateescape_path_on_strict_utf8_stdout`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_check_preserves_host_representable_manifest_paths`.
- Retirement: fold these cases into ordinary manifest/diagnostic behavior tests when those tests exercise the same recurrence.

## WB-048 — A resolved scratch alias bypassed prepare's repository deletion guard

- Owner: `acceptance/prepare.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause/fix: the cached resolved scratch root supplied an exemption before repository overlap refusal. Check equality/ancestors unconditionally first, derive the literal `ROOT/.acceptance-work` at call time, and permit the source-descendant exception only for a resolved strict descendant when that literal root is absent or a real directory.
- Recurrence/limit: Mock deletion/copy while checking cached scratch aliases; separately check absent/real roots, special nodes and nested escapes at call time.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_scratch_alias_cannot_authorize_repository_deletion`.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_refuses_repository_root`.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_scratch_root_descendant_is_exempt_from_repository_overlap`.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_call_time_scratch_requires_absent_or_real_directory`.
- Retirement: fold into ordinary prepare behavior tests when they cover the same alias recurrence, or retire with a replacement mechanism that cannot delete overlapping repository paths.

## WB-047 — Kickoff separation checks failed open to confusable identity aliases

- Owner: `acceptance/kickoff_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: kickoff_oracle imported only `strict_json` and had no `_identity_key`. The owner-versus-coordinator test (`owner == coordinator`), the research-owner set it builds and then tests the challenger against (`research_owners.add(owner)` / `challenger in research_owners`), and the architecture/delivery merge detection (`arch owner == delivery owner`) all keyed on raw text, so a confusable alias failed OPEN — defeating the exact independence invariant those checks exist to hold.
- Recurrence/limit: Direct negatives cover each compatibility-alias separation site, synthetic ignorables and padded twins; they do not establish universal homoglyph detection.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_leading_space_twin_of_research_owner_as_challenger`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_trailing_space_twin_in_architecture_delivery_merge`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_challenger_confusable_alias_of_research_owner`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_coordinator_confusable_alias_as_lane_owner`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_confusable_architecture_delivery_merge`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_synthetic_ignorable_in_separation_identity`.
- Retirement: remove this scar only when typed kickoff identities enforce the same canonical ingress, synthetic-ignorable exclusion, and compatibility-fold key at every separation comparison before verification.

## WB-046 — Installed-state manifest check accepted duplicate-key JSON last-wins

- Owner: `bin/warmboot` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: `check_command` decoded `manifest.json` through the stdlib `json.loads` (the sole parse in the CLI), which normalizes duplicate object pairs into one last-value-wins entry before any schema or frozen-hash check runs, so an earlier tampered block was invisible to the content comparison.
- Recurrence/limit: Raw top-level and nested duplicate-key manifests must fail JSON decoding before frozen-hash comparison.
  - `tests/test_warmboot.py::WarmbootCliTests.test_check_rejects_duplicate_key_manifest`.
- Retirement: remove this scar only when the installed manifest is parsed through a shared typed decoder that makes duplicate-key acceptance structurally impossible at the CLI boundary.
- Sibling edition: Warmboot Light records this defect as WB-006.

## WB-045 — Prepare's repository-overlap guard also refused the dedicated scratch root

- Owner: `acceptance/prepare.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the WB-039 overlap refusal ran before the allowed-roots loop and carried no exemption, so a workspace under the scratch root — itself a ROOT descendant — was rejected by the overlap rule before the loop that admits `ACCEPTANCE_WORK_ROOT` descendants could ever run.
- Recurrence/limit: Accept the dedicated scratch descendant while refusing repository ROOT and ordinary ROOT descendants.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_scratch_root_descendant_is_exempt_from_repository_overlap`.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_refuses_repository_root`.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_arbitrary_deep_non_temp_path_is_rejected`.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_refuses_allowed_roots_themselves`.
- Retirement: remove this scar only when the release harness materializes verifier checkouts and scratch workspaces through a mechanism that cannot target a repository-overlapping path, so prepare needs no path guard (shared with WB-039).

## WB-044 — Shared CommonMark fence helpers had no direct regression home

- Owner: `acceptance/unicode_policy.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the CommonMark fence contract (three-marker minimum, zero-to-three-space indent, bounded closer) had behavior coverage only through the oracles that call it; no test asserted the helper bounds directly, so a silent bound relaxation had no home to fail in.
- Recurrence/limit: Direct cases reject four-space openers/closers and a two-marker run, which caller happy paths did not isolate.
  - `acceptance/tests/test_unicode_policy.py::MarkdownFenceHelperTests.test_four_space_indent_is_not_a_fence_opening`.
  - `acceptance/tests/test_unicode_policy.py::MarkdownFenceHelperTests.test_two_backtick_run_is_not_a_fence`.
  - `acceptance/tests/test_unicode_policy.py::MarkdownFenceHelperTests.test_four_space_indented_closer_is_not_a_valid_closer`.
- Retirement: remove this scar only when the fence helpers gain a typed CommonMark grammar whose indent and run-length bounds cannot be relaxed without a structural failure.

## WB-043 — Result-file ingress sniffed a non-UTF-8 encoding and verified it

- Owner: `acceptance/oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the CLI passed raw bytes to the JSON decoder and let it auto-detect the encoding, breaking the shared UTF-8-text ingress uniformity the other readers hold.
- Recurrence/limit: UTF-16 response bytes must fail controlled UTF-8 ingress at the CLI.
  - `acceptance/tests/test_oracle.py::OracleTests.test_cli_rejects_utf16_encoded_response`.
- Retirement: remove this scar only when a shared typed ingress makes non-UTF-8 evidence unrepresentable at every acceptance reader.

## WB-042 — Float and boolean fake status elements aliased exact int/str evidence

- Owner: `acceptance/capability_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: `evaluate_fake_case` compared status values by equality before checking their exact type, so `float` and `bool` aliases of an integer or string status were admitted.
- Recurrence/limit: An otherwise valid fake status sequence receives float/bool aliases and must fail exact-type validation.
  - `acceptance/tests/test_capability_fakes.py::CapabilityFakeTests.test_rejects_float_or_boolean_status_sequence_element`.
- Retirement: remove this scar only when typed fake evidence makes a non-`int`/`str` status unrepresentable before comparison.

## WB-041 — A nested unbounded whitespace quantifier backtracked catastrophically

- Owner: `acceptance/source_comprehension_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the declaration-gap pattern nested `\s+` within a `(...)*` group, so a run of spaces before a non-matching character forced exponential backtracking.
- Recurrence/limit: The isolated adversarial-whitespace process must finish within its timeout. This slower bounded case reaches backtracking missed by ordinary gaps.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_declaration_gap_regex_stays_linear_on_adversarial_whitespace`.
- Retirement: remove this scar only when a non-backtracking matcher or typed fixture grammar owns the declaration gap.

## WB-040 — Commented or fenced tables and fields stayed visible to the parsers

- Owner: `acceptance/upgrade_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: `_parse_dispositions`, `_parse_guards` (upgrade) and `_source_ids_from_card` (capability) split on `split_markdown_lines`, which retains commented and fenced lines, so evidence hidden from a reader still reached the parser.
- Recurrence/limit: Otherwise valid tables and source-ID fields become comments/fences and must stop providing authority.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_disposition_and_guard_tables_must_be_visible_markdown`.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_source_ids_field_must_be_visible_markdown`.
- Retirement: remove this scar only when a typed evidence format makes commented or fenced authority unrepresentable before these readers run.

## WB-039 — Prepare admitted a temp-root workspace overlapping the repository ROOT

- Owner: `acceptance/prepare.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: `_safe_workspace` proved only strict-descendant containment within `ACCEPTANCE_WORK_ROOT` or `SYSTEM_TEMP_ROOT`; it never rejected a workspace that equaled, contained, or was contained by the repository ROOT, so a repository checkout located under the temp root passed the guard and was destroyed before any snapshot.
- Recurrence/limit: Repository-root refusal includes a checkout under system temp; ordinary allowed-root refusal remains covered.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_refuses_repository_root`.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_arbitrary_deep_non_temp_path_is_rejected`.
- Retirement: remove this scar only when the release harness materializes verifier checkouts through a mechanism that cannot target a repository-overlapping path, so prepare needs no path guard.

## WB-038 — Python line and fence semantics manufactured Markdown evidence

- Owner: `acceptance/unicode_policy.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: production readers delegated raw Markdown boundaries to Python's broader Unicode line/whitespace semantics and independently approximated fence visibility. Their ordering could parse HTML-comment syntax before deciding whether the untouched raw line was a fence, even though CommonMark fence grammar is line-oriented.
- Recurrence/limit: Cross-reader mutations cover raw Markdown boundaries, trim rules, fence ordering and visible headings. These bounded cases do not prove a complete CommonMark parser.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_non_markdown_separators_cannot_create_capability_lines`.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_non_markdown_separators_cannot_be_trimmed_from_source_ids`.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_capability_markdown_accepts_commonmark_line_endings`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_repeated_outer_pipes_cannot_shift_checked_table_cells`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_adr_heading_requires_material_content_after_inline_comments`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_template_pack_membership_is_derived_from_the_role_selection_table`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_non_markdown_separators_cannot_create_upgrade_record_lines`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_comment_text_cannot_synthesize_or_leak_from_upgrade_fences`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_backtick_in_info_string_does_not_hide_upgrade_evidence`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_non_markdown_separators_cannot_create_visible_adr_heading`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_comment_text_cannot_synthesize_or_leak_from_fences_before_adr`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_visible_adr_heading_accepts_commonmark_line_endings`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_safety_receipt_accepts_commonmark_closing_fence_shapes`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_safety_receipt_rejects_nonclosing_fence_shapes`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_non_markdown_separators_cannot_be_trimmed_from_table_cells`.
- Retirement: remove this scar only when one lower-tax typed evidence format or reviewed Markdown parser owns all affected line, trim, and visibility boundaries without Python-only separator or duplicated fence behavior.

## WB-037 — Bounded prose and Java scanners misclassified syntax as evidence

- Owner: `acceptance/upgrade_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the ownership scanner normalized paragraph lines before classifying the first raw content line's indentation. The bounded Java matcher recognized declaration keywords and identifier starts without separating member-selected `.class` expressions or requiring a record header to reach its component `(`; a single-line assumption would also make a valid multiline generic header disappear from exact-one counting.
- Recurrence/limit: Raw paragraph indentation, instance-of class literals and multiline generic records have direct cases and Java controls.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_native_ownership_requires_unique_section_and_first_raw_paragraph`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_accepts_instanceof_expressions_without_extra_declarations`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_instanceof_expression_controls_are_valid_java`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_accepts_multiline_unicode_generic_primary_record`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_rejects_multiline_unicode_generic_second_record`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_multiline_unicode_generic_record_controls_are_valid_java`.
- Retirement: remove this scar only when typed ownership evidence makes hidden/code-block authority unrepresentable and a target-native Java parser owns exact declaration enumeration without these bounded token/header distinctions.

## WB-036 — Unsafe embedded Unicode evidence characters bypassed semantic boundaries

- Owner: `acceptance/unicode_policy.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the shared Unicode policy covered designed/runtime ignorables and compatibility aliases, while summary punctuation and ATX syntax had separate guards. No shared raw ingress predicate rejected the remaining unsafe Unicode `C` categories before identity comparison, materiality classification, or heading-domain validation. The canonical ATX regex also treated every non-space/non-`#` code point as material without consulting the shared synthetic-ignorable policy.
- Recurrence/limit: Unsafe-category identity/summary/heading mutations and synthetic-only headings reach each affected reader while preserving visible Unicode controls.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_unsafe_unicode_evidence_characters_reject_identity_and_heading`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_adr_heading_requires_visible_content_beyond_synthetic_ignorables`.
  - `acceptance/tests/test_self_improvement_oracle.py::SelfImprovementOracleTests.test_unsafe_unicode_evidence_characters_reject_identity`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_unsafe_unicode_evidence_characters_reject_identity_and_summary`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_candidate_release_note_summaries_are_not_bounded_state_only_shapes`.
- Retirement: remove this scar only when typed evidence ingress makes unsafe embedded Unicode categories unrepresentable before every affected identity, materiality, and heading comparison, and makes synthetic-only ATX content unrepresentable, while preserving ordinary assigned-Unicode and synthetic-enhanced visible-heading controls.

## WB-035 — ADR anchors could live outside their declaration and target locations

- Owner: `acceptance/source_comprehension_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: local rationale fragments were checked against the selected declaration comment, but the exact ADR `source_fragment` was checked against the aggregate comment text. An unrelated comment could therefore satisfy the ADR source half of the evidence. The target half used a raw substring search, so it proved neither a visible line-equal heading nor uniqueness. The visibility repair did not first constrain the declared value to the bounded ATX-heading domain.
- Recurrence/limit: Source-local anchors and one exact visible canonical target heading replace aggregate comment/substring success.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_rejects_adr_anchor_relocated_to_trailing_comment`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_adr_heading_record_requires_canonical_one_line_atx_form`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_adr_target_requires_one_exact_visible_raw_heading`.
- Retirement: remove this scar only when typed declaration evidence binds its ADR source fragment and target document/heading structurally, without aggregate-comment search.

## WB-034 — Old and new releases could reuse one immutable annotated tag

- Owner: `acceptance/upgrade_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: each request release, manifest and note was validated independently, and the cross-release boundary compared commits and payload digests but not the two declared annotated-tag refs. Internal agreement therefore could not prove old/new ref independence.
- Recurrence/limit: Fully rebound inputs retain distinct commits/payloads while sharing a tag, isolating the cross-release refusal.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_rejects_same_annotated_ref_after_fully_rebound_release_inputs`.
- Retirement: remove this scar only when typed old/new release identities, or an authoritative tag resolver, make one immutable annotated ref structurally incapable of naming both sides of an upgrade comparison.

## WB-033 — Java pre-lex Unicode escapes bypassed declaration enumeration

- Owner: `acceptance/source_comprehension_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the fixture scanner applied its position-preserving lexical mask directly to raw source, while Java processes eligible Unicode escapes before comments, strings, tokens and declaration parsing. Implementing only the later lexical view left a pre-lex representation gap.
- Recurrence/limit: Raw pre-lex escape rejection retains literal Unicode and annotation-adjacency controls.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_rejects_raw_java_unicode_escape_syntax_before_lexing`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_accepts_literal_unicode_primary_declarations`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_accepts_primary_annotation_declaration_adjacency_forms`.
- Retirement: remove this scar only when a target-native parser with Java pre-lex Unicode translation, or a typed fixture format that structurally forbids raw escapes, owns the complete declaration/orientation boundary.

## WB-032 — Upgrade role and native-owner aliases bypassed identity boundaries

- Owner: `acceptance/upgrade_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: upgrade request roles and digest-bound native owners used canonical-text checks or raw equality rather than the shared synthetic-ignorable rejection and `NFKC(casefold(NFKC(text)))` collision key already used by source/self evidence. The independence set omitted challenger-versus-coordinator/Git, and record validation searched for generic owner/coordinator text instead of one exact sentence derived from the validated native-authority inventory and request roles. Its substring/count check did not bind the first nonempty raw paragraph or distinguish a unique raw, unquoted `## Native truth and excluded work` heading from heading-shaped text inside the bounded comment/fence forms.
- Recurrence/limit: Canonical role/native-owner cases and exact derived first-paragraph binding reach alias collisions and hidden/late authority.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_upgrade_role_alias_keys_enforce_sameness_and_independence`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_upgrade_role_identities_reject_padding_or_synthetic_ignorables`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_native_owner_identities_reject_unsafe_text_and_accept_alias_forms`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_record_binds_native_root_owner_and_request_git_identity`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_native_ownership_requires_unique_section_and_first_raw_paragraph`.
- Retirement: remove this scar only when typed role/native-owner identifiers enforce the same canonical ingress, synthetic-ignorable exclusion, coordinator/Git sameness, challenger/release-holder independence and separate content-owner/Git-holder record binding in a typed record field before upgrade planning.

## WB-031 — Leading and internal Unicode punctuation manufactured material summaries

- Owner: `acceptance/upgrade_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: summary normalization removed only trailing Unicode punctuation. Leading or internal category-`P` characters survived; deleting them or treating them as token boundaries could reveal a state-only alias that the preserved spelling hid.
- Recurrence/limit: Rebound summaries reject punctuation-manufactured state-only text; legitimate material-summary controls remain in the owning suite.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_unicode_punctuation_cannot_manufacture_materiality`.
- Retirement: remove this scar only when typed release-note semantics make state-only text and punctuation aliases unrepresentable before materiality comparison, while preserving legitimate punctuation-bearing change descriptions.

## WB-030 — First-match Java search ignored later authored declarations

- Owner: `acceptance/source_comprehension_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: `TYPE_RE.search` selected one declaration and never established that the position-preserving masked source contained no later authored type. One orientation, classification, rationale list and ADR anchor could therefore appear to cover a multi-declaration fixture. The later exact-one matcher admitted any non-whitespace post-keyword character, conflating Java identifier starts with contextual syntax.
- Recurrence/limit: Second-declaration mutations and valid Java controls retain exact-one counting while preserving contextual syntax and identifier bounds.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_rejects_every_second_supported_java_declaration`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_second_declaration_rejections_use_valid_java_controls`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_accepts_primary_annotation_declaration_adjacency_forms`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_java_identifier_start_categories_are_bounded`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_accepts_contextual_record_uses_without_extra_declarations`.
- Retirement: remove this scar only when a target-native parser or per-declaration typed fixture schema owns complete declaration enumeration and orientation/rationale coverage without this bounded regex scanner.

## WB-029 — Default-ignorable and compatibility aliases bypassed evidence semantics

- Owner: `acceptance/unicode_policy.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the ignorable policy treated runtime `Cf` as the complete ignorable set and summary text used casefold without compatibility normalization. Unicode default-ignorables in other categories and characters exposed by normalization therefore remained semantic input.
- Recurrence/limit: The explicit policy table/predicate, state-token splits, normalized summaries and identity cases reach designed ignorables and compatibility aliases.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_ignorables_cannot_split_any_state_only_token_position`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_unicode_policy_has_independent_table_count_and_predicate_parity`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_all_synthetic_ignorables_are_non_material`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_release_note_summaries_are_canonical_and_material_after_rebind`.
  - `acceptance/tests/test_self_improvement_oracle.py::SelfImprovementOracleTests.test_rejects_synthetic_ignorables_in_role_identities`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_rejects_synthetic_ignorables_in_author_or_reviewer`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_upgrade_role_identities_reject_padding_or_synthetic_ignorables`.
- Retirement: remove this scar only when typed canonical identities and typed material-change semantics reject the same designed/runtime ignorables and compatibility aliases before independence/materiality comparison, with an equivalent explicit Unicode-policy refresh boundary.

## WB-028 — Exact scalar and release-note state substitutes passed semantic evidence

- Owner: `acceptance/upgrade_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: equality ran before exact scalar validation; the upgrade reader bound note bytes and paths but not each release's compatibility role or canonical material text.
- Recurrence/limit: Exact fake-attempt/planner scalars and compatibility/state-only mutations after digest rebinding reach values hidden by ordinary equality.
  - `acceptance/tests/test_capability_fakes.py::CapabilityFakeTests.test_rejects_boolean_or_float_expected_attempts`.
  - `acceptance/tests/test_self_improvement_oracle.py::SelfImprovementOracleTests.test_rejects_boolean_like_planner_result_scalars`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_release_note_compatibility_is_canonical_and_release_specific`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_release_note_summaries_are_canonical_and_material_after_rebind`.
- Retirement: remove this scar only when typed evidence ingress makes numeric aliases, compatibility swaps, and state-only summaries unrepresentable before semantic checks.

## WB-027 — Raw acceptance JSON and boolean-like primitives hid unsafe evidence

- Owner: `acceptance/strict_json.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: standard JSON decoding kept the last duplicate key, while Python equality admits booleans as integers and boolean-like authority values.
- Recurrence/limit: Raw duplicate JSON and exact-type mutations cover result, kickoff, source, self-improvement and upgrade ingress before equality.
  - `acceptance/tests/test_oracle.py::OracleTests.test_cli_rejects_duplicate_unsafe_authority_from_file_and_stdin`.
  - `acceptance/tests/test_oracle.py::OracleTests.test_rejects_boolean_schema_version`.
  - `acceptance/tests/test_oracle.py::OracleTests.test_rejects_numeric_authority_flags`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_rejects_duplicate_verdict_before_safe_value`.
  - `acceptance/tests/test_self_improvement_oracle.py::SelfImprovementOracleTests.test_rejects_duplicate_or_boolean_like_request_authority_and_handoff_schema`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_rejects_duplicate_json_authority_before_safe_value`.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_rejects_boolean_like_schema_and_authority_values_after_rebind`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_duplicate_implementation_authority_before_safe_value`.
- Retirement: remove this scar only when the accepted evidence format makes duplicate keys and boolean-like substitutes unrepresentable before these bounded readers run.

## WB-026 — Fixture oracles accepted semantic type and placement substitutes

- Owner: `acceptance/source_comprehension_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: equality admitted Python's boolean-as-integer value; regex searched unmasked file text and aggregated comments file-wide; text-block closure ignored escaped triple quotes or overlapping candidates; the declaration gap interpreted literal parentheses as syntax; orientation was searched anywhere before the type; addendum text lacked canonical-text validation.
- Recurrence/limit: Exact schema and adjacency, comment/string masking, text-block closure and declaration-local rationale cases reach the observed substitutes.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_rejects_boolean_schema_version_and_displaced_orientation`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_ignores_decoy_type_tokens_in_comments_and_annotation_strings`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_allows_flat_annotation_string_char_and_text_block_arguments`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_accepts_overlapping_escaped_text_block_closer`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_rejects_escaped_text_block_decoy_in_valid_java_source`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_requires_local_rationale_in_the_declaration_comment`.
- Retirement: remove this scar only when typed fixture schemas make those substitutes unrepresentable and retain the same declaration-adjacency boundary.

## WB-025 — Release proof polluted candidate or example workspaces

- Owner: `acceptance/prepare.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Historical cause: inventory commands omitted `-B`, and the published prepare sequence/test wrote repository-local output without the current disposable-output boundary.
- Recurrence/limit: The current command-contract check asserts `python3 -B` prepare/check commands and repository-local `.acceptance-work/` output. The release contract limits those writes to disposable scratch children outside selected release paths. Separately, the prepare test exercises an external system-temp child and checks the repository snapshot is unchanged. These checks do not prove every subprocess is side-effect-free.
  - `tests/test_warmboot.py::WarmbootCliTests.test_release_evidence_uses_external_no_bytecode_workspaces`.
  - `acceptance/tests/test_prepare.py::PrepareTests.test_system_temp_child_is_allowed_without_repository_residue`.
- Retirement: remove this scar only when the release harness structurally isolates all test/prepare writes from the candidate checkout without command discipline and examples inherit a universal no-bytecode runner.

## WB-024 — State-only release-note summaries passed release-note/upgrade validation

- Owner: `acceptance/upgrade_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the oracle required only a non-empty summary, so state and identity could substitute for what changed.
- Recurrence/limit: Rebinding the mutated note digest keeps state-only rejection independent of byte integrity.
  - `acceptance/tests/test_upgrade_oracle.py::UpgradeOracleTests.test_rejects_state_only_release_note_summary_after_digest_rebind`.
- Retirement: remove this scar only when typed release-note semantics make a state-only summary unrepresentable.

## WB-023 — Historical receipts reactivated commands, authority and unproved closure

- Owner: `docs/release.md` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: programme closure (closing an earlier planned batch of maintenance work), command-inventory single-homing, provider-state migration and status-only checkpoint evidence were updated independently. The existing exact disposition test pinned one disposition row's prose but not the behavior across its current authority homes.
- Recurrence/limit: The surviving case checks absent root release manifest, unreleased state and current release/backlog routing. Earlier provider-authority and unsupported-checkpoint recurrence is UNPROVED; this narrower case cannot justify its retirement.
  - `tests/test_warmboot.py::WarmbootCliTests.test_maintenance_authorities_point_to_current_release_state`.
- Retirement: fold this pin into a lower-tax typed active-task/authority contract only when that contract still rejects closed-programme permission, historical provider authority and unsupported checkpoint freshness without suppressing exact task/evidence receipts.

## WB-022 — Plans, tests and ADRs passed while production source stayed opaque

- Owner: `acceptance/source_comprehension_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: prior Warmboot required “consequential rationale” as an aspiration but did not require a target-fit source rule/owner, changed-file definition of done, complete changed-source reviewer read, or release-blocking finding. Review could sample or accept green tests and remote documentation.
- Recurrence/limit: Source fixtures and installed-contract checks reject green tests/unlinked ADRs as substitutes for local rationale, target ownership and complete independent source review.
  - `tests/test_warmboot.py::WarmbootCliTests.test_source_comprehension_rule_projects_and_blocks_green_test_substitution`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_rejects_tests_and_unlinked_adr_as_source_substitutes`.
  - `acceptance/tests/test_source_comprehension_oracle.py::SourceComprehensionOracleTests.test_mutations_remove_load_bearing_source_and_review_evidence`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_missing_target_fit_source_comprehension_contract`.
- Retirement: fold/delete the special fixture when a lower-tax target-fit mechanism still proves local-contract, complete changed-set and independent-review recurrence without count/score theatre.

## WB-021 — Completed lanes collapsed into root implementation and self-review

- Owner: `acceptance/self_improvement_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the prior core made one agent the general default, routes described initial topology but not persistence, and task/handoff samples had no scope-revision or authorship surface. Outer-coordinator addenda without explicit replanning compounded the toolkit gap.
- Recurrence/limit: Installed role checks and addendum cases cover coordinator exclusion, affected-only renewal, unaffected receipt preservation and non-author review.
  - `acceptance/tests/test_self_improvement_oracle.py::SelfImprovementOracleTests.test_directly_rejects_coordinator_as_exploration_owner`.
  - `acceptance/tests/test_self_improvement_oracle.py::SelfImprovementOracleTests.test_scope_change_renews_only_affected_lane_and_preserves_receipt`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_installed_topology_contract_preserves_proportional_role_separation`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_review_contract_converges_on_unchanged_non_author_scope`.
  - `acceptance/tests/test_self_improvement_oracle.py::SelfImprovementOracleTests.test_scope_change_rejects_renewing_unaffected_lane`.
  - `acceptance/tests/test_self_improvement_oracle.py::SelfImprovementOracleTests.test_scope_change_rejects_coordinator_rotation_or_author_review`.
- Retirement: fold these cases into a lower-tax typed task/topology contract only when it structurally preserves scope-impact, ownership/authorship and review-convergence semantics and still projects to installed consumers.

## WB-020 — Remediation compression dropped the external-effects invariant from the installed core

- Owner: `WARMBOOT.md` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: word-budget compression treated the sentence as a duplicate of `BOOTSTRAP.md` §6/§7 — which are not installed. The audits' own compression-drops-unique-facts class, replayed by the auditor.
- Recurrence/limit: No executable invariant-presence pin exists. A material installed-contract rewrite requires an independent challenger to compare installed invariants. Budget/payload equality does not assert separate external-effect authorization; that challenger proof is UNPROVED here.
- Retirement: when an executable invariant-presence pin or a typed contract format makes a silently dropped invariant detectable without the challenger.

## WB-019 — Takeover-gate anchoring over-narrowed away the named-but-absent case

- Owner: `WARMBOOT.md` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: strengthening the gate against seizure substituted a stricter predicate without re-deriving the original case the rule existed for.
- Recurrence/limit: No current executable behavior pin exists. The ownership gate retains the named-but-demonstrably-absent branch; changes require fresh refusal and close-out cold probes. Those probes were not rerun: current behavior is UNPROVED.
- Retirement: when the gate gains an executable behavioral test or a typed form.

## WB-018 — Source-ID parsing erased duplicate card declarations

- Owner: `acceptance/capability_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: `_source_ids_from_card()` searched one broad text slice and immediately built a set from every backtick match, erasing order and multiplicity before validation.
- Recurrence/limit: Raw card mutations retain matching inventory digests and exercise duplicate fields/values, missing fields and noncanonical IDs before set aggregation.
  - `acceptance/tests/test_capability_rights_lineage.py::NormalizedLineageTests.test_rejects_missing_dangling_duplicate_and_noncanonical_card_sources`.
- Retirement: only when card/source ownership moves to a typed format whose parser structurally preserves field and list multiplicity before validation, making these text-boundary cases redundant.

## WB-017 — JSON duplicate keys bypassed repository authority validation

- Owner: `acceptance/capability_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: `_load_json()` used the default `json.loads()` object construction, which normalizes duplicate pairs into one dictionary entry before schema or policy code can observe them.
- Recurrence/limit: Raw-text duplicates reach recursive rejection before dictionary/schema equality can discard them.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_repository_json_inputs_reject_same_and_different_duplicate_keys_recursively`.
- Retirement: only when all capability JSON inputs move behind a lower-level parser or typed decoder that makes duplicate-key acceptance structurally impossible and the common hook no longer adds coverage.

## WB-016 — A nominal worker-history read rewrote Git index stat-cache bytes

- Owner: `routes/context.md` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the old rule made the coordinator a history-output relay and treated read-looking Git porcelain as non-mutating by name. The candidate initially needed one extra attestation exchange because the task did not pre-supply the exact repository/ref/ancestry/pathspec/command boundary.
- Recurrence/limit: The installed-contract test checks bounded attestation and command exclusions. Hard byte-preservation claims still require a disposable exact-environment before/after canary.
  - `tests/test_warmboot.py::WarmbootCliTests.test_bounded_worker_git_history_contract_is_consistent_and_installed`.
- Retirement: when Git or a provider-neutral inspection mechanism proves an equally bounded, lower-tax history path that cannot mutate any relevant repository byte, including the index stat cache, across the supported environments.

## WB-015 — Cold bootstrap could omit the human workspace while helper owned a generic shell

- Owner: `BOOTSTRAP.md` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: workspace creation was described as an optional role/integration preference and simultaneously implemented as an exact helper-owned byte. No single authority required a target-owned adapted workspace as bootstrap completion.
- Recurrence/limit: Helper preservation/exclusion and native-command parity checks cover target workspace ownership. A context-clean bootstrap must separately discover the usable workspace or accepted replacement.
  - `tests/test_warmboot.py::WarmbootCliTests.test_workspace_seed_is_inert_and_outside_managed_payload`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_target_named_workspace_is_unmanaged_and_preserved`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_differently_named_workspace_survives_preview_apply_rerun_and_check`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_multiple_invalid_and_symlink_workspaces_are_unmanaged_and_preserved`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_workspace_edit_after_apply_does_not_fail_managed_check`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_repository_workspace_is_target_owned_and_matches_testing_authority`.
- Retirement: only when a provider-neutral bootstrap mechanism independently makes omission impossible and proves an equally usable human entry without a persistent workspace-specific contract/test burden.

## WB-014 — Fixed kickoff staffing imposed avoidable orchestration and artifact tax

- Owner: `acceptance/kickoff_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: owner independence was encoded as exactly one owner per concern plus a seventh challenger instead of as risk-proportional independent authorship and complete concern attribution.
- Recurrence/limit: Positive proportional cases and negative independence/merge/rationale/cross-check mutations preserve structural coverage. They do not measure live staffing cost.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_accepts_proportional_research_owners_with_high_risk_split`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_accepts_lower_risk_merge_with_rationale_and_challenger_cross_checks`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_high_risk_architecture_delivery_merge`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_lower_risk_merge_without_concrete_rationale`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_lower_risk_merge_missing_named_cross_check`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_lower_risk_merge_when_challenge_omits_assigned_cross_checks`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_one_research_owner_for_all_six_concerns`.
  - `acceptance/tests/test_kickoff_oracle.py::KickoffOracleTests.test_rejects_challenger_who_authored_a_research_concern`.
  - `acceptance/tests/test_self_improvement_oracle.py::SelfImprovementOracleTests.test_directly_rejects_high_risk_architecture_delivery_owner_merge`.
- Retirement: when a provider-neutral mechanism proves concern coverage, useful independence and challenger separation without owner-count rules, and paired cold evidence shows equal or better safety/recoverability with lower recurring tax.

## WB-013 — Routine provider handoff was misclassified as coordinator rotation

- Owner: `routes/handoff.md` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the handoff route/template combined routine freshness with authority transfer, while the rotation route lacked a strong provider/session-change anti-trigger.
- Recurrence/limit: The source canary distinguishes routine state transfer from explicit singleton replacement.
  - `tests/test_warmboot.py::WarmbootCliTests.test_routine_handoff_and_exceptional_rotation_are_semantically_separate`.
- Retirement: when the handoff and rotation roles become structurally distinct types whose trigger and fields cannot be confused, replace the text canary with that typed boundary.

## WB-012 — Cold audit was repeatedly misclassified as bootstrap

- Owner: `docs/acceptance.md` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the exceptional audit prompt named the capability library but did not name its exceptional route soon enough; adding that toolkit-only route to the installed core would create a broken consumer path and change the frozen default payload.
- Recurrence/limit: The early audit route, the fixed managed path set of the capability-free default payload and the absence of any `acceptance/` link in the installed core are source checks. Cold route discovery remains a separate live gate.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_cold_prompt_routes_before_bootstrap_misclassification`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_real_root_default_payload_has_only_managed_paths_and_excludes_capabilities`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_installed_status_vocabulary_is_defined_in_the_installed_files`.
  - `tests/test_warmboot.py::WarmbootCliTests.test_installed_core_stays_within_budget_and_carries_no_maintainer_residue`.
- Retirement: remove the sentence only if a future installed/provider-neutral route can reach optional toolkit acceptance without a broken consumer path, core bloat or bootstrap misclassification, and cold evidence proves that replacement.

## WB-011 — Acceptance instructions leaked prior outsider results

- Owner: `acceptance/capability-outsider.md` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: stable execution protocol and mutable run history shared one document, so an outsider (a context-clean agent auditing the capability library) could read earlier results.
- Recurrence/limit: The pin rejects the observed history markers in required routes. It does not exclude every paraphrase; independent cold review still owns input isolation.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_cold_outsider_route_rejects_observed_history_markers`.
- Retirement: remove the text pin when protocol and execution results have separate structurally enforced authorities that cannot be routed together; keep the cold behavioral review while it remains decision-useful.

## WB-010 — Selective bootstrap conflicted with the all-card audit

- Owner: `BOOTSTRAP.md` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: ordinary selective adoption and exhaustive acceptance coverage shared the same vocabulary without an explicit mode boundary.
- Recurrence/limit: Selection structure distinguishes empty/single and exhaustive audit cases without auto-selecting related cards. Cold discovery still requires a context-clean outsider.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_accepts_empty_single_and_outsider_selections_without_auto_selecting_related`.
- Retirement: only when one unambiguous interface structurally separates ordinary selection from exhaustive audit without extra prose.

## WB-009 — Cold target test mutated bytes under read/process-only authority

- Owner: `acceptance/oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: the acceptance command treated a test runner as read-only and did not account for Python's default bytecode-cache writes.
- Recurrence/limit: A passing native command concealed generated writes. Compare complete target snapshots and reject bytecode paths before and after execution; this does not prove every runtime is read-only.
  - `acceptance/tests/test_oracle.py::OracleTests.test_read_only_native_command_passes_without_mutating_target`.
- Retirement: only when the selected native runtime is proved not to write generated state or the audit explicitly grants one holder and destination for that state.

## WB-008 — Repository JSON could escape through a parent symlink

- Owner: `acceptance/capability_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: JSON loading checked the leaf file and semantic contents but did not verify containment and every path component before following the parent chain.
- Recurrence/limit: Valid bytes through a symlink still lacked path authority. Reject symlinked parents and escaped resolution before semantic validation.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_repository_json_inputs_reject_symlinked_parent_directories`.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_repository_json_inputs_reject_escaped_resolution_and_outside_paths`.
- Retirement: only when one lower-level no-follow/attested-root loader makes parent symlink traversal and outside resolution structurally impossible for every authority.

## WB-006 — Parsed rights fields created false source/publication proof

- Owner: `acceptance/capability_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: structural schema validation was mistaken for semantic policy enforcement; source rights were outside the oracle's compared invariant set.
- Recurrence/limit: Synthetic catalogue mutations check inherited rights and payload exclusion; they do not reproduce real licence evidence.
  - `acceptance/tests/test_capability_oracle.py::CapabilityOracleTests.test_rejects_source_catalog_rights_payload_and_invalid_identity`.
- Retirement: keep the synthetic rights checks until one authority structurally enforces inheritance and exclusions.

## WB-004 — Restricted source rights were inferred from local ownership

- Owner: `acceptance/capability_oracle.py` maintainer, with its acceptance owner responsible for the recurrence checks below.
- Cause: source admission inferred rights from local checkout/user ownership and file relevance instead of resolving the committed repository licence and propagating its rights classification to every stored/cited entry.
- Recurrence/limit: A synthetic restricted catalogue checks that restricted rights are inherited and cannot be upgraded; it does not authenticate a real licence or permission.
  - `acceptance/tests/test_capability_rights_lineage.py::NormalizedLineageTests.test_synthetic_restrictions_inherit_and_cannot_upgrade`.
- Retirement: keep the synthetic inheritance checks until the format makes rights upgrades impossible.
