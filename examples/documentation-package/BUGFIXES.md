# Resolved defects — example only

This is the causal defect ledger, not an issue tracker. The entry below is an
illustrative lifecycle record for this teaching project, not production history.

## 2026-07-31 — Normalized keys were initially described as display labels

1. **Symptom:** the first wording implied callers could replace the original
   label with the normalized result. That would lose typography because NFKC and
   case folding are intentionally destructive.

   **Cause:** one output was being asked to serve two owners: human presentation
   and equality comparison.

   **Fix:** define `normalize_label` as a comparison-key operation only, keep
   display text outside this package, and state the boundary in the README,
   function docstring, ADR, and CLI help.

   **Owner and red-before signal:** the public comparison-contract owner. Challenge
   finding `F1` captured ambiguous “normalized label” wording before correction.

   **Regression evidence:** ordinary behavior tests cover compatibility normalization
   and Unicode case folding (`Straße` → `strasse`). Documentation review checks that
   README, API docstring, ADR, invariants, and CLI help describe a destructive
   comparison key rather than preserved display text.

   **Source-pin admission:** `OMIT`. Behavior tests observe the transformation and
   review observes the wording boundary, so no invisible source/wiring recurrence
   exists for a permanent text/AST pin. Add one only after a reproduced recurrence
   proves these checks insufficient.

   **Deletion condition:** remove this entry only if a living successor absorbs
   the warning and the public API is replaced by separate display and comparison
   types. Otherwise it remains useful causal history.

   **Limits:** no locale-specific collation or transliteration is claimed.
